## Creating Maps with GeoPandas

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

### Matplotlib Basics

Before we start using `matplotlib` inside a Jupyter notebook, it is useful to set the matplotlib backend to `inline`. This setting makes the matplotlib graphs included in your notebook, next to the code. [Learn more](https://ipython.readthedocs.io/en/stable/interactive/plotting.html) about different plotting backends.

We use the [magic function](https://ipython.readthedocs.io/en/stable/interactive/tutorial.html#magics-explained) `%matplotlib` to achieve this.


```python
%matplotlib inline
import matplotlib.pyplot as plt
```

It is important to understand the 2 matplotlib objects

* Figure: This is the main container of the plot. A figure can contain multiple plots inside it
* Axes:  Axes refers to an individual plot or graph. A figure contains 1 or more axes.

We create a figure and a single subplot. Specifying 1 row and 1 column for the `subplots()` function create a figure and an axes within it. Even if we have a single plot in the figure, it is useful to use tthis logic of intialization so it is consistent across different scripts.



```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(5,5)
plt.show()
```


    
![](supplement1_plotting_files/supplement1_plotting_9_0.png)
    


First, let's learn how to plot a single point using matplotlib. Let's say we want to display a point at the coordinate (0.5, 0.5). 



```python
point = (0.5, 0.5)
```

We display the point using the `plot()` function. The `plot()` function expects at least 2 arguments, first one being one or more x coordinates and the second one being one or more y coordinates. Remember that once a plot is displayed using `plt.show()`, it displays the plot and empties the figure. So you'll have to create it again.


```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(5,5)
ax.plot(point[0], point[1], color='green', marker='o')
plt.show()
```


    
![](supplement1_plotting_files/supplement1_plotting_13_0.png)
    


One problematic area for plotting geospatial data using matplotlib is that geospatial data is typically represented as a list of x and y coordinates. But to plot it, we require 2 separate lists or x and y coordinates. Here we can use the `zip()` function to create list of x and y coordinates.


```python
points = [(0.1, 0.5), (0.5, 0.5), (0.9, 0.5)]
x, y = zip(*points)
print(x)
print(y)
```

    (0.1, 0.5, 0.9)
    (0.5, 0.5, 0.5)


Now these can be plotted using the `plot()` function. We can set `linestyle=None` so it displays the points but doesn't connect them. You can also use `ax.scatter(x, y)` to create a scatter plot with the same result.


```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(5,5)
ax.plot(x, y, color='green', marker='o', linestyle='none')
plt.show()
```


    
![](supplement1_plotting_files/supplement1_plotting_17_0.png)
    


GeoPandas provides a convenient `plot()` function for GeoDataFrame and GeoSeries objects. It takes care of doing the coordinate transformations so that it can be plotted using matplotlib. Calling `.plot()` on a GeoDataFrame returns a matplotlib axes instance. Any options one can pass to matplotlib as seen before can be used with the GeoPandas `plot()` function. [Learn more](https://geopandas.org/en/stable/docs/user_guide/mapping.html#mapping-and-plotting-tools) about mapping and plotting using GeoPandas.


We will now see different examples of creating maps.

### Rendering Map Layouts

We can now work on creating a *figure* with multiple *axes* - each with a different rendering on a map layer. The `subplots()` function creates one or more plots within the figure. You can design a map layout with multiple rows/columns. In the code below, we create a map with **1** row and **3** columns. Using the `set_size_inches()` function, we set the size of the map to 15in x 7in.


```python
fig, axes = plt.subplots(1, 3)
fig.set_size_inches(15,7)
```


    
![](supplement1_plotting_files/supplement1_plotting_21_0.png)
    


The `subplots()` function returns 2 items. The figure and a tuple with all the axes within the figure. As we have 3 axes, we unpack them into separate variables


```python
ax0, ax1, ax2 = axes
```

GeoDataFrame objects have a `plot()` method that uses `pyplot` and creates a plot. We supply the `ax` object to the function so the resulting plot is displayed in the Axes created previously. Here we add the `districts` polygon layer into the `ax0` object - which refers to the first subplot.


```python
districts.plot(ax=ax0, linewidth=1, facecolor='none', edgecolor='#252525')
fig
```




    
![](supplement1_plotting_files/supplement1_plotting_25_0.png)
    




    <Figure size 432x288 with 0 Axes>


Similarly, we add the `roads` layer to the second axes.


```python
roads.plot(ax=ax1, linewidth=0.4, color='#2b8cbe')
fig
```




    
![](supplement1_plotting_files/supplement1_plotting_27_0.png)
    




    <Figure size 432x288 with 0 Axes>


Lastly, we add the `national_highways` layer to the third axes.


```python
national_highways.plot(ax=ax2, linewidth=1, color='#de2d26')
fig
```




    
![](supplement1_plotting_files/supplement1_plotting_29_0.png)
    




    <Figure size 432x288 with 0 Axes>


We can turn off the coordinates display on the X-axis and Y-axis using `plt.axis('off')`. It is useful to set a title to each map. The `set_title()` function adds the title to the approproate axes. We specify a negative `y` parameter to place the title at the bottom of the map instead of top.


```python
ax0.axis('off')
ax0.set_title('Karnataka Districts', y=-0.1)
ax1.axis('off')
ax1.set_title('Karnataka Major Roads', y=-0.1)
ax2.axis('off')
ax2.set_title('Karnataka National Highways', y=-0.1)
fig
```




    
![](supplement1_plotting_files/supplement1_plotting_31_0.png)
    



Now that our map is ready, we can save the map to the computer using the `savefig()` function.


```python
output_filename = 'map_layout.png'
output_dir = 'output'
output_path = os.path.join(output_dir, output_filename)

if not os.path.exists(output_dir):
    os.mkdir(output_dir)

fig.savefig(output_path, dpi=300)
```

### Creating A Map with Multiple Layers

If we want to display multiple layers, we simply create new plots on the same `Axes`. Here we create a figure with a single axes and add the `districts`,`roads` and `national_highways` layers to the same axes.


```python
fig, ax = plt.subplots()
fig.set_size_inches(10,15)

plt.axis('off')

districts.plot(ax=ax, linewidth=1, facecolor='none', edgecolor='#252525')
roads.plot(ax=ax, linewidth=0.4, color='#2b8cbe')
national_highways.plot(ax=ax, linewidth=1, color='#de2d26')


output_filename = 'multiple_layers.png'
output_path = os.path.join(output_dir, output_filename)
plt.savefig(output_path, dpi=300)
```


    
![](supplement1_plotting_files/supplement1_plotting_36_0.png)
    


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
    plt.annotate(text=row['DISTRICT'], xy=row['label_position'], horizontalalignment='center')

```


    
![](supplement1_plotting_files/supplement1_plotting_41_0.png)
    

