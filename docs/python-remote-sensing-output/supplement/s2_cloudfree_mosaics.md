This notebook shows how to access, process and save a large subset of the Sentinel 2 Cloud Free Temporal Mosaics provided by Earth Genome. The workflow involves accessing the annual cloud-free composites, stacking and scaling the required bands, tiling the region and saving each tile as a Cloud Optimized GeoTIFF (COG) in a remote Google Cloud Storage (GCS) bucket.

![](https://storage.googleapis.com/spatialthoughts-public-data/sentinel-2/cloud-free-mosaics/preview.png)


#### Setup and Data Download

The following blocks of code will install the required packages and download the datasets to your Colab environment.


```python
%%capture
if 'google.colab' in str(get_ipython()):
    !pip install pystac-client odc-stac rioxarray dask['distributed'] \
     jupyter-server-proxy
```


```python
import dask
import duckdb
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pystac_client
import rioxarray as rxr
import tempfile
import xarray as xr
from datetime import datetime
from odc import stac
from osgeo import gdal
from shapely.geometry import box
```


```python
data_folder = 'data'
output_folder = 'output'

if not os.path.exists(data_folder):
    os.mkdir(data_folder)
if not os.path.exists(output_folder):
    os.mkdir(output_folder)
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

#### Select a Region of Interest

We use the [FieldMaps](https://fieldmaps.io/data/) GeoParquet file to select a large state in India.


```python
parquet_url = 'https://data.fieldmaps.io/edge-matched/open/intl/adm1_polygons.parquet'
con = duckdb.connect()
con.install_extension('spatial')
con.load_extension('spatial')

```


```python
country = 'IND'
adm1_name = 'Karnātaka'

query = f'''
SELECT adm1_name, adm1_id, ST_AsText(geometry) AS geometry
FROM read_parquet('{parquet_url}')
WHERE
  adm0_src = '{country}' and
  adm1_name = '{adm1_name}'
'''

admin1_df = con.sql(query).df()
admin1_gdf = gpd.GeoDataFrame(
    admin1_df, geometry=gpd.GeoSeries.from_wkt(admin1_df.geometry), crs='EPSG:4326'
)
```


```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(5,5)

admin1_gdf.plot(
    ax=ax,
    facecolor='none',
    edgecolor='#969696')
ax.set_axis_off()
plt.show()
```


```python
geometry = admin1_gdf.geometry
```

### Earth Genome STAC

Earth Genome provides ready-to-use annual and semi-annual Sentinel-2 mosaics created to L2A scenes. We can use the [Earth Genome STAC API Catalog](https://browser.stac.earthgenome.org/) to query for the matching tiles for our year and region of interest.


```python
catalog = pystac_client.Client.open(
    'https://stac.earthgenome.org/')
```

We define a location and time of interest to get some satellite imagery.


```python
bbox = geometry.total_bounds
year = 2023
```

Search the catalog for matching tiles for the selected year.


```python
search = catalog.search(
    collections=['sentinel2-temporal-mosaics'],
    bbox=bbox,
    datetime=f'{year}'
)
items = search.item_collection()

# The annual mosaics have a date range that goes from
# 1-Jan-{year} to 1-jan-{year+1}
# This matches items for 2 years in the above query
# We filter these using the start_datetime and end_datetime
# properties in the item metadata

# Create a start and end datetime strings
start_date = datetime(year, 1, 1).strftime('%Y-%m-%dT%H:%M:%SZ')
end_date = datetime(year + 1, 1, 1).strftime('%Y-%m-%dT%H:%M:%SZ')

items_filtered = [
    item for item in items
    if item.properties['start_datetime'] == start_date
    and item.properties['end_datetime'] == end_date
]
```

### Load STAC Images to XArray

Load the matching images as a XArray Dataset.


```python
ds = stac.load(
    items_filtered,
    bands=['B04', 'B03', 'B02'],
    resolution=10,
    crs='utm',
    chunks={'x': 1000, 'y':1000},  # <-- use Dask
    groupby='solar_day',
    preserve_original_order=True
)
ds
```

Since all the tiles are for the same year, we can remove the time dimension.


```python
scene = ds.isel(time=0)
scene
```

Each band of the scene is saved with integer pixel values (data type `uint16`). This help save the storage cost as storing the reflectance values as floating point numbers (data type `float64`) requires more storage. We need to convert the raw pixel values to reflectances by applying the *scale* values. The scale `0.0001`.


```python
scale = 0.0001
scene = scene*scale
```

Convert to a DataArray.


```python
scene_da = scene.to_array('band')
scene_da
```

#### Create a Grid

Instead of writing a single large file, we can tile the outputs into smaller tiles for ease of access.

We start by creating a grid and specifying the size of each tile in pixels.


```python
TILE_SIZE = 10000
```

Reproject the geometry to match the CRS of the DataArray.


```python
gdf_proj = admin1_gdf.to_crs(scene_da.rio.crs)
geometry_crs = gdf_proj.geometry
```


```python
left, bottom, right, top = scene_da.rio.bounds()
minx, miny, maxx, maxy = gdf_proj.total_bounds
res_x = (right - left) / scene_da.sizes['x']
res_y = (top - bottom) / scene_da.sizes['y']
TILE_SIZE_M = TILE_SIZE * res_x  # e.g. 10000 * 10.0 = 100000m

xs = np.arange(minx, maxx, TILE_SIZE_M)
ys = np.arange(miny, maxy, TILE_SIZE_M)

tiles = [
    box(x, y, x + TILE_SIZE_M, y + TILE_SIZE_M)
    for y in sorted(ys, reverse=True)
    for x in xs
]

grid = gpd.GeoDataFrame(geometry=tiles, crs=scene_da.rio.crs)
grid = grid[grid.intersects(gdf_proj.union_all())].reset_index(drop=True)
grid['tile_id'] = [
    f'tile_{(i // len(ys)) + 1:02d}_{(i % len(ys)) + 1:02d}'
    for i in grid.index
]
print(f'{len(grid)} tiles intersect geometry')
```


```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(5,5)

gdf_proj.plot(
    ax=ax,
    facecolor='none',
    edgecolor='#969696')

grid.plot(
    ax=ax,
    facecolor='none',
    edgecolor='blue',
    linewidth=0.5)

ax.set_axis_off()
plt.show()
```

#### Save the Tiles

We can save the tiles to a Google Cloud Storage (GCS) bucket. You may also just save them locally if you wish.


```python
# Specify your project ID and Bucket name
project_id = 'python-363014'
bucket_name = 'spatialthoughts-public-data'
sub_folder = 'sentinel-2/cloud-free-mosaics'
```


```python
if 'google.colab' in str(get_ipython()):
  from google.colab import auth
  from google.cloud import storage

  auth.authenticate_user()
  client = storage.Client(project=project_id)
  bucket = client.get_bucket(bucket_name)

  print(f'Google Cloud Storage client initialized for project: {project_id}')
  print(f'Bucket {bucket_name} selected.')
```

We now fetch the data for each grid tile, clip it and save it as a COG.


```python
geometry_crs = gdf_proj.geometry

gcs_tile_paths = []

for _, row in grid.iterrows():
    tile_id = row['tile_id']
    print(f'Processing {tile_id}')
    tile_bounds = row.geometry.bounds  # (minx, miny, maxx, maxy)

    # Construct the GCS blob path relative to the bucket
    gcs_blob_path = f'{sub_folder}/{tile_id}.tif'
    gcs_tile_paths.append(f'/vsigs/{bucket.name}/{gcs_blob_path}')

    if bucket.blob(gcs_blob_path).exists():
        print(f'Tile {tile_id} already exists in GCS. Skipping.')
        continue

    # Pull only this tile into RAM
    tile = scene_da.rio.clip_box(*tile_bounds).compute()

    try:
        tile_clipped = tile.rio.clip(geometry_crs)
    except Exception:
        continue

    # Save to a temporary local file first
    with tempfile.NamedTemporaryFile(suffix='.tif', delete=False) as tmp_file:
        local_tile_path = tmp_file.name

    tile_clipped.rio.to_raster(local_tile_path, driver='COG')
    blob = bucket.blob(gcs_blob_path)

    print(f'Uploading {local_tile_path} to gs://{bucket.name}/{gcs_blob_path}')
    blob.upload_from_filename(local_tile_path)

    os.remove(local_tile_path) # Clean up the local temporary file
    print(f'Successfully uploaded {tile_id}.tif')

print('All tiles processed and uploaded to GCS.')
```

To enable viewing and processing all the tiles as a single mosaic, we create a Virtual Dataset (VRT) file. This VRT references all the individual tiles and you can load this VRT file using QGIS or rioxarray which will load as the merged mosaic.


```python
with tempfile.NamedTemporaryFile(suffix='.vrt', delete=False) as tmp_file:
    local_vrt_path = tmp_file.name

vrt = gdal.BuildVRT(local_vrt_path, gcs_tile_paths)
vrt.FlushCache()
vrt = None

vrt_blob_path = f'{sub_folder}/mosaic.vrt'
bucket.blob(vrt_blob_path).upload_from_filename(local_vrt_path)
os.remove(local_vrt_path)
print(f'VRT uploaded to gs://{bucket.name}/{vrt_blob_path}')
```
