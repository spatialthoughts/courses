## Overview

Spectral indices are core to many remote sensing analysis. In this section, we will learn how can we perform calculations using XArray.

We will take a single Sentinel-2 scene and calculate spectral indices like NDVI, MNDWI and SAVI.

## Setup and Data Download

The following blocks of code will install the required packages and download the datasets to your Colab environment.


```python
%%capture
if 'google.colab' in str(get_ipython()):
    !pip install pystac-client odc-stac rioxarray dask jupyter-server-proxy
```


```python
import os
import matplotlib.pyplot as plt
import pandas as pd
import pystac_client
from odc import stac
import xarray as xr
import rioxarray as rxr
```


```python
from dask.distributed import Client
client = Client()  # set up local cluster on the machine
client
```

f you are running this notebook in Colab, you will need to create and use a proxy URL to see the dashboard running on the local server.


```python
if 'google.colab' in str(get_ipython()):
    from google.colab import output
    port_to_expose = 8787  # This is the default port for Dask dashboard
    print(output.eval_js(f'google.colab.kernel.proxyPort({port_to_expose})'))

```

## Get a Sentinel-2 Scene

We define a location and time of interest to get some satellite imagery.


```python
latitude = 27.163
longitude = 82.608
year = 2023
```


```python
# Define a small bounding box around the chosen point
km2deg = 1.0 / 111
x, y = (longitude, latitude)
r = 1 * km2deg  # radius in degrees
bbox = (x - r, y - r, x + r, y + r)
```

Search the catalog for matching items.


```python
# Query the STAC Catalog
catalog = pystac_client.Client.open(
    'https://earth-search.aws.element84.com/v1')

search = catalog.search(
    collections=['sentinel-2-c1-l2a'],
    bbox=bbox,
    datetime=f'{year}',
    query={'eo:cloud_cover': {'lt': 30}, 's2:nodata_pixel_percentage': {'lt': 10}},
    sortby=[{'field': 'properties.eo:cloud_cover', 'direction': 'asc'}]

)
items = search.item_collection()

# Load to XArray
ds = stac.load(
    items,
    bands=['red', 'green', 'blue', 'nir', 'swir16'],
    resolution=10,
    chunks={},  # <-- use Dask
    groupby='solar_day',
    preserve_original_order=True
)

# Select the first scene
timestamp = pd.to_datetime(items[0].properties['datetime']).tz_convert(None)
scene = ds.sel(time=timestamp)
# Mask nodata values
scene = scene.where(scene != 0)
# Apply scale/offset
scale = 0.0001
offset = -0.1
scene = scene*scale + offset
```

## Visualize the Scene

To visualize our Dataset, we first convert it to a DataArray using the `to_array()` method. All the variables will be converted to a new dimension. Since our variables are image bands, we give the name of the new dimesion as band.



```python
scene_da = scene.to_array('band')
```

Rather than loading the entire scene into memory, we resample it to a lower resolution preview and render it.


```python
preview = scene_da.rio.reproject(
    scene.rio.crs, resolution=300
)

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

We can also view a False Color Composite (FCC) with a different combination of spectral bands.


```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(5,5)
preview.sel(band=['nir', 'red', 'green']).plot.imshow(
    ax=ax,
    robust=True)
ax.set_title('NRG Visualization')
ax.set_axis_off()
plt.show()
```

## Calculate Spectral Indices

The Normalized Difference Vegetation Index (NDVI) is calculated using the following formula:

`NDVI = (NIR - Red)/(NIR + Red)`

Where:
*   NIR = Near-Infrared band reflectance
*   Red = Red band reflectance


```python
red = scene_da.sel(band='red')
nir = scene_da.sel(band='nir')

ndvi = (nir - red)/(nir + red)
ndvi
```

Let’s visualize the results.


```python
ndvi_preview = ndvi.rio.reproject(
    ndvi.rio.crs, resolution=300
)
cbar_kwargs = {
    'orientation':'horizontal',
    'fraction': 0.025,
    'pad': 0.05,
    'extend':'neither'
}
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(5,5)
ndvi_preview.plot.imshow(
    ax=ax,
    cmap='Greens',
    robust=True,
    cbar_kwargs=cbar_kwargs)
ax.set_title('NDVI')
ax.set_axis_off()
plt.show()
```

The Modified Normalized Difference Water Index (MNDWI) is calculated using the following formula:

`MNDWI = (Green - SWIR1)/(Green + SWIR1)`

Where:
*   Green = Green band reflectance
*   SWIR1 = Short-wave infrared band 1 reflectance


```python
green = scene_da.sel(band='green')
swir16 = scene_da.sel(band='swir16')
mndwi = (green - swir16)/(green + swir16)
```

The Soil Adjusted Vegetation Index (SAVI) is calculated using the following formula:


`SAVI = (1 + L) * ((NIR - Red)/(NIR + Red + L))`

Where:
*   NIR = Near-Infrared band reflectance
*   Red = Red band reflectance
*   L = Soil brightness correction factor (typically 0.5 for moderate vegetation)


```python
savi = 1.5 * ((nir - red) / (nir + red + 0.5))
```

## Save the Computed Indices

Rather than saving it to the temporary machine where Colab is running, we can save it to our own Google Drive. This will ensure the image will be available to us even after existing Google Colab.

Run the following cell to authenticate and mount the Google Drive.


```python
from google.colab import drive
drive.mount('/content/drive')
```


```python
drive_folder_root = 'MyDrive'
output_folder = 'data'
output_folder_path = os.path.join(
    '/content/drive', drive_folder_root, output_folder)

# Check if Google Drive is mounted
if not os.path.exists('/content/drive'):
    print("Google Drive is not mounted. Please run the cell above to mount your drive.")
else:
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)
```


```python
files = {
    'ndvi.tif': ndvi,
    'mndwi.tif': mndwi,
    'savi.tif': savi
}

for file in files:
  output_path = os.path.join(output_folder_path, file)
  files[file].rio.to_raster(output_path, driver='COG')
  print(f'Saved {file} to {output_path}')
```
