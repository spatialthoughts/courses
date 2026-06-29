### Overview

This section introduces various landcover datasets and shows you how to use them. We will work with two different global landcover datasets [ESA WorldCover](https://esa-worldcover.org/en) and [GLAD Global Land Cover and Land Use Change](https://glad.umd.edu/dataset/GLCLUC2020). You will learn how to:


* Visualize landcover data
* Calculate areas of each landcover class
* How to reclassify and compare different datasets

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
  !pip install pystac-client odc-stac rioxarray xarray-spatial \
    dask[distributed] jupyter-server-proxy planetary_computer
```

Import all required libraries. Make sure to import everything at the beginning as certain Xarray extensions are activated on import and registers certain accesors, like `.rio` and `.odc` for Xarray objects.


```python
import os

import dask.array as da
import geopandas as gpd
import matplotlib.colors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import planetary_computer as pc
import pyproj
import pystac_client
import rioxarray as rxr
import xarray as xr
from affine import Affine
from matplotlib import cm
from odc import stac
from odc.geo.geobox import GeoBox
from odc.stac import load
from xrspatial.classify import reclassify
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

### Get ESA WorldCover Data

Let's use [Planetary Computer STAC API](https://planetarycomputer.microsoft.com/docs/quickstarts/reading-stac/) search endpoint to look for items from the ESA WorldCover collection on Azure Blob Storage.

ESA WorldCover has data for year 2020 and 2021. We will use the 2021 data.


```python
catalog = pystac_client.Client.open(
    'https://planetarycomputer.microsoft.com/api/stac/v1')

search = catalog.search(
    collections=['esa-worldcover'],
    intersects=geometry,
    datetime=f'2020', # Data available only for years 2020 and 2021
)
items = search.item_collection()
items
```

Each STAC item has metadata containing information about the class names, legend colors and pixel values. Let's extract it so we can use it later to contruct a meaningful legend.


```python
class_list = items[0].assets['map'].extra_fields['classification:classes']
class_dict = {
    c['value']: {'description': c['description'], 'hex': c['color_hint']}
    for c in class_list
}
class_dict
```

Load the matching images as a XArray Dataset. Accessing data from Planetary Computer is free but requires getting a Shared Access Signature (SAS) token and sign the URLs. The `planetary_computer` Python package provides a simple mechanism for signing the URLs using `sign()` function.


```python
# Load to XArray
ds = stac.load(
    items,
    bbox=geometry.bounds, # <-- load data only for the bbox
    resolution=10,
    crs='utm',
    chunks={'x': 1024, 'y': 1024},  # Explicitly define chunk sizes
    patch_url=pc.sign,
    groupby='solar_day',
    preserve_original_order=True
)
ds
```

The landcover classification data is in the `map` variable. Select it and remove the empty `time` dimension.


```python
map_data = ds['map'].squeeze()
map_data
```

Run this computation using the local Dask cluster and load the data into memory using `.compute()`.


```python
%%time
map_data = map_data.compute()
```

Clip the data to the geometry. Before we clip, we need to reproject the `aoi_gdf` to the same CRS as the data.


```python
aoi_gdf_reprojected = aoi_gdf.to_crs(map_data.rio.crs)
map_data_clipped = map_data.rio.clip(aoi_gdf_reprojected.geometry)
```

### Visualize the Landcover

To create a meaningful legend, we use the class names and colors from the `class_dict` created earlier.


```python
colors = ['#000000' for r in range(256)]
for key, value in class_dict.items():
    colors[int(key)] = f'#{value['hex']}'

# Set color for value 0 to transparent
colors[0] = (0, 0, 0, 0)
cmap = matplotlib.colors.ListedColormap(colors)

# Data range is 8-bit (0-255)
normalizer = matplotlib.colors.Normalize(vmin=0, vmax=255)

# Set tick labels
values = [key for key in class_dict]
boundaries = [(values[i + 1] + values[i]) / 2 for i in range(len(values) - 1)]
boundaries = [0] + boundaries + [255]
ticks = [
    (boundaries[i + 1] + boundaries[i]) / 2
    for i in range(len(boundaries) - 1)
]
tick_labels = [
    f'{value['description']} ({key})'
     for key, value in class_dict.items()
]
tick_labels
```


```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(12, 10)

map_data_clipped.plot(
    ax=ax, cmap=cmap, norm=normalizer
)

colorbar = fig.colorbar(
    cm.ScalarMappable(norm=normalizer, cmap=cmap),
    boundaries=boundaries,
    values=values,
    cax=fig.axes[1].axes,
)
colorbar.set_ticks(ticks, labels=tick_labels)

ax.set_axis_off()
ax.set_title('Landcover Classes from ESA WorldCover');
```

### Write a Paletted GeoTIFF

Let's save the clipped and reprojected data as a COG.


```python
output_file = 'esa_worldcover_original.tif'
output_path = os.path.join(output_folder, output_file)
map_data_clipped.rio.to_raster(output_path, driver='COG')
print(f'Wrote {output_path}')
```

You will notice that the output image is a single band image with pixel values such as 10, 20, ..., 90. The output image does not have the class colors applied to them. We can instead create a **paletted raster** - which can carry an embedded `colormap` that's applied automatically when the file is read. In the paletted image, the pixel values stay as their original codes (10, 20, and so on), but each one displays in its assigned color, so you get a readable image without losing the underlying data.


We first create a Color Lookup Table (LUT) mapping each pixel value to a RGBA color.


```python
color_table = {
    k: (int(v['hex'][0:2], 16), int(v['hex'][2:4], 16), int(v['hex'][4:6], 16), 255)
    for k, v in class_dict.items()
}
color_table[0] = (0, 0, 0, 0)  # nodata transparent
color_table
```

At present `rioxarray` as well as `odc-geo`packages do not have built-in support for saving a colormap to a Cloud Optimized GeoTIFF (COG). We use the `rasterio` package to attach the colormap instead. Below is a helper function.


```python
def write_cog_with_colormap(data_array, output_path, color_table):
    if data_array.dtype != np.dtype('uint8'):
        raise TypeError(f'data_array must be uint8 for a color table to attach')

    # Write to a temp file, add color table, then convert to COG
    tmp_path = output_path + '.tmp.tif'
    data_array.rio.to_raster(tmp_path)

    with rasterio.open(tmp_path) as src:
        profile = src.profile.copy()
        profile['driver'] = 'COG'
        data = src.read(1)
        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(data, 1)
            dst.write_colormap(1, color_table)

    os.remove(tmp_path)
```

Use the helper function to save the output as a paletted COG. Once saved, open the resulting file in GeoLibre and compare the output against a high-resolution basemap.


```python
output_file = 'esa_worldcover_colormap.tif'
output_path = os.path.join(output_folder, output_file)
write_cog_with_colormap(map_data_clipped, output_path, color_table)
print(f'Wrote {output_path}')
```

### Calculate Class Areas

Landcover datasets are crucial for quantifying landuse patterns. We can now calculate the area of each class within our region of interest. As our data is in a projected CRS, each pixel's area is fixed. We can count the total number of pixels for each class and multiply it by the area of a single pixel to get the area. 

Let's get the underlying array of pixel values.


```python
data = map_data_clipped.values
```

To efficiently get the pixel counts of all unique pixel values in the data, we can use `histogram()` function provided by NumPy. The function takes an array of values and returns counts of each pixel value. We need to specify the bins to be used. Since we need counts for each class, we can use the class values as bins.


```python
# Get unique class values to define histogram bins
unique_classes = sorted(class_dict.keys())
# right edge for last bin
bins = unique_classes + [unique_classes[-1] + 1]

counts, _ = np.histogram(data, bins=bins)
counts
```

We now have pixel counts of each class. We multiply it by the area of each pixel to get the area. We can also filter out pixels with value 0 (nodata pixels) and counts 0 (not present in the region) to get a clean table.


```python
pixel_area_m2 = 100.0

area_df = pd.DataFrame({
    'class_value': unique_classes,
    'area_m2': counts * pixel_area_m2,
})

area_df['class_name'] = area_df['class_value'].map(
    lambda x: class_dict[x]['description'])

# Drop nodata class (0) and classes with no pixels
area_df = area_df[
    (area_df['class_value'] != 0) & (area_df['area_m2'] > 0)]

area_df
```

Save the results as a CSV file.


```python
output_filename = f'aoi_class_areas.csv'
output_filepath = os.path.join(output_folder, output_filename)
area_df.to_csv(output_filepath, index=False)
```

### Load GLAD Annual Land Cover and Land Use Dataset

Let's load another landcover dataset and learn how we can compare two different classification schemes by harmonizing them. [UMD GLAD Annual Land Cover and Land Use (GLCUC)](https://glad.umd.edu/dataset/GLCLUC2020) is a long time-series of landcover classification dataset derived from Landsat. It has detailed classification scheme with over 100 classes grouped into 7 primary classes.

The complete dataset is available on [OpenLandMap STAC Catalog](https://stac.openlandmap.org/). This is a static catalog containing many useful remote sensing dataset. As it is a static catalog, we cannot use the `search` function. You can see [Loading Data from a Static STAC Catalog](https://www.geopythontutorials.com/notebooks/stac_static_catalog.html) for a guide on how to list and load items of interest. 

As we want to access just one image, it is easiest to load it directly. We access the [UMD GLAD annual land cover and land use (GLCLUC)
](https://stac.openlandmap.org/lc_glad.glcluc/collection.json?.language=en) page and obtain the URL for the COG file for 2020 landcover classification. 


```python
data_url = ('https://s3.openlandmap.org/arco/'
            'lc_glad.glcluc_c_30m_s_20200101_20201231_go_epsg.4326_v20230901.tif')
glad_ds = rxr.open_rasterio(
    data_url,
    chunks={'x': 1024, 'y': 1024},
    dtype='uint8',
)
glad_ds

```

This is a global raster at 30m resolution available as a single COG. We can clip and reproject the data to get the subset for our region of interest.


```python
glad_ds = glad_ds.rio.clip_box(*geometry.bounds)
glad_ds = glad_ds.odc.reproject('utm')
glad_ds
```

Remove the empty 'band' dimension.


```python
glad_da = glad_ds.squeeze()
glad_da
```

Run this computation using the local Dask cluster and load the data into memory using `.compute()`.


```python
%%time
glad_da = glad_da.compute()
```


```python
glad_da
```

### Reclassify Pixel Values

GLAD GLCLUC encodes land cover, tree height, and change type in the range (0–254). The table below shows how value ranges map to ESA WorldCover classes.

| GLCLUC Values | GLAD Description | WorldCover Value | WorldCover Class |
|---|---|---|---|
| 0–24 | Terra Firma short vegetation | 30 | Grassland |
| 25–96 | Terra Firma tree cover | 10 | Tree cover |
| 100–124 | Wetland short vegetation | 90 | Herbaceous wetland |
| 125–196 | Wetland tree cover | 10 | Tree cover |
| 208–211 | Open surface water | 80 | Permanent water bodies |
| 240 | Short vegetation after tree loss | 30 | Grassland |
| 241–243 | Snow and ice | 70 | Snow and ice |
| 244–249 | Cropland  | 40 | Cropland |
| 250–253 | Built-up  | 50 | Built-up |
| 254 | Ocean | 80 | Permanent water bodies |


To compare both these datasets, we must harmonize the class values. We use from [`xrspatial.classify.reclassify()`](https://xarray-spatial.readthedocs.io/en/stable/reference/_autosummary/xrspatial.classify.reclassify.html) function from Xarray Spatial package to remap and group the pixel values to match ESA WorldCover classes.



```python
# Each bin defines the upper bound of a range (low, high]
# Gaps (97-99, 197-207, 212-239) are assigned 0 value
bins =       [ 24,  96,  99, 124, 196, 207, 211, 239, 240, 243, 249, 253, 254, 255]
new_values = [ 30,  10,   0,  90,  10,   0,  80,   0,  30,  70,  40,  50,  80,   0]

glad_da_reclass = reclassify(
    glad_da, bins=bins, new_values=new_values, name='glad_reclass'
)
glad_da_reclass
```

Clip the data to geometry. Before we clip, we need to reproject the `aoi_gdf` to the same CRS as the data.


```python
aoi_gdf_reprojected = aoi_gdf.to_crs(glad_da_reclass.rio.crs)
glad_da_reclass_clipped = glad_da_reclass.rio.clip(aoi_gdf_reprojected.geometry)
```

The reclassify function turns the output to `float32`. We convert it back to 8-bit interger and set 0 as nodata. This is required to created a paletted output.


```python
glad_da_reclass_clipped = glad_da_reclass_clipped.fillna(0).astype('uint8')
glad_da_reclass_clipped.rio.set_nodata(0, inplace=True)
glad_da_reclass_clipped
```

### Compare GLCLUC with ESA WorldCover

Plot and compare both the datasets. Notice where both these datasets differ. The different in resolution (10m for ESA WorldCover vs. 30m for GLCLUC) also plays a big role in what features can be distinguished. 


```python
fig, axes = plt.subplots(1, 2)
fig.set_size_inches(20, 8)

glad_da_reclass_clipped.plot(
    ax=axes[0], cmap=cmap, norm=normalizer, add_colorbar=False)
axes[0].set_axis_off()
axes[0].set_title('GLAD GLCLUC Reclassified to ESA WorldCover Classes')

map_data_clipped.plot(
    ax=axes[1], cmap=cmap, norm=normalizer, add_colorbar=False)
axes[1].set_axis_off()
axes[1].set_title('ESA WorldCover')

cbar_ax = fig.add_axes([0.92, 0.1, 0.02, 0.8])

colorbar = fig.colorbar(
    cm.ScalarMappable(norm=normalizer, cmap=cmap),
    boundaries=boundaries,
    values=values,
    cax=cbar_ax,
)
colorbar.set_ticks(ticks, labels=tick_labels)

```

Save the output as a palleted raster. Once saved, open the resulting COG in GeoLibre and compare the output with ESA WorldCover.


```python
output_file = 'glad_glcuc.tif'
output_path = os.path.join(output_folder, output_file)
write_cog_with_colormap(glad_da_reclass_clipped, output_path, color_table)
print(f'Wrote {output_path}')
```

Close the dask client. This presents multiple clients being instantiated when running different notebooks on the same machine. This is not required on Colab but a good practice when you are running it on a local machine. Uncomment and run to shutdown the dask cluster.


```python
client.shutdown()
```

### Exercise

Select only the pixels of *Tree Cover* (class value `10`) from the ESA WorldCover dataset to create a map of tree cover in your region. 

Hint: Use the [`where()`](https://docs.xarray.dev/en/stable/generated/xarray.DataArray.where.html) function.
