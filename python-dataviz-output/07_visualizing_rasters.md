# Visualizing Rasters

RasterIO supports visualizing raster data using Matplotlib. 

In this section, we will learn how to visualize a DEM raster and annotate it with some information.


```python
import glob
import os
import rasterio
import numpy as np

%matplotlib inline
import matplotlib.pyplot as plt
```

We have 4 different SRTM tiles in the directory. We get a list of them using the `glob` module.


```python
data_pkg_path = 'data'
srtm_path = os.path.join(data_pkg_path, 'srtm', '*.hgt')
all_files = glob.glob(srtm_path)
all_files
```




    ['data/srtm/N28E086.hgt',
     'data/srtm/N28E087.hgt',
     'data/srtm/N27E087.hgt',
     'data/srtm/N27E086.hgt']



Let's open the first tile and read it using rasterio.


```python
file1 = all_files[0]
dataset = rasterio.open(file1)
band = dataset.read(1)
transform = dataset.transform
dataset.close()
```

The `band` variable is a Numpy Array. Matplotlib can render this as an image using the `imshow()` method.


```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(7,7)

ax.imshow(band, cmap='Greys_r')
plt.show()
```


    
![](python-dataviz-output/07_visualizing_rasters_files/07_visualizing_rasters_8_0.png)
    


Notice that the X and Y axis displays the column/row numbers, not coordinates. To display the image with the correct georeference information, rasterio providers a plotting API that correctly transforms the image. Instead of matplotlib's `imshow()`, we use rasterio's `show()` method, which takes an additonal argument for the `transform`.


```python
from rasterio.plot import show

fig, ax = plt.subplots(1, 1)
fig.set_size_inches(7,7)

show(band, cmap='Greys_r', ax=ax, transform=transform)
plt.show()
```


    
![](python-dataviz-output/07_visualizing_rasters_files/07_visualizing_rasters_10_0.png)
    


So far, we have only created a single *Axes* within a *Figure*. But matplotlib allows you to create layouts that can contain multiple plots in a single figure. Let's now visualize all 4 tiles together in a single figure. We first read all tiles and store the opened rasters in a list.


```python
datasets = []
for file in all_files:
    path = os.path.join(srtm_path, file)
    dataset = rasterio.open
```

Create 1 row of 4 subplots using the `subplots()` method.

Reference:
- [matplotlib.pyplot.subplots](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplots.html)
- [Arranging multiple Axes in a Figure
](https://matplotlib.org/stable/tutorials/intermediate/arranging_axes.html)


```python
fig, axes = plt.subplots(1, 4)
fig.set_size_inches(15,3)
plt.tight_layout()
```


    
![](python-dataviz-output/07_visualizing_rasters_files/07_visualizing_rasters_14_0.png)
    


The `axes` variable contains a list of 4 axes objects. We show 1 tile in each of the axes.


```python
fig, axes = plt.subplots(1, 4)
fig.set_size_inches(15,3)
plt.tight_layout()

for index, file in enumerate(python-dataviz-output/all_files):
    with rasterio.open(file) as dataset:
        band = dataset.read(1)
        transform = dataset.transform
    ax = axes[index]
    show(band, ax=ax, cmap='Greys_r', transform=transform)
    filename = all_files[index]
    ax.set_title(os.path.basename(filename))

plt.show()
```


    
![](python-dataviz-output/07_visualizing_rasters_files/07_visualizing_rasters_16_0.png)
    


Since each tile represents a different region, a better visualization would be to merge all of them into a single raster.


```python
from rasterio import merge

dataset_list = []
for file in all_files:
    dataset_list.append(rasterio.open(file))

merged_data, merged_transform = merge.merge(dataset_list)
```

Similarly, we can visualize the merged raster.


```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(12, 12)
show(merged_data, ax=ax, cmap='viridis', transform=merged_transform)
ax.set_title('merged')
plt.show()
```


    
![](python-dataviz-output/07_visualizing_rasters_files/07_visualizing_rasters_20_0.png)
    


The DEM is of the region surrounding Mt.Everest. Let's try to find the coordinates of Mt. Everest by queriing this merged raster for the highest value. The `merged_data` variable contains the numpy array. But it has an extra empty dimension. We use the `squeeze()` method to remove the empty extra dimention and get a 2D array.


```python
merged_array = merged_data.squeeze()
```

Next we obtain the coordinates of the highest pixel value in the array.


```python
rows, cols = np.where(merged_array == np.max(merged_array))
row = rows[0]
col = cols[0]
lon, lat = rasterio.transform.xy(merged_transform, row, col)
print(lat, lon)
```

    27.988888888888887 86.92555555555556


We can use the `annotate()` method to add a label on the plot with a text.


```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(12, 12)
show(merged_data, ax=ax, cmap='viridis', transform=merged_transform)
ax.plot(lon, lat, '^r', markersize=11)
ax.annotate("Mt. Everest",
            xy=(lon, lat), xycoords='data',
            xytext=(20, 20), textcoords='offset points',
            arrowprops=dict(arrowstyle="->", color='black')
            )

output_folder = 'output'
output_path = os.path.join(output_folder, 'mt_everest.png')
plt.savefig(output_path, dpi=300)

plt.show()
```


    
![](python-dataviz-output/07_visualizing_rasters_files/07_visualizing_rasters_26_0.png)
    


## Exercise

Create a layout using the `subplots()` method with 2 rows and 2 columns. Plot a different color marker at location (1,1) in each plot.

Hint: You can access the axes in a particular row/col using the index notation. `axes[0,0]` will return the axes in the first row and first column.
