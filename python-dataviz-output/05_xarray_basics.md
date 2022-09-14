## Overview

Many climate and meteorological datasets come as gridded rasters in data formats such as NetCDF and GRIB. We will use [XArray](http://xarray.pydata.org/) to read, process and visualize the gridded raster dataset.

Xarray is an evolution of rasterio and is inspired by libraries like pandas to work with raster datasets. It is particularly suited for working with multi-dimensional time-series raster datasets. It also integrates tightly with dask that allows one to scale raster data processing using parallel computing. XArray provides [Plotting Functions](https://xarray.pydata.org/en/stable/user-guide/plotting.html) based on Matplotlib. 

In this section, we will take the [Gridded Monthly Temperature Anomaly Data](https://data.giss.nasa.gov/gistemp/) from 1880-present from GISTEMP and visualize the temperature anomaly for the year 2021.

## Setup and Data Download

The following blocks of code will install the required packages and download the datasets to your Colab environment.


```python
import os
import matplotlib.pyplot as plt
import xarray as xr
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

filename = 'gistemp1200_GHCNv4_ERSSTv5.nc'
data_url = 'https://github.com/spatialthoughts/python-dataviz-web/raw/main/data/gistemp/'

download(data_url + filename)
```

## XArray Terminology

By convention, XArray is imported as `xr`. We use Xarray's `open_dataset()` method to read the gridded raster. The result is a `xarray.Dataset` object.



```python
file_path = os.path.join(data_folder, filename)
ds = xr.open_dataset(file_path)
ds
```

The NetCDF file contains a grid of values for each month from 1880-2021 at a spatial resolution of 2 degrees. Let's understand what is contained in a Dataset.

* *Variables*: This is similar to a band in a raster dataset. Each variable contains an array of values.
* *Dimensions*: This is similar to number of array axes.
* *Coordinates*: These are the labels for values in each dimension. 
* *Attributes*: This is the metadata associated with the dataset.

<img src='https://courses.spatialthoughts.com/images/python_dataviz/xarray_terminology.png' width=800/>

A Dataset consists of one or more `xarray.DataArray` object. This is the main object that consists of a single variable with dimension names, coordinates and attributes. You can access each variable using `dataset.variable_name` syntax.

Let's see the `time_bnds` variable. This contains a 2d array which has both a starting and ending time for each one averaging period.


```python
ds.time_bnds
```

The main variable of interest is = `tempanomaly` - containing the grid of temperature anomaly values at different times. Let's select that variable and store it as `da`.


```python
da = ds.tempanomaly
da
```

## Selecting Data

XArray provides a very powerful way to select subsets of data, using similar framework as Pandas. Similar to Panda's `loc` and `iloc` methods, XArray provides `sel` and `isel` methods. Since DataArray dimensions have names, these methods allow you to specify which dimension to query.

Let's select the temperature anomany values for the last time step. Since we know the index (-1) of the datam we can use `isel` method.


```python
da.isel(time=-1)
```

We can also specify a value to query using the `sel()` method.


```python
da.sel(time='2021-12-15')
```

We can specify multiple dimensions to query for a subset. Let's extract the temperature anomaly at `lat=49`, `lon=-123` and `time='2021-06-15'`. This region experienced abnormally high temperatures in June 2021.


```python
da.sel(lat=49, lon=-123, time='2021-06-15')
```

The `sel()` method also support nearest neighbor lookups. This is useful when you do not know the exact label of the dimension, but want to find the closest one. 

> Tip: You can use `interp()` instead of `sel()` to interpolate the value instead of closest lookup.


```python
da.sel(lat=28.6, lon=77.2, time='2021-05-01', method='nearest')
```

You can call `.values` on a DataArray to get an array of the values.


```python
selected = da.sel(lat=28.6, lon=77.2, time='2021-05-01', method='nearest')
print(selected.values)
```

The `sel()` method also allows specifying range of values using Python's built-in `slice()` function. The code below will select all observationss in the year 2021.


```python
da.sel(time=slice('2021-01-01', '2021-12-31'))
```

## Masking and Subsetting Data

XArray has a [`where()`](https://docs.xarray.dev/en/stable/generated/xarray.DataArray.where.html) function that allows you to extract a subset of the array. The code block below extracts the anomaly at a specific Lat/Lon. We then use the `.where()` function to select items that have a positive anomaly.



```python
selected = da.sel(lat=28.6, lon=77.2, method='nearest')
selected
```

We can use `drop=True` to remove all items where the condition did not match and create a subset of the data.


```python
positive = selected.where(selected > 0, drop=True)
positive
```

## Aggregating Data

A very-powerful feature of XArray is the ability to easily aggregate data across dimensions - making it ideal for many remote sensing analysis. Let's calculate the average temperature anomany for the year 2021.

We first select the subset for year 2021 and apply the `.mean()` aggregation across the `time` dimension.


```python
subset2021 = da.sel(time=slice('2021-01-01', '2021-12-31'))
subset2021.mean(dim='time')
```

XArray has many features easily work with time-series data such as this. We can use temporal components to aggregate the data across time. Here we take our monthly time-series of anomalies and aggregate it to a yearly time-series using the `groupby()` method.

Reference: [Resampling and grouped operations](https://docs.xarray.dev/en/stable/user-guide/time-series.html#resampling-and-grouped-operations)


```python
yearly = da.groupby('time.year').mean(dim='time')
yearly
```

## Exercise

Can you find out when did the highest temperature anomaly occured at a specific location?

Replace the `lat` and `lon` in the following code with your chosen location. You will see the resulting `max_anomaly` DataArray with the anomaly value along with lat, lon and time coordinates.  Extract the `time` coordinate of the resulting array and print the time when the maximum anomaly occured.


```python
selected = da.sel(lat=28.6, lon=77.2, method='nearest')
max_anomaly = selected.where(selected==selected.max(), drop=True)
max_anomaly
```
