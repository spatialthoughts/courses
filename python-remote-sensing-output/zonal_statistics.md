### Overview

Zonal Statistics is used to summarises the values of a raster dataset within the zones of a vector dataset. Here we select all Admin1 units of a country and calculate a sum of nighttime light pixel intensities over multiple years. This is a large computation that is enabled by cloud-hosted NightTime Lights data in the Cloud-Optimized GeoTIFF (COG) format and parallel computing on a local dask cluster.


### Setup and Data Download

The following blocks of code will install the required packages and download the datasets to your Colab environment.


```python
%%capture
if 'google.colab' in str(get_ipython()):
    !apt install libspatialindex-dev
    !pip install fiona shapely pyproj rtree
    !pip install geopandas
    !pip install rioxarray
    !pip install regionmask
```


```python
import os
import glob
import pandas as pd
import geopandas as gpd
import numpy as np
import xarray as xr
import rioxarray as rxr
import matplotlib.pyplot as plt
from datetime import datetime
import dask
import regionmask
```


```python
import warnings
import rasterio
warnings.filterwarnings("ignore", category=rasterio.RasterioDeprecationWarning)
```


```python
from dask.distributed import Client, progress
client = Client()  # set up local cluster on the machine
client
```


```python
dask.config.set({"array.slicing.split_large_chunks": False})
dask.config.set({'array.chunk-size': '32MiB'})
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

admin1_zipfile = 'ne_10m_admin_1_states_provinces.zip'
admin1_url = 'https://naciscdn.org/naturalearth/10m/cultural/'

download(admin1_url + admin1_zipfile)
```

### Data Pre-Processing

First we will read the GDL shapefile and filter to a country.
The 'adm1_code' column contains a unique id for all the counties present in the state, but it is of `object` type. We need to convert it to `int` type to be used in xarray.



```python
country_code = 'LK'
admin1_file_path = os.path.join(data_folder, admin1_zipfile)

admin1_df = gpd.read_file(admin1_file_path)

zones = admin1_df[admin1_df['iso_a2'] == country_code][['adm1_code', 'name', 'iso_a2', 'geometry']].copy()
zones['id'] = zones.reset_index().index + 1
zones
```


```python
bbox = zones.total_bounds
bbox
```

Next we read the NTL files and create an XArray object.

These files were download from [Harvard Dataverse](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/YGIVCD) and converted to Cloud-Optimized GeoTIFFs using GDAL.

 Example command `gdalwarp -of COG -co COMPRESS=DEFLATE -co PREDICTOR=2 -co NUM_THREADS=ALL_CPUS 2021_HasMask/LongNTL_2021.tif 2021.tif -te -180 -90 180 90 -dstnodata 0`
  
The resulting files are now hosted on a Google Cloud Storage bucket.


```python
start_year = 2015
end_year = 2020
```


```python

ntl_folder = 'https://storage.googleapis.com/spatialthoughts-public-data/ntl/npp_viirs_ntl'

da_list = []

for year in range(start_year, end_year + 1):
  cog_url = f'{ntl_folder}/{year}.tif'
  da = rxr.open_rasterio(
      cog_url,
      chunks=True).rio.clip_box(*bbox)
  dt = pd.to_datetime(year, format='%Y')
  da = da.assign_coords(time = dt)
  da = da.expand_dims(dim="time")
  da_list.append(da)
```


```python
ntl_datacube = xr.concat(da_list, dim='time').chunk('auto')
ntl_datacube
```


```python
ntl_datacube = ntl_datacube.sel(band=1, drop=True)
```

### Zonal Stats

Now we will extract the sum of the raster pixel values for every admin1 region in the selected countrey.

First, we need to convert the GeoDataFrame to a XArray Dataset. We will be using the `regionmask` module for that. It takes geodataframe, it's unique value as integer and converts the geodataframe into  a `xarray dataset` having dimension and coordinates same as of given input xarray dataset



```python
# Create mask of multiple regions from shapefile
mask = regionmask.mask_3D_geopandas(
        zones,
        ntl_datacube.x,
        ntl_datacube.y,
        drop=True,
        numbers="id",
        overlap=True
    )
```


```python
ntl_datacube = ntl_datacube.where(mask).chunk('auto')
ntl_datacube
```


```python
grouped = ntl_datacube.groupby('time').sum(['x','y'])
grouped
```


```python
%time grouped = grouped.compute()
```


```python
stats = grouped.drop('spatial_ref').to_dataframe('sum').reset_index()
stats
```


```python
stats['year'] = stats.time.dt.year
stats = stats.rename(columns={'region': 'id'})
stats
```


```python
results = zones.merge(stats, on='id')
results
```

Finally, we save the result to disk.


```python
output = results[['adm1_code', 'name', 'iso_a2', 'year', 'sum']]
output
```


```python
output_file = 'output.csv'
output_path = os.path.join(output_folder, output_file)

output.to_csv(output_path, index=False)
print('Successfully written output file at {}'.format(output_path))
```

### Exercise


Change the code to calculate the Zonal Statistics for all admin1 units in your chosen country.
