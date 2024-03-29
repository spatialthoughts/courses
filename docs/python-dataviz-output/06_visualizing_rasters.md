# Visualizing Rasters

[Xarray](http://xarray.pydata.org/) is an evolution of rasterio and is inspired by libraries like pandas to work with raster datasets. It is particularly suited for working with multi-dimensional time-series raster datasets. It also integrates tightly with [dask](https://dask.org/) that allows one to scale raster data processing using parallel computing.

[rioxarray](https://corteva.github.io/rioxarray/stable/index.html) is an extension of xarray that makes it easy to work with geospatial rasters. You can install the `rioxarray` package from the `conda-forge` channel. 

This notebook shows how we can replicate the analysis from the [Working with RasterIO](#working-with-rasterio) exercise and also covers raster data visualization using `matplotlib`. 

### XArray and rioxarray Basics

We start by reading a single SRTM tile containing elevation values.


```python
import os
import numpy as np
data_pkg_path = 'data'
srtm_dir = 'srtm'
filename = 'N28E087.hgt'
path = os.path.join(data_pkg_path, srtm_dir, filename)
```

By convention, `rioxarray` is imported as `rxr`


```python
import rioxarray as rxr
```

The `open_rasterio()` method is able to read any data source supported by `rasterio` library.


```python
rds = rxr.open_rasterio(path)
```

The result is a `xarray.DataArray` object.


```python
type(rds)
```

You can access the pixel values using the `values` property which returns the array’s data as a numpy array.


```python
rds.values
```

A `xarray.DataArray` object also contains 1 or more `coordinates`. Each coordinate is a 1-dimensional array representing values along one of the data axes. In case of the 1-band SRTM elevation data, we have 3 coordinates - `x`, `y` and `band`.


```python
rds.coords
```

A key feature of `xarray` is the ability to access slices of the dataset using [index lookup](http://xarray.pydata.org/en/stable/user-guide/indexing.html) methods. For example, we can slice the main dataset and get the data for Band1 using the `sel()` method.


```python
band1 = rds.sel(band=1)
```

The raster metadata is stored in the [`rio`](https://corteva.github.io/rioxarray/stable/rioxarray.html#rioxarray-rio-accessors) accessor. This is enabled by the `rioxarray` library which provides geospatial functions on top of `xarray`. 


```python
print('CRS:', rds.rio.crs)
print('Resolution:', rds.rio.resolution())
print('Bounds:', rds.rio.bounds())
print('Width:', rds.rio.width)
print('Height:', rds.rio.height)
```

### Merging Rasters

Now that you understand the basic data structure of *xarray* and the &rio* extension, let's use it to process some data. We will take 4 individual SRTM tiles and merge them to a single GeoTiff. You will note that `rioxarray` handles the CRS and transform much better - taking care of internal details and providing a simple API.

> Remember to always import `rioxarray` even if you are using sub-modules. Importing `rioxarray` activates the `rio` accessor which is required for all operations.


```python
import rioxarray as rxr
from rioxarray.merge import merge_arrays
```

Define input and output paths.


```python
srtm_path = os.path.join(data_pkg_path, 'srtm')
all_files = os.listdir(srtm_path)
output_filename = 'merged.tif'
output_dir = 'output'
output_path = os.path.join(output_dir, output_filename)
```

Open each source file using `open_rasterio()` method and store the resulting datasets in a list.


```python
datasets = []
for file in all_files:
    path = os.path.join(srtm_path, file)
    datasets.append(rxr.open_rasterio(path))
```

Use the `merge_arrays()` method from the `rioxarray.merge` module to merge the rasters.


```python
merged = merge_arrays(datasets)
```

Finally, save the merged array to disk as a GeoTiff file.


```python
merged.rio.to_raster(output_path)
```

### Visualizing Rasters using Matplotlib

`xarray` plotting functionality is built on top of the the popular `matplotlib` library. 


```python
%matplotlib inline
import matplotlib.pyplot as plt
```

You cna visualize any `DataArray` object by calling `plot()` method. Here we create a row of 4 plots and render each of the source SRTM rasters. We can use the `cmap` option to specify a color ramp. Here we are using the built-in *Greys* ramp. Appending **_r** gives us the inverted ramp with blacks representing lower elevation values.


```python
fig, axes = plt.subplots(1, 4)
fig.set_size_inches(15,3)
plt.tight_layout()
for index, dataset in enumerate(datasets):
    ax = axes[index]
    dataset.plot(ax=ax, cmap='Greys_r')
    ax.axis('off')
    filename = all_files[index]
    ax.set_title(filename)
```

Similarly, we can visualize the merged raster.


```python
fig, ax = plt.subplots()
fig.set_size_inches(12, 10)
merged.plot(ax=ax, cmap='Greys_r')
ax.set_title('merged')
plt.show()
```


```python
merged
```


```python
bands, rows, cols = np.where(merged == np.max(merged))
band = bands[0]
row = rows[0]
col = cols[0]
print(band, row, col)
```


```python
result = merged.isel(band=band, x=col, y=row)
lat = result.y.values
lon = result.x.values
elevation = int(result)
print(lat, lon, elevation)
```


```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(12, 12)
merged.plot(ax=ax, cmap='viridis')
ax.plot(lon, lat, '^r', markersize=11)
ax.annotate('Mt. Everest (elevation:{}m)'.format(elevation),
            xy=(lon, lat), xycoords='data',
            xytext=(20, 20), textcoords='offset points',
            arrowprops=dict(arrowstyle='->', color='black')
            )

output_folder = 'output'
output_path = os.path.join(output_folder, 'mt_everest.png')
plt.savefig(output_path, dpi=300)

plt.show()
```
