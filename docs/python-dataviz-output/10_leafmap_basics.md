## Overview

[Leafmap](https://leafmap.org/) is a Python package for interactive mapping that supports a wide-variety of plotting backends.

We will explore the capabilities of Leafmap and create a map that includes vector and raster layers. For a more comprehensive overview, check out [leafmap key Features](https://leafmap.org/notebooks/00_key_features/).

## Setup and Data Download


```python
%%capture
if 'google.colab' in str(get_ipython()):
  !pip install leafmap rioxarray
```


```python
import os
import geopandas as gpd
import leafmap.foliumap as leafmap
import requests
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
      with requests.get(url, stream=True, allow_redirects=True) as r:
          with open(filename, 'wb') as f:
              for chunk in r.iter_content(chunk_size=8192):
                  f.write(chunk)
      print('Downloaded', filename)
```


```python
json_file = 'bangalore_wards.json'
gpkg_file = 'bangalore_roads.gpkg'

data_url = 'https://github.com/spatialthoughts/python-dataviz-web/releases/' \
  'download/bangalore/'

for f in json_file, gpkg_file:
  download(data_url + f)
```

## Creating a Map


```python
m = leafmap.Map(width=800, height=500)
m
```

You can change the basemap to a Google basemap and set the center of the map. `leafmap.Map()` supports many arguments to customize the map and available controls.

References:

* [`leafmap.leafmap.Map`](https://leafmap.org/leafmap/#leafmap.leafmap.Map)
* [`ipyleaflet.leaflet.Map`](https://ipyleaflet.readthedocs.io/en/latest/api_reference/index.html#ipyleaflet.leaflet.Map)


```python
m = leafmap.Map(width=800, height=500, google_map='HYBRID', center=(12.97, 77.59), zoom=10)
m
```

## Adding Data Layers

Leafmap's `foliumap` module supports adding a variety of data types along with helper functions such as `set_center()`. Let's add a GeoJSON file to the map using `add_geojson()`.

Reference: [leafmap.foliumap.Map.add_geojson](https://leafmap.org/foliumap/#leafmap.foliumap.Map.add_geojson)


```python
m = leafmap.Map(width=800, height=500)

json_filepath = os.path.join(data_folder, json_file)

m.add_geojson(json_filepath, layer_name='City')
m.set_center(77.59, 12.97, 10)
m
```

We can also add any vector layer that can be read by GeoPandas. Here we add a line layer from a GeoPackage using the `add_gdf()` function. The styling parameters can be any folium supported styles.


```python
m = leafmap.Map(width=800, height=500)

gpkg_filepath = os.path.join(data_folder, gpkg_file)

roads_gdf = gpd.read_file(gpkg_filepath)

m.add_gdf(roads_gdf, layer_name='Roads', style={'color':'blue', 'weight':0.5})
m.zoom_to_gdf(roads_gdf)
m
```

A very useful feature of LeafMap is the ability to load a Cloud-Optimized GeoTIFF (COG) file directly from a URL without the need of a server. The file is streamed directly and high-resolution tiles are automatically fetched as you zoom in. We load a 8-bit RGB image hosted on GitHub using the `add_cog_layer()` function.

Reference: [`leafmap.Map.add_cog_layer`](https://leafmap.org/leafmap/#leafmap.leafmap.Map.add_cog_layer)


```python
cog_url = os.path.join(data_url, 'bangalore_lulc_rgb.tif')
cog_url
```


```python
m = leafmap.Map(width=800, height=500)

bounds = leafmap.cog_bounds(cog_url)

m.add_cog_layer(cog_url, name='Land Use Land Cover')
m.zoom_to_bounds(bounds)
m
```

Leafmap also supports adding custom legends. We define a list of color codes and labels for the land cover classes contained in the `bangalore_lulc.tif` image. We can now add a legend to the map using the `add_legend()` function.

Reference: [leafmap.foliumap.Map.add_legend](https://leafmap.org/foliumap/#leafmap.foliumap.Map.add_legend)


```python
m = leafmap.Map(width=800, height=500)

bounds = leafmap.cog_bounds(cog_url)

m.add_cog_layer(cog_url, name='Land Use Land Cover')
m.zoom_to_bounds(bounds)

# Add a Legend
colors = ['#006400', '#ffbb22','#ffff4c','#f096ff','#fa0000',
          '#b4b4b4','#f0f0f0','#0064c8','#0096a0','#00cf75','#fae6a0']
labels = ["Trees","Shrubland","Grassland","Cropland","Built-up",
          "Barren / sparse vegetation","Snow and ice","Open water",
          "Herbaceous wetland","Mangroves","Moss and lichen"]
m.add_legend(colors=colors, labels=labels)
m
```

We can save the resulting map to a HTML file using the `to_html()` function.


```python
m = leafmap.Map(width=800, height=500)

bounds = leafmap.cog_bounds(cog_url)

m.add_cog_layer(cog_url, name='Land Use Land Cover')
m.zoom_to_bounds(bounds)

# Add a Legend
colors = ['#006400', '#ffbb22','#ffff4c','#f096ff','#fa0000',
          '#b4b4b4','#f0f0f0','#0064c8','#0096a0','#00cf75','#fae6a0']
labels = ["Trees","Shrubland","Grassland","Cropland","Built-up",
          "Barren / sparse vegetation","Snow and ice","Open water",
          "Herbaceous wetland","Mangroves","Moss and lichen"]
m.add_legend(colors=colors, labels=labels)

output_file = 'lulc.html'
output_path = os.path.join(output_folder, output_file)
m.to_html(output_path)
```

## Exercise

We want to visualize a large (7.9GB) raster on the map. The URL to a Cloud Optmized GeoTiff (COG) file hosted on Google Cloud Storage is given below. Add the raster to the map, apply a colormap and zoom the map to your region of interest.

<img src='https://courses.spatialthoughts.com/images/python_dataviz/leafmap_cog.png' width=600/>




Use the code block below as your starting point.

Hints:

* The GeoTIFF image is a single-band image with grayscale values of night time light intensities. Specify additional `kwargs` parameters from [`leafmap.Map.add_cog_layer()`](https://leafmap.org/leafmap/#leafmap.leafmap.Map.add_cog_layer).
  * The range of these values are between 0-60. Use `rescale='0,60'`.
  * A grayscale image can be displayed in color using a named colormap. For example `colormap_name='viridis'`.
  * The map automatically zooms to the extent of the COG. Turn that behavior off by supplying `zoom_to_layer=False`.
* To zoom to your chosen region, use [`leafmap.Map.zoom_to_bounds()`](https://leafmap.org/leafmap/#leafmap.leafmap.Map.zoom_to_bounds) method with the bounding box in the `[minx, miny, maxx, maxy]` format. You can use this [bounding box app](https://boundingbox.streamlit.app/) to find the coordinates for your region.


```python
gcs_bucket = 'https://storage.googleapis.com/spatialthoughts-public-data/ntl/viirs/'
cog_url = os.path.join(gcs_bucket, 'viirs_ntl_2021_global.tif')
```
