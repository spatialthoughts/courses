## Maps and Plots with GeoPandas

GeoPandas comes with built-in functions for visualizing geospatial data and creating maps. It uses the very powerful `matplotlib` library to do the plotting. If you are not familiar with matplotlib, check out this [introductory tutorial](https://www.data-blogger.com/2017/11/15/python-matplotlib-pyplot-a-perfect-combination/).

This notebook shows how we can create visualizaion using the datasets from the [Working with GeoPandas](#working-with-geopandas) exercise.


```python
import geopandas as gpd
import os
data_pkg_path = 'data'
filename = 'karnataka.gpkg'
path = os.path.join(data_pkg_path, filename)
districts = gpd.read_file(path, layer='karnataka_districts')
roads = gpd.read_file(path, layer='karnataka_major_roads')
national_highways = roads[roads['ref'].str.match('^NH') == True]
```

### Creating A Map with Multiple Layers

Before we start using `matplotlib` inside a Jupyter notebook, it is useful to set the matplotlib backend to `inline`. This setting makes the matplotlib graphs included in your notebook, next to the code. We use the [magic function](https://ipython.readthedocs.io/en/stable/interactive/tutorial.html#magics-explained) `%matplotlib` to achieve this.


```python
%matplotlib inline
import matplotlib.pyplot as plt
```

We first create an empty plot of size 10in x 15in. The `plt.subplots()` function returns 2 objects

* Figure: This is the main container of the plot. A figure can contain multiple plots inside it
* Axes:  Axes refers to an individual plot or graph. A figure contains 1 or more axes.


```python
fig, ax = plt.subplots(figsize=(10, 15))
```


    
![](supplement1_plotting_files/supplement1_plotting_8_0.png)
    


GeoDataFrame objects have a `plot()` method that uses `pyplot` and creates a plot. We supply the `ax` object to the function so the resulting plot is displayed in the Axes created previously.


```python
fig, ax = plt.subplots(figsize=(10, 15))

districts.plot(ax=ax, linewidth=1, facecolor='none', edgecolor='#252525')
```




    <AxesSubplot:>




    
![](supplement1_plotting_files/supplement1_plotting_10_1.png)
    


If we want to display multiple layers, we simply create new plots on the same `Axes`. Here we add both the `districts` and `roads` layer to the same plot.


```python
fig, ax = plt.subplots(figsize=(10, 15))

districts.plot(ax=ax, linewidth=1, facecolor='none', edgecolor='#252525')
roads.plot(ax=ax, linewidth=0.4, color='#2b8cbe')
```




    <AxesSubplot:>




    
![](supplement1_plotting_files/supplement1_plotting_12_1.png)
    


We can also save the map to the computer using the `savefig()` function. We create a path to the output file. 


```python
output_filename = 'map.png'
output_dir = 'output'
output_path = os.path.join(output_dir, output_filename)

if not os.path.exists(output_dir):
    os.mkdir(output_dir)
```

We can add one more layer of `national_highways` to the map and turn off the coordinates display on the X-axis and Y-axis using `plt.axis('off')`.

> Remember to call `savefig()` *BEFORE* displaying the map. Matplotlib resets the `ax` object once the plot is displayed. 


```python
fig, ax = plt.subplots(figsize=(10, 15))
plt.axis('off')

districts.plot(ax=ax, linewidth=1, facecolor='none', edgecolor='#252525')
roads.plot(ax=ax, linewidth=0.4, color='#2b8cbe')
national_highways.plot(ax=ax, linewidth=1, color='#de2d26')

plt.savefig(output_path, dpi=300)
```


    
![](supplement1_plotting_files/supplement1_plotting_16_0.png)
    


### Labelling Features

We can also add labels to the maps, but that requires a bit of pre-processing. Let's say we want to add a label for each of the distrit polygons. First, we need to decide the anchor position of the label. We can use `representative_point()` to get a point inside each polygon that best represents the geometry. It is similar to a centroid, but is guranteed to be inside the polygon. Below code creates a new field in the GeoDataFrame called `label_position` with the coordinates of the anchor point.


```python
districts['label_position'] = districts['geometry'].apply(lambda x: x.representative_point().coords[:])
districts['label_position'] = [coords[0] for coords in districts['label_position']]
```

Now we can use the `annotate()` function and iterate over each polygon to add labels with the name of the district from the *DISTRICT* column and place it at the coordinates from the *label_position* column.


```python
fig, ax = plt.subplots(figsize=(10, 15))
plt.axis('off')

districts.plot(ax=ax, linewidth=1, facecolor='none', edgecolor='#252525')

for idx, row in districts.iterrows():
    plt.annotate(text=row['DISTRICT'], xy=row['label_position'],horizontalalignment='center')

```


    
![](supplement1_plotting_files/supplement1_plotting_21_0.png)
    

