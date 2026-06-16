### Overview

We are now ready to perform a large computation to create a median composite image for a city using XArray and Dask, leveraging STAC and DuckDB for querying cloud-hosted data sources.

### Overview of the Task

We will query the Overture Maps catalog for the boundary for the city of Bengaluru, India, use it to query a STAC catalog for Sentinel-2 imagery for a chosen period and then use XArray and Dask to create a median composite image using distributed processing.


### Setup


```python
%%capture
if 'google.colab' in str(get_ipython()):
    !pip install pystac-client odc-stac rioxarray dask['distributed'] botocore \
      jupyter-server-proxy
```


```python
import dask
import matplotlib.pyplot as plt
import os
import pandas as pd
import geopandas as gpd
import numpy as np
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

### Load City Boundary

Read the file containing the city boundary from your Google Drive saved in the previous notebook.

Run the following cell to authenticate and mount the Google Drive.


```python
if 'google.colab' in str(get_ipython()):
  from google.colab import drive
  drive.mount('/content/drive')
```


```python
drive_folder_root = 'MyDrive'
output_folder = 'python-remote-sensing'
drive_folder_path = os.path.join(
      '/content/drive', drive_folder_root, output_folder)
aoi_filename = 'aoi.geojson'
aoi_filepath = os.path.join(drive_folder_path, aoi_filename)
aoi_filepath
```

Read the GeoJSON.


```python
city_gdf = gpd.read_file(aoi_filepath)
```

Extract the geometry.


```python
geometry = city_gdf.geometry.union_all()
geometry
```

### Search and Load Sentinel-2 Imagery

Let's use Element84 search endpoint to look for items from the `sentinel-2-c1-l2a` collection on AWS. We search for the imagery collected within the date range and intersecting the AOI geometry.

We also specify additonal filters to select scenes based on metadata. The parameter `eo:cloud_cover` contains the overall cloud percentage and we use it to select imagery with < 30% overall cloud cover.


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
items_gdf = gpd.GeoDataFrame.from_features(items.to_dict(), crs='EPSG:4326')

fig, ax = plt.subplots(1, 1)
fig.set_size_inches(5,5)
items_gdf.plot(
    ax=ax,
    facecolor='none',
    edgecolor='black',
    alpha=0.5)

city_gdf.plot(
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
ds = load(
    items,
    bands=['red', 'green', 'blue', 'nir'],
    resolution=10,
    bbox=geometry.bounds,
    crs='utm',
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

### Create a Median Composite
A very-powerful feature of XArray is the ability to easily aggregate data across dimensions - making it ideal for many remote sensing analysis. Let’s create a median composite from all the individual images.

We apply the `.median()` aggregation across the time dimension.


```python
median_composite = ds.median(dim='time')
median_composite
```

Select the required bands.


```python
rgb_composite = median_composite[['red', 'green', 'blue']]
rgb_composite
```

So far all the operations that we have created a computation graph. To run this computation using the local Dask cluster, we must call `.compute()`.


```python
%%time
rgb_composite = rgb_composite.compute()
```

### Visualize the Results

The composite is creating from all the pixels within the bounding box of the geometry. We can use `rioxarray` to clip the image to the city boundary to remove pixels outside the polygon.

To visualize our Dataset, we first convert it to a DataArray using the `to_array()` method. All the variables will be converted to a new dimension. Since our variables are image bands, we give the name of the new dimesion as band.



```python
rgb_composite_da = rgb_composite.to_array('band')
rgb_composite_da
```


```python
image_crs = rgb_composite_da.rio.crs
city_gdf_reprojected = city_gdf.to_crs(image_crs)
rgb_composite_clipped = rgb_composite_da.rio.clip(city_gdf_reprojected.geometry)
rgb_composite_clipped
```

For visualizing, we resample it to a lower resolution preview


```python
preview = rgb_composite_clipped.rio.reproject(
    rgb_composite_clipped.rio.crs, resolution=100
)
```


```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(5,5)
preview.sel(band=['red', 'green', 'blue']).plot.imshow(
    ax=ax,
    robust=True)
ax.set_title('RGB Visualization')
ax.set_axis_off()
ax.set_aspect('equal')
plt.show()
```


    
![](python-remote-sensing-output/module_01/04_median_composite_files/04_median_composite_41_0.png)
    


We can manually apply a contrast stretch as well.


```python
percentile_stretch = (1, 95)
stretch_vmin, stretch_vmax = np.nanpercentile(preview_da.values, percentile_stretch)
print(stretch_vmin, stretch_vmax)
```


```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(5,5)
preview.sel(band=['red', 'green', 'blue']).plot.imshow(
    ax=ax,
    vmin=stretch_vmin,
    vmax=stretch_vmax)
ax.set_title(f'Sentinel-2 Composite {year}')
ax.set_axis_off()
ax.set_aspect('equal')
plt.show()
```


    
![](python-remote-sensing-output/module_01/04_median_composite_files/04_median_composite_44_0.png)
    


### Export the Composite

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
  # Use the local folder
  output_folder_path = output_folder
```

Ww use the `rioxarray` accessor to save the results as a Cloud-Optimized GeoTIFF.


```python
output_file = f'raw_composite_{time_range}.tif'
output_path = os.path.join(output_folder_path, output_file)
rgb_composite_clipped.rio.to_raster(output_path, driver='COG')
print(f'Wrote {output_file}')
```

    Wrote raw_composite_2024.tif


The raw composite is suitable for downstream scientific analysis as it preserves the pixel reflectance values.Sometimes it is desirable to export the output as a colorized RGBA image. This visualized output suitable for use user-facing applications like basemaps or prints.

The `odc-geo` package provides a handy [`to_rgba()`](https://odc-geo.readthedocs.io/en/latest/_api/odc.geo.xr.to_rgba.html) function to save the visualized version of the composite. This function can be used via the `.odc` accessor.


```python
# Convert to a Xarray Dataset first
rgb_composite_ds = rgb_composite_clipped.to_dataset(dim='band')
composite_rgba = rgb_composite_ds.odc.to_rgba(
    vmin=stretch_vmin, vmax=stretch_vmax)

```

Save the visualized output.


```python
visualized_file = f'visualized_composite_{time_range}.tif'
visualized_output_path = os.path.join(output_folder_path, visualized_file)
composite_rgba.odc.write_cog(visualized_output_path)
print(f'Wrote {output_file}')
```

### Exercise

Create and export a median composite for your city using the boundary extracted in the previous section.
