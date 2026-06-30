### Overview

We will prepare a multi-band composite containing spectral bands, spectral indices, elevation and slope. When the composite is used to extract training features for machine learning models, each band adds a different context for the model.


### Setup

Determine our runtime environment.



```python
import os

if 'COLAB_RELEASE_TAG' in os.environ:
    environment = 'colab'
    if os.environ.get('VERTEX_PRODUCT') == 'COLAB_ENTERPRISE':
        environment = 'colab_enterprise'
else:
    environment = 'local'

# Set to True to use Google Drive for data storage in Colab
use_google_drive = True

# Google Drive is available only in 'colab' environment
if environment == 'colab' and use_google_drive:
    from google.colab import drive
    drive.mount('/content/drive')
    drive_folder_root = 'MyDrive'
    drive_data_folder = 'python-remote-sensing'
    drive_folder_path = os.path.join('/content/drive', drive_folder_root, drive_data_folder)
    data_folder = drive_folder_path
    output_folder = drive_folder_path
else:
    data_folder = 'data'
    output_folder = 'output'

if not os.path.exists(data_folder):
    os.mkdir(data_folder)
if not os.path.exists(output_folder):
    os.mkdir(output_folder)

print(f'Environment: {environment}')
print(f'Data folder: {data_folder}')
print(f'Output folder: {output_folder}')
```

If we are on Google Colab, install the required packages. Local runtimes are expected to have the packages already installed.


```python
%%capture
if environment in ['colab', 'colab_enterprise']:
    !pip install pystac-client odc-stac rioxarray dask['distributed'] botocore \
      jupyter-server-proxy planetary_computer xarray-spatial
```

Import all required libraries. Make sure to import everything at the beginning as certain Xarray extensions are activated on import and registers certain accesors, like `.rio` and `.odc` for Xarray objects.


```python
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import os
import pystac_client
import rioxarray as rxr
import xarray as xr
from odc.stac import configure_s3_access, load
import planetary_computer as pc
from xrspatial import slope
```


```python
year = 2023
```

Setup a local Dask cluster. This distributes the computation across multiple workers on your computer.


```python
from dask.distributed import Client
client = Client()  # set up local cluster on the machine
client
```

If you are running this notebook in Colab, you will need to create and use a proxy URL to see the dashboard running on the local server.


```python
if environment == 'colab':
    from google.colab import output
    port_to_expose = 8787  # This is the default port for Dask dashboard
    print(output.eval_js(f'google.colab.kernel.proxyPort({port_to_expose})'))
```

### Load Area of Interest

Read the file containing the city boundary.


```python
aoi_filepath = os.path.join(data_folder, 'aoi.geojson')

if not os.path.exists(aoi_filepath):
    print(f'AOI file not found at {aoi_filepath}. Using default AOI.')
    aoi_filepath = ('https://storage.googleapis.com/spatialthoughts-public-data'
                    '/python-remote-sensing/aoi.geojson')

aoi_filepath
```

Read the GeoJSON and extract the geometry.


```python
aoi_gdf = gpd.read_file(aoi_filepath)
geometry = aoi_gdf.geometry.union_all()
geometry

```

### Search and Load Sentinel-2 Imagery

We search the Earth Search STAC catalog for Sentinel-2 L2A scenes covering our AOI and load them as a lazy XArray Dataset using Dask.


```python
catalog = pystac_client.Client.open(
    'https://earth-search.aws.element84.com/v1')

configure_s3_access(aws_unsigned=True)

year = 2023

search = catalog.search(
    collections=['sentinel-2-c1-l2a'],
    intersects=geometry,
    datetime=f'{year}',
    query={'eo:cloud_cover': {'lt': 30}},
)
items = search.item_collection()
```

Load the matching scenes as a lazy XArray Dataset.


```python
ds = load(
    items,
    bands=['red', 'green', 'blue', 'nir', 'swir16', 'swir22', 'scl'],
    resolution=10,
    crs='utm',
    bbox=geometry.bounds,
    chunks={'x': 1024, 'y': 1024},  # Explicitly define chunk sizes
    groupby='solar_day',
)
ds
```


```python
# Mask nodata (Sentinel-2 uses 0 as nodata)
ds = ds.where(ds != 0)

# Apply scale and offset to spectral bands
scale = 0.0001
offset = -0.1
data_bands = [b for b in ds.data_vars if b != 'scl']
for band in data_bands:
    ds[band] = ds[band] * scale + offset

# Apply cloud mask using SCL band
# 3=cloud shadow, 8=cloud medium probability, 9=cloud high probability, 10=thin cirrus
cloud_mask = ds.scl.isin([3, 8, 9, 10])
ds = ds[data_bands].where(~cloud_mask)
ds
```

### Create Median Composite

Aggregate all cloud-masked scenes into a single median composite. The median effectively removes any remaining cloud and shadow artifacts that pass the SCL mask.


```python
composite = ds.median(dim='time')
composite
```

### Calculate Spectral Indices

We compute five spectral indices that are useful for mapping urban land cover and water bodies.

- NDVI: `(NIR − Red) / (NIR + Red)`
- NDBI: `(SWIR1 − NIR) / (SWIR1 + NIR)`
- BSI: `((SWIR1 + Red) − (NIR + Blue)) / ((SWIR1 + Red) + (NIR + Blue))`
- MNDWI: `(Green − SWIR1) / (Green + SWIR1)`
- NDWI: `(Green − NIR) / (Green + NIR)`


```python
red    = composite['red']
green  = composite['green']
blue   = composite['blue']
nir    = composite['nir']
swir16 = composite['swir16']

composite['ndvi']  = (nir - red)    / (nir + red)
composite['ndbi']  = (swir16 - nir) / (swir16 + nir)
composite['bsi'] = (
    ((swir16 + red) - (nir + blue)) /
    ((swir16 + red) + (nir + blue))
)
composite['mndwi'] = (green - swir16) / (green + swir16)
composite['ndwi']  = (green - nir)    / (green + nir)

composite
```

### Add Elevation Data

We query Microsoft’s Planetary Computer Data Catalog and load the [ALOS World 3D - 30m](https://planetarycomputer.microsoft.com/dataset/alos-dem#overview) elevation data.




```python
catalog = pystac_client.Client.open(
    'https://planetarycomputer.microsoft.com/api/stac/v1')

search = catalog.search(
    collections=['alos-dem'],
    intersects=geometry,
)
items = search.item_collection()
items
```

We will add the resulting data as a new band to the composite. To ensure the data is aligned with the pixel grid of the composite, we extract the [GeoBox](https://odc-geo.readthedocs.io/en/latest/intro-geobox.html) of the composite and use it to load the items.


```python
geobox = composite.odc.geobox
geobox
```


```python
chunks = dict(zip(ds['red'].dims, ds['red'].data.chunksize))
chunks
```


```python
# Load to XArray
dem_ds = load(
    items,
    geobox=geobox, # <--- Match pixel grid
    chunks=chunks,  # <-- Match dask chunks
    patch_url=pc.sign,
    groupby='solar_day',
    preserve_original_order=True
)
dem_ds

```

We remove the extra `time` dimension to create a 2D DataArray.


```python
elevation_da = dem_ds.data.squeeze()
elevation_da
```

We use [`xrspatial.slope.slope()`](https://xarray-spatial.readthedocs.io/en/latest/reference/_autosummary/xrspatial.slope.slope.html) function to calculate the slope.


```python
slope_da = slope(elevation_da)
slope_da
```

Add the data to the composite.


```python
composite[['elevation', 'slope']] = elevation_da, slope_da
composite
```


```python
print(f'DataSet size: {composite.nbytes/1e6:.2f} MB.')
```

Compute and load the results.


```python
%%time
composite = composite.compute()
```

### Clip and Export the Composite

We first convert it to a DataArray using the `to_array()` method. All the variables will be converted to a new dimension. Since our variables are image bands, we give the name of the new dimesion as band.



```python
composite_da = composite.to_array('band')
composite_da
```

Clip the composite to the AOI polygon.


```python
image_crs = composite_da.rio.crs
aoi_gdf_reproj = aoi_gdf.to_crs(image_crs)
composite_clipped = composite_da.rio.clip(aoi_gdf_reproj.geometry)
composite_clipped
```

We finally save the results as a local Cloud-Optimized GeoTIFF file.


```python
output_folder_path = output_folder

if not os.path.exists(output_folder_path):
    os.makedirs(output_folder_path)
```

Ww use the rioxarray accessor to save the results as a Cloud-Optimized GeoTIFF.


```python
output_file = f'multiband_composite.tif'
local_output_path = os.path.join(output_folder_path, output_file)
composite_clipped.rio.to_raster(local_output_path, driver='COG')
print(f'Wrote {local_output_path}')
```
