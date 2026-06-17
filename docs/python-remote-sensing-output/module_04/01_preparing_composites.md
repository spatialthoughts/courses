### Overview

This notebook builds a cloud-masked Sentinel-2 median composite for Bangalore, India and computes five spectral indices. The output is saved to Google Drive as a multiband Cloud-Optimized GeoTIFF for use in downstream analysis.

**Workflow**

1. Search the Earth Search STAC catalog for Sentinel-2 L2A scenes covering the area of interest
2. Load the scenes as a lazy XArray Dataset using Dask
3. Apply Sentinel-2 preprocessing: nodata mask, scale/offset correction, SCL cloud mask
4. Aggregate all scenes into a single median composite
5. Compute five spectral indices: NDVI, NDBI, BSI, MNDWI, NDWI
6. Save the 11-band composite (6 spectral bands + 5 indices) to Google Drive as `multiband_composite.tif`

### Setup and Data Download

The following blocks of code will install the required packages and set up the computing environment.


```python
%%capture
if 'google.colab' in str(get_ipython()):
    !pip install pystac-client odc-stac rioxarray dask['distributed'] botocore \
      jupyter-server-proxy
```


```python
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import os
import pystac_client
import rioxarray as rxr
import xarray as xr
from odc.stac import configure_s3_access, load
```


```python
data_folder = 'data'
output_folder = 'output'

if not os.path.exists(data_folder):
    os.mkdir(data_folder)
if not os.path.exists(output_folder):
    os.mkdir(output_folder)
```

Setup a local Dask cluster. This distributes the computation across multiple workers on your computer.


```python
from dask.distributed import Client
client = Client()  # set up local cluster on the machine
client
```

If you are running this notebook in Colab, you will need to create and use a proxy URL to see the dashboard running on the local server.


```python
if 'google.colab' in str(get_ipython()):
    from google.colab import output
    port_to_expose = 8787  # This is the default port for Dask dashboard
    print(output.eval_js(f'google.colab.kernel.proxyPort({port_to_expose})'))
```

### Load Area of Interest

We load the boundary of Bangalore, India as our area of interest.


```python
aoi_file_path = ('https://storage.googleapis.com/spatialthoughts-public-data/'
    'bangalore.geojson')
aoi_gdf = gpd.read_file(aoi_file_path)
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
print(f'Found {len(items)} items')
```

Load the matching scenes as a lazy XArray Dataset. We use 20m resolution to keep the dataset size manageable for a city-scale analysis.


```python
ds = load(
    items,
    bands=['red', 'green', 'blue', 'nir', 'swir16', 'swir22', 'scl'],
    resolution=20,
    crs='utm',
    bbox=geometry.bounds,
    chunks={},           # use Dask
    groupby='solar_day',
)
ds
```

### Preprocessing

Apply the standard Sentinel-2 preprocessing steps: mask nodata pixels, apply scale and offset to convert raw values to reflectances, then apply the SCL cloud mask.


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


```python
%%time
composite = composite.compute()
```

Clip the composite to the AOI polygon.


```python
image_crs = composite.rio.crs
aoi_gdf_reproj = aoi_gdf.to_crs(image_crs)
composite = composite.rio.clip(aoi_gdf_reproj.geometry)
composite
```

Visualize the composite as a true-color image.


```python
rgb_da = composite[['red', 'green', 'blue']].to_array('band')
preview = rgb_da.rio.reproject(rgb_da.rio.crs, resolution=100)

fig, ax = plt.subplots(1, 1)
fig.set_size_inches(6, 6)
preview.sel(band=['red', 'green', 'blue']).plot.imshow(
    ax=ax,
    vmin=0, vmax=0.3)
ax.set_title(f'Sentinel-2 Median Composite {year}')
ax.set_axis_off()
ax.set_aspect('equal')
plt.show()
```

### Calculate Spectral Indices

We compute five spectral indices that are useful for mapping urban land cover and water bodies.

| Index | Formula | Bands (Sentinel-2) |
|-------|---------|-------------------|
| NDVI | (NIR − Red) / (NIR + Red) | B8, B4 |
| NDBI | (SWIR1 − NIR) / (SWIR1 + NIR) | B11, B8 |
| BSI | ((SWIR1 + Red) − (NIR + Blue)) / ((SWIR1 + Red) + (NIR + Blue)) | B11, B4, B8, B2 |
| MNDWI | (Green − SWIR1) / (Green + SWIR1) | B3, B11 |
| NDWI | (Green − NIR) / (Green + NIR) | B3, B8 |


```python
red    = composite['red']
green  = composite['green']
blue   = composite['blue']
nir    = composite['nir']
swir16 = composite['swir16']

composite['ndvi']  = (nir - red)    / (nir + red)
composite['ndbi']  = (swir16 - nir) / (swir16 + nir)
composite['bsi']   = ((swir16 + red) - (nir + blue)) / ((swir16 + red) + (nir + blue))
composite['mndwi'] = (green - swir16) / (green + swir16)
composite['ndwi']  = (green - nir)    / (green + nir)

composite
```

### Save to Google Drive

Rather than saving it to the temporary machine where Colab is running, we save the composite to Google Drive so it persists after the session ends and can be used in other notebooks.

Run the following cell to authenticate and mount the Google Drive.


```python
if 'google.colab' in str(get_ipython()):
    from google.colab import drive
    drive.mount('/content/drive')
```


```python
if 'google.colab' in str(get_ipython()):
    drive_folder_root = 'MyDrive'
    output_folder = 'python-remote-sensing'
    output_folder_path = os.path.join(
        '/content/drive', drive_folder_root, output_folder)
    if not os.path.exists('/content/drive'):
        print('Google Drive is not mounted. Please run the cell above.')
    else:
        if not os.path.exists(output_folder_path):
            os.makedirs(output_folder_path)
else:
    output_folder_path = output_folder

band_names = ['red', 'green', 'blue', 'nir', 'swir16', 'swir22',
              'ndvi', 'ndbi', 'bsi', 'mndwi', 'ndwi']
composite_da = composite[band_names].to_array('band')
output_file = 'multiband_composite.tif'
output_path = os.path.join(output_folder_path, output_file)
composite_da.rio.to_raster(output_path, driver='COG')
print(f'Saved {output_path}')
```
