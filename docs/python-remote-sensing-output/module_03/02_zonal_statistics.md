### Overview
We will learn how to calculate zonal statistics — aggregating raster pixel values within vector polygon boundaries. Using the Global Human Settlement Layer (GHSL) population raster and US county boundaries, we compute the total population for each county in California. We use [`xvec`](https://xvec.readthedocs.io/en/stable/index.html) for the zonal aggregation and `dask` to handle the large raster without loading it all into memory at once.

### Setup and Data Download

The following blocks of code will install the required packages and download the datasets to your Colab environment.


```python
%%capture
if 'google.colab' in str(get_ipython()):
    !pip install odc-stac rioxarray dask['distributed'] xvec exactextract
```


```python
import dask
import os
import duckdb
import geopandas as gpd
import matplotlib.pyplot as plt
from odc.stac import stac_load
from odc.geo.geobox import GeoBox
from odc.geo.xr import xr_reproject
import rioxarray as rxr
import xarray as xr
import xvec
import exactextract

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

census_folder = 'https://www2.census.gov/geo/tiger/GENZ2021/shp/'
zones_file = 'cb_2021_us_county_500k.zip'

for file in files:
  download(census_folder + file)
```

Setup a local Dask cluster. This distributes the computation across multiple workers on your computer.


```python
from dask.distributed import Client
client = Client()  # set up local cluster on the machine
client
```

If you are running this notebook in Colab, you will need to create and use a proxy URL to see the dashboard running on the local server.


```python
if 'google.colab' in str(get_ipython()):
    from google.colab import output
    port_to_expose = 8787  # This is the default port for Dask dashboard
    print(output.eval_js(f'google.colab.kernel.proxyPort({port_to_expose})'))

```

### Load Polygons

First we will read the  Zipped counties shapefile and filter out the counties that are in `California` state.

The dataframe has a column  as `STATE_NAME` having names of states that can be used to filter the counties for *California*.


```python
zones_file_path = os.path.join(data_folder, zones_file)

zones_df = gpd.read_file(zones_file_path)
state_gdf  = zones_df[zones_df['STATE_NAME'] == 'California'].copy()

state_gdf.head()
```

### Load Raster Data

We load the [Global Human Settlement Layer (GHSL)](https://ghsl.jrc.ec.europa.eu/) population raster for 2025. The file is a Cloud Optimized GeoTIFF (COG) so we can read only the portion we need. We use `chunks='auto'` to load it lazily as a Dask array.


```python
raster_file_path = 'https://storage.googleapis.com/spatialthoughts-public-data/ghsl/GHS_POP_E2025_GLOBE_R2023A_54009_100_V1_0_cog.tif'
da = rxr.open_rasterio(raster_file_path, chunks='auto', mask_and_scale=True)
da
```

The raster has a single `band` dimension. We use `squeeze()` to drop it and work with a 2D array.


```python
pop_da = da.squeeze()
pop_da
```

### Calculate Zonal Statistics

Reproject the polygons to match the projection of the population raster.


```python
state_gdf_reprojected = state_gdf.to_crs(pop_da.rio.crs)
```

Clip the raster to the bounds of the zones. `clip_box` is window-read aware with COGs — it only fetches the tiles that overlap the bounding box, so the data stays lazy until you call .compute().


```python
bounds = state_gdf_reprojected.total_bounds  # (minx, miny, maxx, maxy)
pop_da_clipped = pop_da.rio.clip_box(*bounds)
pop_da_clipped
```

We will now use the [`xvec.zonal_stats()`](https://xvec.readthedocs.io/en/stable/zonal_stats.html) method to aggregates raster pixel values within each polygon.

Computing zonal stats efficiently requires rasterizing the vector data to the Xarray data structure first. XVec has support for several methods to rasterize the polygons. The preferred method is provided by the [`exactextract`](https://isciences.github.io/exactextract/) package - which calulates fast and accurate statistcs by determining the fraction of each pixel that is covered by the polygon. Read our post on [Understanding Pixel Weights in Zonal Statistics](https://spatialthoughts.com/2023/07/13/pixel-weights-zonal-stats/) to understand why this is an important considertation.

We request the `sum` statistic, which gives us total population per county. Running this cell triggers the dask computation on the cluster.



```python
%%time
aggregated = pop_da_clipped.xvec.zonal_stats(
    state_gdf_reprojected.geometry,
    x_coords='x',
    y_coords='y',
    stats=['sum'],
    method='exactextract'
)
```

The result is an [Vector Data Cube](https://xvec.readthedocs.io/en/stable/intro.html) - an XArray Dataset indexed by geometry.


```python
aggregated
```

At this point we only have the geometries from the original vector data. It will be useful to add some attribues from the original GeoDataFrame. As we have am XArray vector data cube, this is done by adding it as a coordinate variable. The cell below adds the `NAME` attribute with the county name.


```python
aggregated['name'] = ('geometry', state_gdf_reprojected['NAME'].values)
aggregated = aggregated.assign_coords({'name': aggregated['name']})
aggregated
```

Convert the XArray Dataset back to a GeoDataFrame for tabular manipulation and export.


```python
aggregated_gdf = aggregated.xvec.to_geodataframe(name='population_sum', geometry='geometry')
aggregated_gdf
```

 Reset the index to convert the multi-index into columns, and select and rename columns to prepare the output.



```python
output_gdf = aggregated_gdf.reset_index()
output_gdf = output_gdf.rename(columns={'NAME': 'name', 'population_sum': 'population'})
output_gdf = output_gdf[['name', 'population', 'geometry']]
output_gdf
```

Save the results as a GeoPackage file.


```python
# Define the output path
output_path = os.path.join(output_folder, 'california_counties_population.gpkg')

# Save the GeoDataFrame to a GeoPackage file
output_gdf.to_file(output_path, driver='GPKG')

```

### Exercise

[CHIRPS](https://www.chc.ucsb.edu/data/chirps3) - Climate Hazards Center InfraRed Precipitation with Station data - is gridded rainfall time-series data with coverage between 60°N to 60°S latitudes. The data is available aggregated over various time-periods.

The annual GeoTIFF files are available at https://data.chc.ucsb.edu/products/CHIRPS/v3.0/annual/global/tifs/.

Pick a year and calculate the average rainfall in each county in california.
