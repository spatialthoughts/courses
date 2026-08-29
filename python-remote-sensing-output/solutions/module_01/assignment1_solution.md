## Assignment 1 (Solution)

### Setup


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


```python
%%capture
if environment in ['colab', 'colab_enterprise']:
    !pip install pystac-client odc-stac rioxarray dask['distributed'] \
        jupyter-server-proxy planetary_computer
```


```python
import dask
import matplotlib.pyplot as plt
import numpy as np
import os
import planetary_computer as pc
import pystac_client
import rioxarray as rxr
import xarray as xr
from odc.stac import load
import geopandas as gpd
```


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

#### Load City Boundary

Read the file containing the city boundary.


```python
aoi_filepath = os.path.join(data_folder, 'aoi.geojson')

if not os.path.exists(aoi_filepath):
    print(f'AOI file not found at {aoi_filepath}. Using default AOI.')
    aoi_filepath = ('https://storage.googleapis.com/spatialthoughts-public-data'
                    '/python-remote-sensing/aoi.geojson')
```

Read the GeoJSON.


```python
aoi_gdf = gpd.read_file(aoi_filepath)
```

Extract the geometry.


```python
geometry = aoi_gdf.geometry.union_all()
geometry
```

#### Get Satellite Imagery using STAC API

We define a location and time of interest to get some satellite imagery.

Let's use [Planetary Computer STAC API](https://planetarycomputer.microsoft.com/docs/quickstarts/reading-stac/) search endpoint to look for items from the sentinel-2-l2a collection on Azure Blob Storage.


```python
catalog = pystac_client.Client.open(
    'https://planetarycomputer.microsoft.com/api/stac/v1')

year = 2000

search = catalog.search(
    collections=['landsat-c2-l2'],
    intersects=geometry,
    datetime=f'{year}',
    query={
        'eo:cloud_cover': {'lt': 30},
        'platform': {'in': ['landsat-5', 'landsat-7', 'landsat-8', 'landsat-9']},
        
    })
items = search.item_collection()
items
```

Load the matching images as a XArray Dataset. Accessing data from Planetary Computer is free but requires getting a Shared Access Signature (SAS) token and sign the URLs. The `planetary_computer` Python package provides a simple mechanism for signing the URLs using `sign()` function.


```python
# Load to XArray
ds = load(
    items,
    bands=['red', 'green', 'blue'],
    bbox=geometry.bounds, # <-- load data only for the bbox
    resolution=30,
    crs='utm',
    chunks={'x': 1024, 'y': 1024},  # Explicitly define chunk sizes
    patch_url=pc.sign,
    groupby='solar_day',
    preserve_original_order=True
)
ds
```

#### Processing Data

Apply scale and offset to all spectral bands


```python
for band in ['red', 'green', 'blue']:
  print(items[0].assets[band].extra_fields['raster:bands'][0])
```


```python
# Apply scale/offset
scale = 2.75e-05
offset = -0.2
# Select spectral bands (all except 'scl')
data_bands = [band for band in ds.data_vars if band != 'SCL']
for band in data_bands:
  ds[band] = ds[band] * scale + offset
```

Create a Median Composite


```python
median_composite = ds.median(dim='time')
rgb_composite = median_composite[['red', 'green', 'blue']]
rgb_composite
```


```python
%%time
rgb_composite = rgb_composite.compute()
```

### Visualizing Results


```python
rgb_composite_da = rgb_composite.to_array('band')
image_crs = rgb_composite_da.rio.crs
aoi_gdf_reprojected = aoi_gdf.to_crs(image_crs)
rgb_composite_clipped = rgb_composite_da.rio.clip(aoi_gdf_reprojected.geometry)
rgb_composite_clipped
```


```python
preview = rgb_composite_clipped.rio.reproject(
    rgb_composite_clipped.rio.crs, resolution=100
)

fig, ax = plt.subplots(1, 1)
fig.set_size_inches(5,5)
preview.sel(band=['red', 'green', 'blue']).plot.imshow(
    ax=ax,
    vmin=0, vmax=0.2)
ax.set_title(f'Landsat-8 Composite {year}')
ax.set_axis_off()
ax.set_aspect('equal')
plt.show()
```

### Export the Composite

We use the `rio` accessor to save the results as a Cloud-Optimized GeoTIFF.


```python
output_file = f'landsat_composite_{year}.tif'
output_path = os.path.join(output_folder, output_file)
rgb_composite_clipped.rio.to_raster(output_path, driver='COG')
print(f'Wrote {output_path}')
```
