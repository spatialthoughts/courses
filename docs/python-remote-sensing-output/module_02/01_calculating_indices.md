### Overview

Spectral indices are core to many remote sensing analysis. In this section, we will learn how can we perform calculations using XArray.

We will take a single Sentinel-2 scene and calculate spectral indices like NDVI, MNDWI and SAVI.

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

print(f'Environment: {environment}')
```

If we are on Google Colab, install the required packages. Local runtimes are expected to have the packages already installed.


```python
%%capture
if environment in ['colab', 'colab_enterprise']:
    !pip install pystac-client odc-stac rioxarray dask['distributed'] \
        jupyter-server-proxy
```

Import all required libraries. Make sure to import everything at the beginning as certain Xarray extensions are activated on import and registers certain accesors, like `.rio` and `.odc` for Xarray objects.


```python
import dask
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pystac_client
import rioxarray as rxr
import xarray as xr
from odc.stac import configure_s3_access, load
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

### Get a Sentinel-2 Scene

We define a location and time of interest to get some satellite imagery.


```python
latitude = 27.163
longitude = 82.608
year = 2023
```

Search the catalog for matching items.


```python
# Define a GeoJSON geometry
geometry = {
    'type': 'Point',
    'coordinates': [longitude, latitude]
}

# Query the STAC Catalog
catalog = pystac_client.Client.open(
    'https://earth-search.aws.element84.com/v1')

search = catalog.search(
    collections=['sentinel-2-c1-l2a'],
    intersects=geometry,
    datetime=f'{year}',
    query={'eo:cloud_cover': {'lt': 30}, 's2:nodata_pixel_percentage': {'lt': 10}},
    sortby=[{'field': 'properties.eo:cloud_cover', 'direction': 'asc'}]
)
items = search.item_collection()

least_cloudy = items[0]

ds = load(
    [least_cloudy],
    bands=['red', 'green', 'blue', 'nir', 'swir16', 'swir22'],
    resolution=100, # Load the data at lower resolution to speed up processing 
    crs='utm',
    chunks={'x': 1024, 'y': 1024},  # Explicitly define chunk sizes
    groupby='solar_day',
    preserve_original_order=True
)

scene = ds.squeeze()
# Mask nodata values
scene = scene.where(scene != 0)
# Apply scale/offset
scale = 0.0001
offset = -0.1
scene = scene*scale + offset
scene
```

Let's call `compute()` to kick-off the dask graph. Dask will query the cloud-hosted dataset to fetch the required pixels. Once you run the cell, look at the Dask Diagnostic Dashboard to see the data processing in action.


```python
%%time
scene = scene.compute()
```

### Visualize the Scene

To visualize our Dataset, we first convert it to a DataArray using the `to_array()` method. All the variables will be converted to a new dimension. Since our variables are image bands, we give the name of the new dimesion as band.



```python
scene_da = scene.to_array('band')
```

Let's visualize a nature color band combination (RGB).


```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(5,5)
scene_da.sel(band=['red', 'green', 'blue']).plot.imshow(
    ax=ax,
    robust=True)
ax.set_title('RGB Visualization')
ax.set_axis_off()
ax.set_aspect('equal')
plt.show()
```


    
![](python-remote-sensing-output/module_02/01_calculating_indices_files/01_calculating_indices_23_0.png)
    


We can also view a False Color Composite (FCC) with a different combination of spectral bands.


```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(5,5)
scene_da.sel(band=['nir', 'red', 'green']).plot.imshow(
    ax=ax,
    robust=True)
ax.set_title('NRG Visualization')
ax.set_axis_off()
ax.set_aspect('equal')
plt.show()
```


    
![](python-remote-sensing-output/module_02/01_calculating_indices_files/01_calculating_indices_25_0.png)
    


### Calculate Spectral Indices

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

Let's plot a histogram of the NDVI values.


```python
ndvi_values = ndvi.values.flatten()
ndvi_values = ndvi_values[~np.isnan(ndvi_values)]

fig, ax = plt.subplots(1, 1)
fig.set_size_inches(8, 4)

ax.hist(ndvi_values, bins=100, 
        color='#4CAF50', edgecolor='none', alpha=0.85)

ax.set_title('NDVI Distribution', fontsize=14, pad=12)
ax.set_xlabel('NDVI Value', fontsize=11)
ax.set_ylabel('Pixel Count', fontsize=11)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#cccccc')
ax.spines['bottom'].set_color('#cccccc')
ax.yaxis.grid(True, color='#eeeeee', zorder=0)
ax.set_axisbelow(True)
plt.tight_layout()
plt.show()
```


    
![](python-remote-sensing-output/module_02/01_calculating_indices_files/01_calculating_indices_30_0.png)
    


Let’s visualize the results. While the theoritical range of NDVI is between -1 and +1, most vegetation has NDVI values tend to be in the range 0-0.8. We can use this range to visualize the variation the vegetation better.


```python
cbar_kwargs = {
    'orientation':'horizontal',
    'fraction': 0.025,
    'pad': 0.05,
    'extend':'neither'
}
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(5,5)
ndvi.plot.imshow(
    ax=ax,
    cmap='Greens',
    vmin=0,
    vmax=0.8,
    cbar_kwargs=cbar_kwargs)
ax.set_title('NDVI')
ax.set_axis_off()
ax.set_aspect('equal')
plt.show()
```


    
![](python-remote-sensing-output/module_02/01_calculating_indices_files/01_calculating_indices_32_0.png)
    


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

Let's plot a histogram of the MNDWI values.


```python
mndwi_values = mndwi.values.flatten()
mndwi_values = mndwi_values[~np.isnan(mndwi_values)]

fig, ax = plt.subplots(1, 1)
fig.set_size_inches(8, 4)

ax.hist(mndwi_values, bins=100, 
        color="#4F77CD", edgecolor='none', alpha=0.85)

ax.set_title('MNDWI Distribution', fontsize=14, pad=12)
ax.set_xlabel('MNDWI Value', fontsize=11)
ax.set_ylabel('Pixel Count', fontsize=11)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#cccccc')
ax.spines['bottom'].set_color('#cccccc')
ax.yaxis.grid(True, color='#eeeeee', zorder=0)
ax.set_axisbelow(True)
plt.tight_layout()
plt.show()
```


    
![](python-remote-sensing-output/module_02/01_calculating_indices_files/01_calculating_indices_36_0.png)
    


Visualize the MNDWI values.


```python
cbar_kwargs = {
    'orientation':'horizontal',
    'fraction': 0.025,
    'pad': 0.05,
    'extend':'neither'
}
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(5,5)
mndwi.plot.imshow(
    ax=ax,
    cmap='Blues',
    vmin=-0.5,
    vmax=0.5,
    cbar_kwargs=cbar_kwargs)
ax.set_title('MNDWI')
ax.set_axis_off()
ax.set_aspect('equal')
plt.show()
```


    
![](python-remote-sensing-output/module_02/01_calculating_indices_files/01_calculating_indices_38_0.png)
    


The Soil Adjusted Vegetation Index (SAVI) is calculated using the following formula:


`SAVI = (1 + L) * ((NIR - Red)/(NIR + Red + L))`

Where:

*   NIR = Near-Infrared band reflectance
*   Red = Red band reflectance
*   L = Soil brightness correction factor (typically 0.5 for moderate vegetation)


```python
savi = 1.5 * ((nir - red) / (nir + red + 0.5))
```

Close the dask client. This presents multiple clients being instantiated when running different notebooks on the same machine. This is not required on Colab but a good practice when you are running it on a local machine. Uncomment and run to shutdown the dask cluster.


```python
#client.shutdown()
```

### Exercise

A simple technique for water detection is applying a threshold on the MNDWI image. Apply a threshold and create a water mask where all values above the threshold is 1, and others are set to 0.

Hint: Use the [`xarray.where`](https://docs.xarray.dev/en/stable/generated/xarray.where.html) function that allows you to set both matching and non-matching values.



```python
threshold = 0
# Create a new array 'water' where all MNDWI values
#  greater than the threshold is 1 and others are 0
# Visualize the results.
```
