## Overview

[Leafmap](https://leafmap.org/) is a Python package for interactive mapping that supports a wide-variety of plotting backends. 

We will explore the capabilities of Leafmap and create a map that includes vector and raster layers.

## Setup and Data Download


```python
%%capture
if 'google.colab' in str(get_ipython()):
  !apt install libspatialindex-dev
  !pip install fiona shapely pyproj rtree mapclassify
  !pip install geopandas
  !pip install leafmap
```


```python
import os
import geopandas as gpd
import leafmap.foliumap as leafmap
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

json_file = 'bangalore_wards.json'
gpkg_file = 'bangalore_roads.gpkg'

data_url = 'https://github.com/spatialthoughts/python-dataviz-web/raw/main/data/bangalore/'

for f in json_file, gpkg_file:
  download(data_url + f)

```

## Leafmap Basics

Reference: [Leafmap Key Features](https://leafmap.org/notebooks/00_key_features/)


```python
m = leafmap.Map(width=800, height=500)
m
```

Leafmap's `foliummap` module supports adding a variety of data types along with helper functions.

Reference: [leafmap.foliumap.Map.add_geojson](https://leafmap.org/foliumap/#leafmap.foliumap.Map.add_geojson)


```python
m = leafmap.Map(width=800, height=500)

json_filepath = os.path.join(data_folder, json_file)

m.add_geojson(json_filepath, layer_name='City')
m.set_center(77.59, 12.97, 10)
m
```


```python
m = leafmap.Map(width=800, height=500)

gpkg_filepath = os.path.join(data_folder, gpkg_file)

roads_gdf = gpd.read_file(gpkg_filepath)

m.add_gdf(roads_gdf, layer_name='Roads', style={'color':'blue', 'weight':0.5})
m.zoom_to_gdf(roads_gdf)
m
```


```python
m = leafmap.Map(width=800, height=500)

cog_url = os.path.join(data_url, 'bangalore_lulc.tif')
bounds = leafmap.cog_bounds(cog_url)

m.add_cog_layer(cog_url, layer_name='Land Use Land Cover')
m.zoom_to_bounds(bounds)
m
```

## Exercise

Leafmap also supports adding custom legends. Below cell contains the color codes and labels for the land cover classes contained in the `bangalore_lulc.tif` image. Add a legend to the map using the `add_legend()` function.

Reference: [leafmap.foliumap.Map.add_legend](https://leafmap.org/foliumap/#leafmap.foliumap.Map.add_legend)


```python
m = leafmap.Map(width=800, height=500)

cog_url = os.path.join(data_url, 'bangalore_lulc.tif')
bounds = leafmap.cog_bounds(cog_url)

m.add_cog_layer(cog_url, layer_name='Land Use Land Cover')
m.zoom_to_bounds(bounds)

# Add a Legend
colors = ['#006400', '#ffbb22','#ffff4c','#f096ff','#fa0000',
          '#b4b4b4','#f0f0f0','#0064c8','#0096a0','#00cf75','#fae6a0']
labels = ["Trees","Shrubland","Grassland","Cropland","Built-up",
          "Barren / sparse vegetation","Snow and ice","Open water",
          "Herbaceous wetland","Mangroves","Moss and lichen"]
m

```
