### Extract a Temperature Time-Series

[TerraClimate](https://www.climatologylab.org/terraclimate.html) is long-term climatology dasaset that provides monthly-aggregated gridded data from 1950-present. It is hosted on a THREDDS Data Server (TDS) and served using the OPeNDAP (Open Data Access Protocol) protocol. XArray has built-in support to efficiently read and process OPeNDAP data where we can stream and process only the required pixels without downloading entire dataset.

Your task is to access the TerraClimate Monthly Maximum Temperature dataset and extract a time-series showing the temperatures at your chosen location from 1970-2025.

![](https://courses.spatialthoughts.com/images/python_remote_sensing/terraclimate.png)

Notes:

* Explore the [TerraClimate Catalog](http://thredds.northwestknowledge.net:8080/thredds/terraclimate_aggregated.html) on the THREDDS Data Server for all available datasets. This notebook providers code snippets below to show the access pattern.
* Use XArray's indexing methods to select the required subset from 1970-2025.

----

Install the `netCDF4` package for XArray to access NetCDF format data.


```python
%%capture
if 'google.colab' in str(get_ipython()):
    !pip install netCDF4
```


```python
import os
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
terraclimate_url = 'http://thredds.northwestknowledge.net:8080/thredds/dodsC/'
variable = 'tmax'
filename = f'agg_terraclimate_{variable}_1950_CurrentYear_GLOBE.nc'
remote_file_path = os.path.join(terraclimate_url, filename)
ds = xr.open_dataset(
    remote_file_path,
    chunks='auto',
    engine='netcdf4',
)
ds
```


```python
if 'google.colab' in str(get_ipython()):
    from google.colab import drive
    drive.mount('/content/drive')
```


```python
if 'google.colab' in str(get_ipython()):
    drive_folder_root = 'MyDrive'
    drive_data_folder = 'python-remote-sensing'
    drive_folder_path = os.path.join(
          '/content/drive', drive_folder_root, drive_data_folder)
    output_folder_path = drive_folder_path
    if not os.path.exists('/content/drive'):
        print("Google Drive is not mounted. Please run the cell above to mount your drive.")
    else:
        if not os.path.exists(output_folder_path):
            os.makedirs(output_folder_path)
else:
    output_folder_path = output_folder
```
