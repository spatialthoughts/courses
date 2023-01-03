# Working with Geopandas

![](images/python_foundation/geopandas.png)


GeoPandas extends the Pandas library to enable spatial operations. It provides new data types such as **GeoDataFrame** and **GeoSeries** which are subclasses of Pandas **DataFrame** and **Series** and enables efficient vector data processing in Python.


GeoPandas make use of many other widely used spatial libraries - but it provides an interface similar to Pandas that make it intuitive to use it with spatial analysis. GeoPandas is built on top of the following libraries that allow it to be spatially aware.

- [Shapely](https://shapely.readthedocs.io/en/latest/manual.html) for geometric operations (i.e. buffer, intersections etc.)
- [PyProj](https://pyproj4.github.io/pyproj/stable/index.html) for working with projections
- [Fiona](https://pypi.org/project/Fiona/) for file input and output, which itself is based on the widely used [GDAL/OGR](https://gdal.org/) library

We will carry out a geoprocessing task that shows various features of this library and show how to do geo data processing in Python. The task is to take a roads data layer from OpenStreetMap and compute the total length of National Highways for each district in a state. The problem is described in detail in my [Advanced QGIS](https://courses.spatialthoughts.com/advanced-qgis.html#exercise-find-the-length-of-national-highways-in-a-state) course and show the steps needed to perform this analysis in QGIS. We will replicate this example in Python.

![](images/python_foundation/karnataka.png)


By convention, `geopandas` is commonly imported as `gpd`


```python
import geopandas as gpd
```

## Reading Spatial Data


```python
import os
data_pkg_path = 'data'
filename = 'karnataka.gpkg'
path = os.path.join(data_pkg_path, filename)
```

GeoPandas has a `read_file()` method that is able to open a wide variety of vector datasets, including zip files. Here we will open the GeoPackage `karnataka.gpkg` and read a layer called `karnataka_major_roads`. The result of the read method is a **GeoDataFrame**. 


```python
roads_gdf = gpd.read_file(path, layer='karnataka_major_roads')
print(roads_gdf.info())
```

A GeoDataFrame contains a special column called *geometry*. All spatial operations on the GeoDataFrame are applied to the geomety column. The geometry column can be accessed using the `geometry` attribute.


```python
print(roads_gdf.geometry)
```

## Filtering Data

One can use the standard Pandas filtering methods to select a subset of the GeoDataFrame. In addition, GeoPandas also provide way to subset the data based on a bounding box with the [`cx[]` indexer](https://geopandas.readthedocs.io/en/latest/indexing.html).

For our analysis, we need to apply a filter to extract only the road segments where the `ref` attribute starts with **'NH'** - indicating a national highway. We can apply boolean filtering using Panda's `str.match()` method with a regular expression.


```python
filtered = roads_gdf[roads_gdf['ref'].str.match('^NH') == True]
print(filtered.head())
```

## Working with Projections

Dealing with projetions is a key aspect of working with spatial data. GeoPandas uses the `pyproj` library to assign and manage projections. Each GeoDataFrame as a `crs` attribute that contains the projection info. Our source dataset is in EPSG:4326 WGS84 CRS.


```python
print(filtered.crs)
```

Since our task is to compute line lengths, we need to use a Projected CRS. We can use the `to_crs()` method to reproject the GeoDataFrame.


```python
roads_reprojected = filtered.to_crs('EPSG:32643')
print(roads_reprojected.crs)
```

Now that the layer has been reprojected, we can calculate the length of each geometry using the `length` attribute. The result would be in meters. We can add the line lengths in a new column named `length`.


```python
roads_reprojected['length'] = roads_reprojected['geometry'].length
```

We can apply statistical operations on a DataFrame columns. Here we can compute the total length of national highways in the state by calling the `sum()` method.


```python
total_length = roads_reprojected['length'].sum()
print('Total length of national highways in the state is {} KM'.format(total_length/1000))
```

## Performing Spatial joins

There are two ways to combine datasets in geopandas – table joins and spatial joins. For our task, we need information about which district each road segments belongs to. This can be achived using another spatial layer for the districts and doing a spatial join to transfer the attributes of the district layer to the matching road segment.

The `karnataka.gpkg` contains a layer called `karnataka_districts` with the district boundaries and names.


```python
districts_gdf = gpd.read_file(path, layer='karnataka_districts')
print(districts_gdf.head())
```

Before joining this layer to the roads, we must reproject it to match the CRS of the roads layer.


```python
districts_reprojected = districts_gdf.to_crs('EPSG:32643')
```

A spatial join is performed using the `sjoin()` method. It takes 2 core arguments.

- `op`: The spatial predicate to decdie which objects to join. Options are *intersects*, *within* and *contains*.
- `how`: The type of join to perform. Options are *left*, *right* and *inner*.

For our task, we can do a *left* join and add attributes of the district that *intersect* the road.



```python
joined = gpd.sjoin(roads_reprojected, districts_reprojected, how='left', predicate='intersects')
print(joined.head())
```

## Group Statistics

The resulting geodataframe now has the matching column from the intersecting district feature. We can now sum the length of the roads and group them by districts. This type of *Group Statistics* is performed using Panda's `group_by()` method.


```python
results = joined.groupby('DISTRICT')['length'].sum()/1000
print(results)
```

The result of the `group_by()` method is a Pandas *Series*. It can be saved to a CSV file using the `to_csv()` method.


```python
output_filename = 'national_highways_by_districts.csv'
output_dir = 'output'
output_path = os.path.join(output_dir, output_filename)
results.to_csv(output_path)
print('Successfully written output file at {}'.format(output_path))
```

## Exercise

Before writing the output to the file, round the distance numbers to a whole number.

----
