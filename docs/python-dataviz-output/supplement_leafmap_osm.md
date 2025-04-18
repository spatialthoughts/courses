### Downloading and Visualizing OSM Data with LeafMap

We can use the popular package OSMNx to download data from the OSM database and visualize it using leafmap.

<img src='https://courses.spatialthoughts.com/images/python_dataviz/leafmap_osm.png' width=600/>


#### Setup and Data Download


```python
%%capture
if 'google.colab' in str(get_ipython()):
  !pip install leafmap osmnx mapclassify
```


```python
import folium
import geopandas as gpd
import leafmap.foliumap as leafmap
import osmnx as ox
import os
```


```python
data_folder = 'data'
output_folder = 'output'

if not os.path.exists(data_folder):
    os.mkdir(data_folder)
if not os.path.exists(output_folder):
    os.mkdir(output_folder)
```

#### Downloading OSM Data

We can easily download data for a city or a region by its name using the `osmnx.features.features_from_place()` function. We can specify the list of required tags using a dictionary. See [OSM Wiki](https://wiki.openstreetmap.org/wiki/Map_features) for a complete list of tags and values.

You can also download data using a bounding box using `osmnx.features.features_from_bbox()` function.

Reference: [`osmnx.features.features_from_place`](https://osmnx.readthedocs.io/en/stable/user-reference.html#osmnx.features.features_from_place)


```python
parking_gdf = ox.features.features_from_place(
    query='Bangalore',
    tags={'amenity': ['parking', 'parking_space', 'parking_entrance']}
  )
```

The GeoDataFrame has a hierarchical MultiIndex. Let's flatten it using `reset_index()`


```python
parking_gdf = parking_gdf.reset_index(level=[0,1])
```

The result has many columns. Let's filter to required columns.


```python
parking_gdf_subset = parking_gdf[['amenity','parking', 'access', 'geometry']]
```

The results contains both points and polygon features. Let's separate them out.


```python
parking_zones = parking_gdf_subset[
    parking_gdf_subset['geometry'].apply(lambda x : x.geom_type == 'Polygon' )]
parking_locations = parking_gdf_subset[
    parking_gdf_subset['geometry'].apply(lambda x : x.geom_type == 'Point' )]
```

We can save the resulting GeoDataFrame to a GeoPackage.


```python
output_file = 'parking.gpkg'
output_path = os.path.join(output_folder, output_file)
parking_zones.to_file(driver='GPKG', filename=output_path, layer='zones')
parking_locations.to_file(driver='GPKG', filename=output_path, layer='locations')
```

#### Visualizing OSM Data

For visualizing the data, we first download the city boundary from OSM. We use `osmnx.geocoder.geocode_to_gdf` function to extract the boundary as a GeoDataFrame.

Reference: [`osmnx.geocoder.geocode_to_gdf`](https://osmnx.readthedocs.io/en/stable/user-reference.html#osmnx.geocoder.geocode_to_gdf)


```python
boundary = ox.geocoder.geocode_to_gdf(query='Bangalore')
```

We initialize a leafmap Map and select a basemap. See all available basemaps names using `leafmap.basemaps.keys()`.


```python
m = leafmap.Map(width=800, height=500)
m.add_basemap('CartoDB.DarkMatter')
m
```

We can add the GeoDataFrame to the map as well using GeoPanda's `explore()` function which allows us to customize the marker's shape, size for the point layer.


```python
m = leafmap.Map(width=800, height=500)
m.add_basemap('CartoDB.DarkMatter')
m.zoom_to_gdf(boundary)

boundary.explore(
  style_kwds={'fillColor': 'None', 'color': 'blue'},
  m=m,
  name='Bangalore'
)

parking_zones.explore(
    style_kwds={'fillOpacity': 0.3, 'weight': 0.5},
    color='orange',
    name='parking zones',
    m=m)

parking_locations.explore(
    marker_type='circle',
    marker_kwds={'radius': 1},
    color='yellow',
    name='parking locations',
    m=m)
m
```
