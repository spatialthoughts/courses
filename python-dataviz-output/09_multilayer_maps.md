## Overview

[Folium](https://python-visualization.github.io/folium/) supports creating maps with multiple layers. Recent versions of GeoPandas have built-in support to create interactive folium maps from a GeoDataFrame. 

In this section, we will create a multi-layer interactive map using 2 vector datasets.

## Setup and Data Download


```python
%%capture
if 'google.colab' in str(get_ipython()):
  !apt install libspatialindex-dev
  !pip install fiona shapely pyproj rtree mapclassify
  !pip install geopandas
```


```python
import os
import folium
from folium import Figure
import geopandas as gpd
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

filename = 'karnataka.gpkg'
data_url = 'https://github.com/spatialthoughts/python-dataviz-web/raw/main/data/osm/'
download(data_url + filename)

```

## Using GeoPandas explore()


```python
data_pkg_path = 'data'
filename = 'karnataka.gpkg'
path = os.path.join(data_pkg_path, filename)
roads_gdf = gpd.read_file(path, layer='karntaka_highways')
districts_gdf = gpd.read_file(path, layer='karnataka_districts')
state_gdf = gpd.read_file(path, layer='karnataka')

```

We can use the [explore()](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.explore.html) method to create an interactive folium map from the GeoDataFrame. When you call `explore()` a folium object is created. You can save that object and use it to display or add more layers to the map.


```python
m = districts_gdf.explore()
m
```

The default output of the `explore()` method is a full-width folium map. If you need more control, a better approach is to create a `follium.Figure` object and add the map to it. For this approach we need to first compute the extent of the map.


```python
bounds = districts_gdf.total_bounds
bounds
```

Now we can create a figure of the required size, and add a folium map to it. The `explore()` function takes a `m` agrument where we can supply an existing folium map to which to render the GeoDataFrame.


```python
fig = Figure(width=800, height=400)

m = folium.Map()
m.fit_bounds([[bounds[1],bounds[0]], [bounds[3],bounds[2]]])

districts_gdf.explore(m=m)

fig.add_child(m)
```


```python
fig = Figure(width=800, height=400)

m = folium.Map(tiles='Stamen Terrain')
m.fit_bounds([[bounds[1],bounds[0]], [bounds[3],bounds[2]]])

districts_gdf.explore(
    m=m,
    color='black', 
    style_kwds={'fillOpacity': 0.3, 'weight': 0.5},
  )

fig.add_child(m)
```


```python
roads_gdf
```


```python
def get_category(row):
    ref = str(row['ref'])
    if 'NH' in ref:
        return 'NH'
    elif 'SH' in ref:
        return 'SH'
    else:
        return 'NA'
    
roads_gdf['category'] = roads_gdf.apply(get_category, axis=1)
```


```python
fig = Figure(width=800, height=400)

m = folium.Map()
m.fit_bounds([[bounds[1],bounds[0]], [bounds[3],bounds[2]]])

roads_gdf.explore(
    m=m,
    column='category', 
    categories=['NH', 'SH'], 
    cmap=['#1f78b4', '#e31a1c'],
    categorical=True
)

fig.add_child(m)
```

## Create Multi-layer Maps

When you call `explore()` a folium object is created. You can save that object and add more layers to the same object.


```python
fig = Figure(width=800, height=400)

m = folium.Map(tiles='Stamen Terrain')
m.fit_bounds([[bounds[1],bounds[0]], [bounds[3],bounds[2]]])

districts_gdf.explore(
    m=m,
    color='black', 
    style_kwds={'fillOpacity': 0.3, 'weight':0.5},
    name='districts',
    tooltip=False)

roads_gdf.explore(
    m=m,
    column='category', 
    categories=['NH', 'SH'], 
    cmap=['#1f78b4', '#e31a1c'],
    categorical=True,
    name='highways'
)

fig.add_child(m)
```

To make our map easier to explore, we also add a *Layer Control* that displays the list of layers on the top-right corner and also allows the users to turn them on or off. The `name` parameter to the `explore()` function controls the name that will be displayed in the layer control.


```python
folium.LayerControl().add_to(m)
m
```

## Exercise

Add the `state_gdf` layer to the folium map below with a thick blue border and no fill. Save the resulting map as a HTML file on your computer.

Hint: Use the `style_kwds` with *'fill'* and *'weight'* options.


```python
fig = Figure(width=800, height=400)

m = folium.Map(tiles='Stamen Terrain')
m.fit_bounds([[bounds[1],bounds[0]], [bounds[3],bounds[2]]])

districts_gdf.explore(
    m=m,
    color='black', 
    style_kwds={'fillOpacity': 0.3, 'weight':0.5},
    name='districts',
    tooltip=False)

roads_gdf.explore(
    m=m,
    column='category', 
    categories=['NH', 'SH'], 
    cmap=['#1f78b4', '#e31a1c'],
    categorical=True,
    name='highways'
)

fig.add_child(m)
folium.LayerControl().add_to(m)
m

```
