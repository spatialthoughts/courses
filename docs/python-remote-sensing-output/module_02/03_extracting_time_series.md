### Overview

We are now ready to scale our analysis. Having learned how to calculate spectral indices and do cloud masking for a single scene - we can easily apply these operations to the entire data-cube and extract the results at at one or more locations. Cloud-optimized data formats and Dask ensure that we fetch and process only a small amount of data that is required to compute the results at the pixels of interest.

In this section, we will get all Sentinel-2 scenes collected over our region of interest, apply a cloud-mask, calculate NDVI and extract a time-series of NDVI at a single location. We will also use XArray's built-in time-series processing functions to interpolat and smooth the results.

### Setup

Determine our runtime environment.


```python
import os

if 'COLAB_RELEASE_TAG' in os.environ:
    environment = 'colab'
    if os.environ.get('VERTEX_PRODUCT') == 'COLAB_ENTERPRISE':
        environment = 'colab_enterprise'
else:
    environment = 'local'

# Set to True to use Google Drive for data storage in Colab
use_google_drive = True

# Google Drive is available only in 'colab' environment
if environment == 'colab' and use_google_drive:
    from google.colab import drive
    drive.mount('/content/drive')
    drive_folder_root = 'MyDrive'
    drive_data_folder = 'python-remote-sensing'
    drive_folder_path = os.path.join('/content/drive', drive_folder_root, drive_data_folder)
    data_folder = drive_folder_path
    output_folder = drive_folder_path
else:
    data_folder = 'data'
    output_folder = 'output'

if not os.path.exists(data_folder):
    os.mkdir(data_folder)
if not os.path.exists(output_folder):
    os.mkdir(output_folder)

print(f'Environment: {environment}')
print(f'Data folder: {data_folder}')
print(f'Output folder: {output_folder}')
```

If we are on Google Colab, install the required packages. Local runtimes are expected to have the packages already installed.


```python
%%capture
if environment in ['colab', 'colab_enterprise']:
    !pip install pystac-client odc-stac rioxarray \
        dask['distributed'] jupyter-server-proxy xrscipy
```

Import all required libraries. Make sure to import everything at the beginning as certain Xarray extensions are activated on import and registers certain accesors, like `.rio` and `.odc` for Xarray objects.


```python
import dask
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import os
import pyproj
import pystac_client
import rioxarray as rxr
import xarray as xr
import xrscipy.signal as xrs
from odc.stac import configure_s3_access, load
```

Setup a local Dask cluster. This distributes the computation across multiple workers on your computer.


```python
from dask.distributed import Client
client = Client()  # set up local cluster on the machine
client
```

If you are running this notebook in Colab, you will need to create and use a proxy URL to see the dashboard running on the local server.


```python
if environment == 'colab':
    from google.colab import output
    port_to_expose = 8787  # This is the default port for Dask dashboard
    print(output.eval_js(f'google.colab.kernel.proxyPort({port_to_expose})'))
```

### Get Satellite Imagery using STAC API

We define a location and time of interest to get some satellite imagery.


```python
latitude = 27.163
longitude = 82.608
year = 2023
```

Let's use Element84 search endpoint to look for items from the sentinel-2-l2a collection on AWS and load the matching images as a XArray Dataset.


```python
# Define a GeoJSON geometry
geometry = {
    'type': 'Point',
    'coordinates': [longitude, latitude]
}

# Query the STAC Catalog
catalog = pystac_client.Client.open(
    'https://earth-search.aws.element84.com/v1')

search = catalog.search(
    collections=['sentinel-2-c1-l2a'],
    intersects=geometry,
    datetime=f'{year}',
    query={
        'eo:cloud_cover': {'lt': 30},
    }
)
items = search.item_collection()

# Load to XArray
ds = load(
    items,
    bands=['red', 'green', 'blue', 'nir', 'scl'],
    resolution=10,
    crs='utm',
    chunks={'x': 1024, 'y': 1024},  # Explicitly define chunk sizes
    groupby='solar_day',
    preserve_original_order=True
)
ds
```

### Processing Data

We have a data cube of multiple scenes collected through the year. As XArray supports vectorized operations, we can work with the entire DataSet the same way we would process a single scene.

The Sentinel-2 scenes come with NoData value of 0. So we set the correct NoData value before further processing.


```python
# Mask nodata values
ds = ds.where(ds != 0)
```

Apply scale and offset to all spectral bands


```python
# Apply scale/offset
scale = 0.0001
offset = -0.1
# Select spectral bands (all except 'scl')
data_bands = [band for band in ds.data_vars if band != 'scl']
for band in data_bands:
  ds[band] = ds[band] * scale + offset
```

Apply the cloud mask


```python
ds = ds[data_bands].where(~ds.scl.isin([3,8,9,10]))
ds
```

Calculate NDVI and add it as a data variable.


```python
red = ds['red']
nir = ds['nir']

ndvi = (nir - red)/(nir + red)
ds['ndvi'] = ndvi
ds
```

### Extracting Time-Series

We have a dataset with cloud-masked NDVI values at each pixel of each scene. Remember that none of these values are computed yet. Dask has a graph of all the operations that would be required to calculate the results.

We can now query this results for values at our chosen location. Once we run `compute()` - Dask will fetch the required tiles from the source data and run the operations to give us the results.

Our location coordinates are in EPSG:4326 Lat/Lon. Convert it to the CRS of the dataset so we can query it.


```python
crs = ds.rio.crs
transformer = pyproj.Transformer.from_crs('EPSG:4326', crs, always_xy=True)
x, y = transformer.transform(longitude, latitude)
x,y
```

Query NDVI values at the coordinates.


```python
time_series = ds.ndvi \
  .interp(y=y, x=x, method='nearest')
time_series
```


```python
# As we are proceesing the time-series,
# it needs to be in a single chunk along the time dimension
time_series = time_series.chunk(dict(time=-1))
time_series
```

Run the calculation and load the results into memory.


```python
%%time
time_series = time_series.compute()
```

See the computed values.


```python
time_series
```

Plot the time-series.


```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(15, 7)

time_series.plot.line(
    ax=ax, x='time',
    marker='o', color='#238b45',
    linestyle='-', linewidth=1, markersize=4)

# Format the x-axis to display dates as YYYY-MM
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))

ax.set_title('NDVI Time-Series')
plt.show()
```

### Interpolate and Smooth the time-series

We use XArray's excellent time-series processing functionality to smooth the time-series and remove noise.

First, we resample the time-series to have a value every 5-days and fill the missing values with linear interpolation.


```python
time_series_resampled = time_series\
  .resample(time='5d').mean(dim='time')
time_series_interpolated = time_series_resampled \
  .interpolate_na('time', use_coordinate=False) \
  .bfill('time').ffill('time')
```

We now have a gap-filled and regular time-series.


```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(15, 7)
time_series.plot.line(
    ax=ax, x='time',
    marker='^', color='#66c2a4',
    linestyle='--', linewidth=1, markersize=2)
time_series_interpolated.plot.line(
    ax=ax, x='time',
    marker='o', color='#238b45',
    linestyle='-', linewidth=1, markersize=4)

# Format the x-axis to display dates as YYYY-MM
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))

ax.set_title('Original vs. Gap-Filled NDVI Time-Series')

plt.show()

```

But we still have a lot of noise. This is caused by atmospheric variability and cloud contamination. We can apply a moving-window smoothing to remove outliers.


```python
time_series_smoothed = time_series_interpolated \
  .rolling(time=3, min_periods=1, center=True).mean()
time_series_smoothed
```


```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(15, 7)
time_series.plot.line(
    ax=ax, x='time',
    marker='^', color='#66c2a4',
    linestyle='--', linewidth=1, markersize=2)
time_series_smoothed.plot.line(
    ax=ax, x='time',
    marker='o', color='#238b45',
    linestyle='-', linewidth=1, markersize=4)

# Format the x-axis to display dates as YYYY-MM
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))

ax.set_title('Original vs. Smoothed NDVI Time-Series')

plt.show()

```


    
![](python-remote-sensing-output/module_02/03_extracting_time_series_files/03_extracting_time_series_46_0.png)
    


### Save the Time-Series.

Convert the extracted time-series to a Pandas DataFrame.



```python
df = time_series_smoothed.to_pandas().reset_index()
df.head()

```

Save the DataFrame as a CSV file.


```python
output_filename = 'ndvi_time_series.csv'
output_filepath = os.path.join(output_folder, output_filename)
df.to_csv(output_filepath, index=False)
```

Close the dask client. This presents multiple clients being instantiated when running different notebooks on the same machine. This is not required on Colab but a good practice when you are running it on a local machine. Uncomment and run to shutdown the dask cluster.


```python
#client.shutdown()
```

### Exercise

The Savitzky–Golay (SG) filter is a widely used smoothing technique for time-series data. When applied to remote sensing data - particularly NDVI time-series - it helps recovers the true signal of vegetation change. [Learn more](https://www.sciencedirect.com/science/article/abs/pii/S003442570400080X).

[Scipy for Xarray (`xrscipy`)](https://xr-scipy.readthedocs.io/en/stable/index.html) package wraps the popular scipy package for Xarray and provides many useful time-series processing functions. The code snippet below uses [`xrscipy.signal.savgol_filter`](https://xr-scipy.readthedocs.io/en/1.0.0/generated/xrscipy.other.signal.savgol_filter.html) function to apply a Savitzky-Golay filter on our gap-filled NDVI time-series.

Try SG-Filter with different values of window_length and polyorder and plot the results on a chart.

* `window_length`: Number of data points included in a moving window to calculate the smoothed value. Typically values are odd integers between 5 and 15.
* `polyorder`: The degree (or complexity) of the mathematical polynomial used to fit the data within the window. Typically values are 2 (quadratic) or 3 (cubic).


```python
# Use the equally spaced interpolated time-series
time_series_interpolated = time_series_interpolated.compute()

# savgol_filter() requires integers as time index
# We save the original time index values and
# overwrite it with sequential integers
timestamps = time_series_interpolated.time
time_series_interpolated.coords['time'] = np.arange(len(timestamps))

# Apply the SG filter
window_length = 5 # Size of filter window
polyorder = 2 # Order of the polynomial

time_series_sg = xrs.savgol_filter(
    time_series_interpolated,
    window_length = window_length,
    polyorder = polyorder,
    mode='nearest',
    dim = 'time'
)

# Write back the original timestamps
time_series_interpolated.coords['time'] = timestamps
time_series_sg.coords['time'] = timestamps

time_series_sg
```
