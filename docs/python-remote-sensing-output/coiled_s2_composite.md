## Overview

This notebook is an example of a fairly large computation involving hundrescenes over a large city. Using STAC, XArray and Dask - we can now achieve this  by running the computation via a notebook on a cloud-machine. We use [Coiled](https://coiled.io/) to seamlessly configure a machine and process the data.

## Overview of the Task

We will query a STAC catalog for Sentinel-2 imagery over the city of Bengaluru, India, apply a cloud-mask and create a median composite image using distributed processing.



```python
from odc.stac import stac_load
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import pystac_client
import rioxarray as rxr
import xarray as xr
```


```python
data_folder = 'data'
output_folder = 'output'

if not os.path.exists(data_folder):
    os.mkdir(data_folder)
if not os.path.exists(output_folder):
    os.mkdir(output_folder)
```


```python
def download(url):
    filename = os.path.join(data_folder, os.path.basename(url))
    if not os.path.exists(filename):
        from urllib.request import urlretrieve
        local, _ = urlretrieve(url, filename)
        print('Downloaded ' + local)

data_url = 'https://storage.googleapis.com/spatialthoughts-public-data/'
filename = 'bangalore.geojson'

download(data_url + filename)
```

Setup a local Dask cluster. This distributes the computation across multiple workers on your computer.


```python
from dask.distributed import Client
client = Client()  # set up local cluster on the machine
client
```

## Search and Load Sentinel-2 Scenes

Read the file containing the city boundary.


```python
aoi_file = 'bangalore.geojson'
aoi_filepath = os.path.join(data_folder, aoi_file)
aoi = gpd.read_file(aoi_filepath)
```


```python
geometry = aoi.geometry.union_all()
geometry
```

Let's use Element84 search endpoint to look for items from the `sentinel-2-c1-l2a` collection on AWS. We search for the imagery collected within the date range and intersecting the AOI geometry.

We also specify additonal filters to select scenes based on metadata. The parameter `eo:cloud_cover` contains the overall cloud percentage and we use it to select imagery with < 30% overall cloud cover.

Our region of interest has overlapping scenes from multiple MGRS grid tiles, so we can specify an additional filter using the metadata `mgrs:grid_square` to select tiles only from one of the grids. You will need to update this for your region of interest.


```python
catalog = pystac_client.Client.open(
    'https://earth-search.aws.element84.com/v1')

# Search for images from 2024
year = 2024
time_range = f'{year}'

filters = {
    'eo:cloud_cover': {'lt': 30},
    'mgrs:grid_square': {'eq': 'GQ'}
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

Visualize the resulting image footprints. You can see that our AOI covers only a small part of a single scene. When we process the data for our AOI - we will only stream the required pixels to create the composite instead of downloading entire scenes.


```python
items_df = gpd.GeoDataFrame.from_features(items.to_dict(), crs='EPSG:4326')

fig, ax = plt.subplots(1, 1)
fig.set_size_inches(5,5)
items_df.plot(
    ax=ax,
    facecolor='none',
    edgecolor='black',
    alpha=0.5)

aoi.plot(
    ax=ax,
    facecolor='blue',
    alpha=0.5
)
ax.set_axis_off()
ax.set_title('STAC Query Results')
plt.show()
```

Load the matching images as a XArray Dataset.


```python
ds = stac_load(
    items,
    bands=['red', 'green', 'blue', 'scl'],
    resolution=10,
    bbox=geometry.bounds,
    chunks={},  # <-- use Dask
    groupby='solar_day',
)
ds
```

The Sentinel-2 scenes come with NoData value of 0. So we set the correct NoData value before further processing.


```python
# Mask nodata values
ds = ds.where(ds != 0)
```

Apply scale and offset to all spectral bands


```python
# Apply scale/offset
scale = 0.0001
offset = -0.1
# Select spectral bands (all except 'scl')
data_bands = [band for band in ds.data_vars if band != 'scl']
for band in data_bands:
  ds[band] = ds[band] * scale + offset
```

Apply the cloud mask


```python
ds = ds[data_bands].where(~ds.scl.isin([3,8,9,10]))
ds
```

Convert the Dataset it to a DataArray using the `to_array()` method. All the variables will be converted to a new dimension. Since our variables are image bands, we give the name of the new dimesion as `band`.


```python
da = ds.to_array('band')
da
```

## Create a Median Composite

A very-powerful feature of XArray is the ability to easily aggregate data across dimensions - making it ideal for many remote sensing analysis. Let’s create a median composite from all the individual images.

We apply the `.median()` aggregation across the time dimension.


```python
rgb_composite = da \
  .sel(band=['red', 'green', 'blue']) \
  .median(dim='time')
rgb_composite
```

So far all the operations that we have created a computation graph. To run this computation using the local Dask cluster, we must call `.compute()`.


```python
%%time
rgb_composite = rgb_composite.compute()
```

## Visualizing and Exporting the Results

The composite is creating from all the pixels within the bounding box of the geometry. We can use `rioxarray` to clip the image to the city boundary to remove pixels outside the polygon.


```python
image_crs = rgb_composite.rio.crs
aoi_reprojected = aoi.to_crs(image_crs)
rgb_composite_clipped = rgb_composite.rio.clip(aoi_reprojected.geometry)
```

Plot the results.


```python
preview = rgb_composite_clipped.rio.reproject(
    rgb_composite_clipped.rio.crs, resolution=100
)

fig, ax = plt.subplots(1, 1)
fig.set_size_inches(5,5)
preview.sel(band=['red', 'green', 'blue']).plot.imshow(
    ax=ax,
    robust=True)
ax.set_title(f'Sentinel-2 Composite {year}')
ax.set_axis_off()
ax.set_aspect('equal')
plt.show()
```

We finally save the results as a local Cloud-Optimized GeoTIFF file.


```python
output_file = f'composite_{time_range}.tif'
output_path = os.path.join(output_folder, output_file)
rgb_composite_clipped.rio.to_raster(output_path, driver='COG')
print(f'Wrote {output_file}')
```
