### Downloading and Visualizing OSM Data with LeafMap

[Leafmap](https://leafmap.org/) comes with handy utilities to work with OpenStreetMap data. Using the popular package OSMNx in the background, it provides utility functions to download and visualize data from the OSM database.

* [Leafmap OpenStreetMap Features](https://leafmap.org/notebooks/15_openstreetmap/)
* [`leafmap.osm` module](https://leafmap.org/osm/)

#### Setup and Data Download


```python
%%capture
if 'google.colab' in str(get_ipython()):
  !apt install libspatialindex-dev
  !pip install fiona shapely pyproj rtree mapclassify
  !pip install geopandas
  !pip install leafmap
  !pip install osmnx
```


```python
import os
import geopandas as gpd
import folium
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

#### Downloading OSM Data

We can easily download data for a city or a region by its name using the `leafmap.osm_gdf_from_place()` function. We can specify the list of required tags using a dictionary. See [OSM Wiki](https://wiki.openstreetmap.org/wiki/Map_features) for a complete list of tags and values.

You can also download data using a bounding box using `leafmap.osm.osm_gdf_from_bbox()` function.

Reference: [`leafmap.osm_gdf_from_place`](https://leafmap.org/osm/#leafmap.osm.osm_gdf_from_place)


```python
parking_gdf = leafmap.osm_gdf_from_place(
    'Bangalore', 
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
    parking_gdf_subset['geometry'].apply(lambda x : x.type == 'Polygon' )]
parking_locations = parking_gdf_subset[
    parking_gdf_subset['geometry'].apply(lambda x : x.type == 'Point' )]
```

We can save the resulting GeoDataFrame to a GeoPackage.


```python
output_file = 'parking.gpkg'
output_path = os.path.join(output_folder, output_file)
parking_zones.to_file(driver='GPKG', filename=output_path, layer='zones')
parking_locations.to_file(driver='GPKG', filename=output_path, layer='locations')
```

### Visualizing OSM Data

The `leafmap.osm` module has many functions that can add OSM data directy to the map. Here we use `add_osm_from_geocode()` function to add the boundary of a region from OSM. In addition, we can select a basemap from `leafmap.basemaps.keys()` for the map.


```python
m = leafmap.Map(width=800, height=500)
m.add_basemap('CartoDB.DarkMatter')
m.add_osm_from_geocode('Bangalore', layer_name='Bangalore', info_mode=None)
m
```

We can add the GeoDataFrame to the map as well using GeoPanda's `explore()` function which allows us to customize the marker's shape, size for the point layer.


```python
m = leafmap.Map(width=800, height=500)
m.add_basemap('CartoDB.DarkMatter')
m.add_osm_from_geocode('Bangalore', layer_name='Bangalore', info_mode=None)
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
