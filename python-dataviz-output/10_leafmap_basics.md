## Overview

[Leafmap](https://leafmap.org/) is a Python package for interactive mapping that supports a wide-variety of plotting backends. 

We will explore the capabilities of Leafmap and create a map that includes vector and raster layers. For a more comprehensive overview, check out [leafmap key Features](https://leafmap.org/notebooks/00_key_features/).

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

Leafmap's `foliummap` module supports adding a variety of data types along with helper functions such as `set_center()`. Let's add a GeoJSON file to the map using `add_geojson()`.

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
m = leafmap.Map(width=800, height=500)

cog_url = os.path.join(data_url, 'bangalore_lulc_rgb.tif')
bounds = leafmap.cog_bounds(cog_url)

m.add_cog_layer(cog_url, name='Land Use Land Cover')
m.zoom_to_bounds(bounds)
m
```

Leafmap also supports adding custom legends. We define a list of color codes and labels for the land cover classes contained in the `bangalore_lulc.tif` image. We can now add a legend to the map using the `add_legend()` function.

Reference: [leafmap.foliumap.Map.add_legend](https://leafmap.org/foliumap/#leafmap.foliumap.Map.add_legend)


```python
m = leafmap.Map(width=800, height=500)

cog_url = os.path.join(data_url, 'bangalore_lulc_rgb.tif')
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

cog_url = os.path.join(data_url, 'bangalore_lulc_rgb.tif')
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

The code below contains a basic leafmap map. We want to a raster layers of VIIRS Nighttime Lights over India. The URL to a Cloud Optmized GeoTiff (COG) file hosted on Google Cloud Storage is given below.

Add the data to the map and visualize it.

Reference: [`leafmap.Map.add_cog_layer`](https://leafmap.org/leafmap/#leafmap.leafmap.Map.add_cog_layer)

You will need to specify additional `kwargs` parameters to create a correct visualization.

1. The GeoTIFF image is a single-band image with grayscale values of night light intensities. The range of these values are between 0-60. Use `rescale='0,60'`.
2. The image has a nodata values stored as `nan`. Use `nodata='nan`.
3. A grayscale image can be displayed in color using a colormap. Use `colormap_name=viridis`.



```python
gcs_bucket = 'https://storage.googleapis.com/spatialthoughts-public-data/'
cog_url = os.path.join(gcs_bucket, 'viirs_ntl_2021_india.tif')
```
