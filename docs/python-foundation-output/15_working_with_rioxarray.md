# Working with rioxarray

[rioxarray](https://corteva.github.io/rioxarray/stable/index.html) is a modern library to work with geospatial data in a gridded format. It excels at providing an easy way to read/write raster data and access individual bands and pixels. It is built on top of several high-performance Python libraries that makes it ideal for working with climate and remote sensing data.

* [XArray](https://docs.xarray.dev/en/stable/) provides pandas-like API to work with multi-dimentional gridded data.
* [RasterIO](https://rasterio.readthedocs.io/en/stable/) adds support for geospatial rasters using the widely used [GDAL]((https://gdal.org/)) library.
* [Dask](https://www.dask.org/?utm_source=xarray-docs) provides built-in support for parallel-computing and working with large datasets.

In this section, we will take 4 individual SRTM tiles around the Mt. Everest region and merge them to a single GeoTiff using rioxarray.

![](https://github.com/spatialthoughts/python-foundation-web/blob/master/images/python_foundation/srtm.png?raw=1)


```python
import os
import rioxarray as rxr
```


```python
data_pkg_path = 'data'
srtm_dir = 'srtm'
filename = 'N28E087.hgt'
path = os.path.join(data_pkg_path, srtm_dir, filename)
```

## Reading Raster Data

RasterIO can read any raster format supported by the GDAL library. We can call the `open()` method with the file path of the raster. The resulting dataset behaves much like Python's File object.


```python
da = rxr.open_rasterio(path)
```

You can check information about the raster by displaying the variable.


```python
da
```

The raster metadata is stored in the `rio` accessor. This is enabled by the `RasterIO` library which provides geospatial functions on top of xarray.


```python
print('CRS:', da.rio.crs)
print('Resolution:', da.rio.resolution())
print('Bounds:', da.rio.bounds())
print('Width:', da.rio.width)
print('Height:', da.rio.height)
```

XArray provides a very powerful way to select subsets of data, using similar framework as Pandas. Similar to Panda’s `loc` and `iloc` methods, XArray provides `sel` and `isel` methods. Since DataArray dimensions have names, these methods allow you to specify which dimension to query.


```python
band = da.sel(band=1)
band
```

You can get the array of pixel values using `values` property. The result will be a NumPy array.


```python
values = band.values
values
```

## Merging Rasters

Let's see how we can read the 4 individual tiles and mosaic them together. rioxarray provides multiple sub-modules for various raster operations. We can use the `rioxarray.merge` module to carry out this operation.

We first find all the individual files in the directory using the `os.listdir()` function.


```python
srtm_path = os.path.join(data_pkg_path, 'srtm')
all_files = os.listdir(srtm_path)
all_files
```

The rasterio.merge module has a `merge()` method that takes a list of *datasets* and returns the merged dataset. So we create an empty list, open each of the files and append it to the list.


```python
da_list = []
for file in all_files:
    path = os.path.join(srtm_path, file)
    da_list.append(rxr.open_rasterio(path))
```

We can pass on the list of tile dataset to the merge method, which will return us the merged data and a new *transform* which contains the updated extent of the merged raster.


```python
from rioxarray.merge import merge_arrays
merged_da = merge_arrays(da_list)
merged_da
```

## Writing Raster Data

We can save the resulting raster in any format supported by GDAL using the `to_raster()` method. Let’s save this as a GeoTIFF file.


```python
output_filename = 'merged.tif'
output_dir = 'output'
output_path = os.path.join(output_dir, output_filename)
```


```python
merged_da.rio.to_raster(output_path)
```

## Exercise

The merged array represents elevation values. The extent of the tiles cover Mt. Everest. Read the resulting raster and find the maximum elevation value contained in it.


```python
import rioxarray as rxr
import os
import numpy as np

output_filename = 'merged.tif'
output_dir = 'output'
output_path = os.path.join(output_dir, output_filename)
```

----
