### Overview

We will prepare a multi-band composite containing spectral bands, spectral indices, elevation and slope. When the composite is used to extract training features for machine learning models, each band adds a different context for the model.


### Setup and Data Download

The following blocks of code will install the required packages and set up the computing environment.


```python
%%capture
if 'google.colab' in str(get_ipython()):
    !pip install pystac-client odc-stac rioxarray dask['distributed'] botocore \
      jupyter-server-proxy planetary_computer xarray-spatial
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
import planetary_computer as pc
from xrspatial import slope
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

Read the file containing the city boundary from your Google Drive saved in the previous notebook.

Run the following cell to authenticate and mount the Google Drive.



```python
if 'google.colab' in str(get_ipython()):
  from google.colab import drive
  drive.mount('/content/drive')
```


```python
if 'google.colab' in str(get_ipython()):
  drive_folder_root = 'MyDrive'
  drive_data_folder = 'python-remote-sensing'
  drive_folder_path = os.path.join(
        '/content/drive', drive_folder_root, drive_data_folder)
  data_folder = drive_folder_path
else:
  # Look for the file in local data folder
  data_folder = data_folder

aoi_filename = 'aoi.geojson'
aoi_filepath = os.path.join(data_folder, aoi_filename)
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
    chunks={},           # use Dask
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
if 'google.colab' in str(get_ipython()):
  output_folder_path = drive_folder_path
  # Check if Google Drive is mounted
  if not os.path.exists('/content/drive'):
      print("Google Drive is not mounted. Please run the cell above to mount your drive.")
  else:
      if not os.path.exists(output_folder_path):
          os.makedirs(output_folder_path)
else:
  # Use the local output folder
  output_folder_path = output_folder
```

Ww use the rioxarray accessor to save the results as a Cloud-Optimized GeoTIFF.


```python
output_file = f'multiband_composite.tif'
local_output_path = os.path.join(output_folder_path, output_file)
composite_clipped.rio.to_raster(local_output_path, driver='COG')
print(f'Wrote {local_output_path}')
```

Optionally, we can also the output to Google Cloud Storage (GCS) bucket.


```python
# Specify your project ID and Bucket name
project_id = 'python-363014'
bucket_name = 'spatialthoughts-public-data'
sub_folder = 'python-remote-sensing'
```


```python
if 'google.colab' in str(get_ipython()):
  from google.colab import auth
  from google.cloud import storage

  auth.authenticate_user()
  client = storage.Client(project=project_id)
  bucket = client.get_bucket(bucket_name)

  print(f'Google Cloud Storage client initialized for project: {project_id}')
  print(f'Bucket {bucket_name} selected.')
  gcs_blob_path = f'{sub_folder}/{output_file}'
  blob = bucket.blob(gcs_blob_path)

  print(f'Uploading {local_output_path} to gs://{bucket.name}/{gcs_blob_path}')
  blob.upload_from_filename(local_output_path)
```
