### Overview

This notebook demonstrates how the same processing can be done in different computing environments. We will run the same notebook on different computing platforms.

1. Run on your own local machine.
2. Run on a Google Cloud Runtime with Google Colab
3. Run on a Cloud VM with Coiled

### Overview of the Task

We will query a STAC catalog for Sentinel-2 imagery, apply pixel-level cloud masking using the Scene Classification Layer (SCL) band, and create a cloud-free median composite image using distributed processing.

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
      jupyter-server-proxy pyngrok
```

Import all required libraries. Make sure to import everything at the beginning as certain XArray extensions are activated on import and register certain accessors, like `.rio` and `.odc` for XArray objects.


```python
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import os
import pystac_client
import rioxarray as rxr
import xarray as xr
from dask.distributed import Client
from odc.stac import configure_s3_access, load
```

Setup a local Dask cluster. This distributes the computation across multiple workers on your computer.


```python
client = Client()  # set up local cluster on the machine
client
```

If you are running this notebook in Colab, you will need to create and use a proxy URL to see the dashboard running on the local server.

Colab Enterprise restricts the reverse proxy. So we need to use a service like [ngrok](https://ngrok.com/) to create a secure tunnel from the localhost and get a public URL. You will need to sign-up for a free account and get an auth token. 

> You can skip this step without affecting rest of the notebook. You will not be able to see the Dask dashboad.



```python
if environment == 'colab':
    from google.colab import output
    port_to_expose = 8787  # This is the default port for Dask dashboard
    print(output.eval_js(f'google.colab.kernel.proxyPort({port_to_expose})'))
if environment == 'colab_enterprise':
    YOUR_AUTH_TOKEN = '' # get from ngrok.com
    if YOUR_AUTH_TOKEN:
        from pyngrok import ngrok
        from pyngrok import conf

        ngrok.set_auth_token(YOUR_AUTH_TOKEN)  

        # Expose the Dask dashboard port
        port_to_expose = 8787  # This is the default port for Dask dashboard

        print(ngrok.connect(port_to_expose))
    else:
        print('Please set your ngrok auth token to expose the Dask dashboard in Colab Enterprise.')
```

### Load Area of Interest

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

### Search and Load Sentinel-2 Scenes

Let's use the Element84 search endpoint to look for items from the `sentinel-2-c1-l2a` collection on AWS. We search for imagery collected within the date range and intersecting the AOI geometry.

We specify an additional filter using `eo:cloud_cover` to select only scenes with less than 30% overall cloud cover. This pre-filters at the scene level, but we will also apply a pixel-level cloud mask using the SCL band.


```python
catalog = pystac_client.Client.open(
    'https://earth-search.aws.element84.com/v1')

# Configure settings for reading from Earth Search STAC
configure_s3_access(
    aws_unsigned=True,
)

# Search for images for the year
year = 2024
time_range = f'{year}'

# Optionally, we can specify a range of months
# start_month = 4
# end_month = 6
# time_range = f'{year}-{start_month:02d}/{year}-{end_month:02d}'

filters = {
    'eo:cloud_cover': {'lt': 30},
    # Uncomment below if your AOI spans multiple MGRS tiles and
    # you want to limit results to a single grid square
    # 'mgrs:grid_square': {'eq': 'GQ'},
}

search = catalog.search(
    collections=['sentinel-2-c1-l2a'],
    intersects=geometry,
    datetime=time_range,
    query=filters,
)
items = search.item_collection()
len(items)
```

Visualize the resulting image footprints. When we process the data for our AOI, we will only stream the required pixels instead of downloading entire scenes.


```python
items_gdf = gpd.GeoDataFrame.from_features(items.to_dict(), crs='EPSG:4326')

fig, ax = plt.subplots(1, 1)
fig.set_size_inches(5, 5)
items_gdf.plot(
    ax=ax,
    facecolor='none',
    edgecolor='black',
    alpha=0.5)

aoi_gdf.plot(
    ax=ax,
    facecolor='blue',
    alpha=0.5
)
ax.set_axis_off()
ax.set_title('STAC Query Results')
plt.show()
```

Load the matching images as a XArray Dataset. We include the `scl` (Scene Classification Layer) band which we will use to apply the pixel-level cloud mask.


```python
ds = load(
    items,
    bands=['red', 'green', 'blue', 'nir', 'scl'],
    resolution=10,
    crs='utm',
    bbox=geometry.bounds,
    chunks={'x': 1024, 'y': 1024},  # Explicitly define chunk sizes
    groupby='solar_day',
)
ds
```

### Preprocess Imagery

The Sentinel-2 scenes come with a NoData value of 0. We set the correct NoData value before further processing.


```python
# Mask nodata values
ds = ds.where(ds != 0)
```

Apply scale and offset to convert raw digital numbers to surface reflectance values. The `scl` band is a classification layer and must not have scale/offset applied.


```python
# Apply scale/offset to spectral bands only (exclude scl)
scale = 0.0001
offset = -0.1
data_bands = [band for band in ds.data_vars if band != 'scl']
for band in data_bands:
    ds[band] = ds[band] * scale + offset
```

Apply the pixel-level cloud mask using the SCL band. The SCL classes we mask are: 3 (cloud shadow), 8 (cloud medium probability), 9 (cloud high probability), and 10 (cirrus).


```python
cloud_mask = ds.scl.isin([3, 8, 9, 10])
ds = ds[data_bands].where(~cloud_mask)
ds
```

### Create a Cloud-Free Median Composite

A very powerful feature of XArray is the ability to easily aggregate data across dimensions. We apply the `.median()` aggregation across the time dimension. Since cloud-masked pixels are `NaN`, the median is computed only from valid (cloud-free) pixels.


```python
median_composite = ds.median(dim='time')
median_composite
```

Select the RGB bands for visualization and export.


```python
rgb_composite = median_composite[['red', 'green', 'blue']]
rgb_composite
```

So far all the operations have created a computation graph. To run this computation using the local Dask cluster, we must call `.compute()`.


```python
%%time
rgb_composite = rgb_composite.compute()
```

### Visualize the Results

The composite is created from all the pixels within the bounding box of the geometry. We can use `rioxarray` to clip the image to the AOI boundary to remove pixels outside the polygon.

To visualize our Dataset, we first convert it to a DataArray using the `to_array()` method. All the variables will be converted to a new dimension. Since our variables are image bands, we give the new dimension the name `band`.


```python
rgb_composite_da = rgb_composite.to_array('band')
image_crs = rgb_composite_da.rio.crs
aoi_gdf_reprojected = aoi_gdf.to_crs(image_crs)
rgb_composite_clipped = rgb_composite_da.rio.clip(aoi_gdf_reprojected.geometry)
rgb_composite_clipped
```

For visualizing, we resample to a lower resolution preview.


```python
preview = rgb_composite_clipped.rio.reproject(
    rgb_composite_clipped.rio.crs, resolution=100
)
```


```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(5, 5)
preview.sel(band=['red', 'green', 'blue']).plot.imshow(
    ax=ax,
    robust=True)
ax.set_title('RGB Visualization')
ax.set_axis_off()
ax.set_aspect('equal')
plt.show()
```

### Save the Output

We use the `rio` accessor to save the results as a Cloud-Optimized GeoTIFF. The raw composite preserves the pixel reflectance values and is suitable for downstream scientific analysis.


```python
output_file = f'cloudfree_composite_{time_range}.tif'
output_path = os.path.join(output_folder, output_file)
rgb_composite_clipped.rio.to_raster(output_path, driver='COG')
print(f'Wrote {output_path}')
```

Close the Dask client. This prevents multiple clients being instantiated when running different notebooks on the same machine.


```python
client.shutdown()
```
