### Overview

We extract a per-field, per-date NDVI time series for the field boundaries sampled in the first notebook, restricted to the grid cells selected in the second notebook. Because building an NDVI cube over the full extent at full resolution for a whole year is expensive, we process one grid tile at a time - each tile bounds a small enough window that only the pixels actually needed for its fields get read and computed.

### Overview of the Task

We build a single lazy, Dask-backed NDVI data cube over the whole grid extent. We then loop over each grid tile: find the fields within it, clip the cube down further to just those fields' own bounds, and use `xvec` with `exactextract` to compute the mean NDVI and a count of valid pixels for each field on each date. We test this on a single tile before running the full computation and merging the results into one DataFrame.

### Setup

Determine our runtime environment and connect to Google Drive if needed.


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
    output_folder = 'data'

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
  !pip install pystac-client odc-stac rioxarray dask['distributed'] \
      xvec exactextract jupyter-server-proxy botocore
```

Import all required libraries.


```python
import exactextract
import geopandas as gpd
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pystac_client
import rioxarray as rxr
import xarray as xr
import xvec
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

### Load Grid and Field Boundaries

Load the grid and field boundaries saved by the previous two notebooks.


```python
grid_filepath = os.path.join(data_folder, 'field_tiling_grid.gpkg')
if not os.path.exists(grid_filepath):
    print(f'Grid file not found at {grid_filepath}.',
          'Using default grid.')
    grid_filepath = (
        'https://storage.googleapis.com/spatialthoughts-public-data'
        '/python-remote-sensing/field_tiling_grid.gpkg')

grid_gdf = gpd.read_file(grid_filepath)

fields_filepath = os.path.join(data_folder, 'field_boundaries_with_tile_id.gpkg')
if not os.path.exists(fields_filepath):
    print(f'Field boundaries file not found at {fields_filepath}.',
          'Using default field boundaries.')
    fields_filepath = (
        'https://storage.googleapis.com/spatialthoughts-public-data'
        '/python-remote-sensing/field_boundaries_with_tile_id.gpkg')

fields_gdf = gpd.read_file(fields_filepath)

print(f'{len(grid_gdf)} grid cells, {len(fields_gdf)} fields')
```

### Build a Lazy NDVI Data Cube

We build a single Dask-backed NDVI cube over the extent of the entire grid. We only need the `red` and `nir` bands to compute NDVI, plus `scl` for cloud masking.

Use the grid's bounding box to limit the search and load to the area we actually need.


```python
year = 2025
bbox = list(grid_gdf.total_bounds)
```

Search Element84's Earth Search STAC catalog for Sentinel-2 scenes intersecting the grid, for the selected year.


```python
catalog = pystac_client.Client.open(
    'https://earth-search.aws.element84.com/v1')

# Configure settings for reading from Earth Search STAC
configure_s3_access(
    aws_unsigned=True,
)

search = catalog.search(
    collections=['sentinel-2-c1-l2a'],
    bbox=bbox,
    datetime=f'{year}',
    query={
        'eo:cloud_cover': {'lt': 30},
    },
)
items = search.item_collection()
len(items)
```

Load the matching images as a lazy XArray Dataset. Passing `bbox` here too ensures we only read the pixels within the grid extent, not the full Sentinel-2 tiles.


```python
ds = load(
    items,
    bands=['red', 'nir', 'scl'],
    resolution=10,
    crs='utm',
    bbox=bbox,
    chunks={'x': 1024, 'y': 1024},  # Explicitly define chunk sizes
    groupby='solar_day',
    preserve_original_order=True,
)
ds
```

The Sentinel-2 scenes come with NoData value of 0. So we set the correct NoData value before further processing.


```python
# Mask nodata values
ds = ds.where(ds != 0)
```

Apply scale and offset to the spectral bands (not to `scl`, which is a classification band).


```python
scale = 0.0001
offset = -0.1
data_bands = [band for band in ds.data_vars if band != 'scl']
for band in data_bands:
    ds[band] = ds[band] * scale + offset
```

Mask cloud, cloud shadow and cirrus pixels using the Scene Classification Layer (`scl`).


```python
ds = ds[data_bands].where(~ds.scl.isin([3, 8, 9, 10]))
```

Compute NDVI. A pixel where `nir + red` is exactly zero produces `inf`, which silently poisons any mean computed over it later - we guard against this and also clip to NDVI's mathematically valid range of -1 to 1.


```python
red = ds['red']
nir = ds['nir']

ndvi = (nir - red) / (nir + red)
ndvi = ndvi.where(np.isfinite(ndvi))  # guard against divide-by-zero producing inf
ndvi = ndvi.clip(-1, 1)               # enforce the valid NDVI range

ndvi_cube = ndvi
ndvi_cube
```

### Extract NDVI Time Series per Grid Tile

For each grid tile, we select the fields already assigned to it (via the `tile_id` column from the previous notebook), clip the NDVI cube down from the tile's 10 km box to just those fields' own bounds, and use [`xvec.zonal_stats`](https://xvec.readthedocs.io/en/stable/generated/xvec.ZonalAccessor.zonal_stats.html) with the `exactextract` backend to compute the mean NDVI and a count of valid pixels per field per date. The pixel count lets us later identify dates where a field was mostly cloud-masked.


```python
def process_tile(tile, fields_gdf, ndvi_cube):
    fields_in_tile = fields_gdf[fields_gdf['tile_id'] == tile['tile_id']]
    if fields_in_tile.empty:
        return None

    # Clip to the fields' bounds, so we don't process pixels
    # the tile contains but no field touches.
    fields_bounds = fields_in_tile.to_crs(ndvi_cube.rio.crs).total_bounds
    tile_cube = ndvi_cube.rio.clip_box(*fields_bounds).compute()

    fields_reprojected = fields_in_tile.to_crs(tile_cube.rio.crs)
    aggregated = tile_cube.xvec.zonal_stats(
        fields_reprojected.geometry,
        x_coords='x',
        y_coords='y',
        stats=['mean', 'count'],
        method='exactextract')
    aggregated['field_id'] = ('geometry', fields_reprojected['field_id'].values)
    aggregated = aggregated.assign_coords({'field_id': aggregated['field_id']})

    tile_df = aggregated.to_dataframe(name='ndvi').reset_index()
    tile_df = tile_df.pivot(
        index=['field_id', 'time'], columns='zonal_statistics', values='ndvi'
    ).reset_index()
    tile_df = tile_df.rename(columns={'mean': 'ndvi_mean', 'count': 'pixel_count'})
    tile_df['tile_id'] = tile['tile_id']
    return tile_df
```

### Test on a Single Tile

Before running the full computation across every tile, test the function on one tile and inspect the result.


```python
test_tile = grid_gdf.iloc[0]
test_result = process_tile(test_tile, fields_gdf, ndvi_cube)
test_result
```

Plot the NDVI time series for the fields in this test tile.


```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(8, 4)

for field_id, group in test_result.groupby('field_id'):
    ax.plot(group['time'], group['ndvi_mean'], marker='o', markersize=3, label=f'field {field_id}')

ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
ax.set_ylabel('Mean NDVI')
ax.set_title(f"NDVI Time Series - {test_tile['tile_id']}")
ax.legend(fontsize=8)
fig.autofmt_xdate()
plt.show()
```


    
![](python-remote-sensing-output/projects/ndvi_time_series/03_extract_ndvi_time_series_files/03_extract_ndvi_time_series_34_0.png)
    


### Full Computation: Process All Tiles

Loop over every grid tile, skipping any with no fields, and merge the per-tile results into a single DataFrame.


```python
%%time
results = []
for _, tile in grid_gdf.iterrows():
    tile_df = process_tile(tile, fields_gdf, ndvi_cube)
    if tile_df is None:
        print(f"{tile['tile_id']}: skipped (no fields)")
        continue
    print(f"{tile['tile_id']}: {tile_df['field_id'].nunique()} fields")
    results.append(tile_df)

ndvi_timeseries = pd.concat(results, ignore_index=True)
print(f'{len(ndvi_timeseries)} field-date records across '
      f'{ndvi_timeseries["field_id"].nunique()} fields')
```

### Post-Processing

Before saving, we clean up the raw tall table: we drop observations where a field was only partially covered by valid pixels (so its NDVI isn't representative of the whole field), and reshape the result into a wide table with one row per field and one column per date.

A field's pixel count varies by date because of cloud masking - the highest count observed for a field represents its full, unmasked pixel footprint. We drop any date where the count falls below that maximum, since a partial-pixel NDVI mean isn't representative of the whole field.


```python
full_pixel_count = ndvi_timeseries.groupby('field_id')['pixel_count'].transform('max')
ndvi_filtered = ndvi_timeseries[ndvi_timeseries['pixel_count'] >= full_pixel_count].copy()
print(f'Kept {len(ndvi_filtered)} of {len(ndvi_timeseries)} field-date records with full pixel coverage')
```

Reshape the filtered table from tall (one row per field per date) to wide (one row per field, one column per date).


```python
ndvi_wide = ndvi_filtered.pivot(index='field_id', columns='time', values='ndvi_mean')
ndvi_wide.columns = [pd.Timestamp(c).strftime('%Y-%m-%d') for c in ndvi_wide.columns]
ndvi_wide = ndvi_wide.reset_index()
ndvi_wide
```

### Save the Results

Save the merged NDVI time series to the output folder, which points to Google Drive when running on Colab.


```python
output_filename = 'ndvi_timeseries.csv'
output_path = os.path.join(output_folder, output_filename)
ndvi_wide.to_csv(output_path, index=False)
print(f'Saved to {output_path}')
```
