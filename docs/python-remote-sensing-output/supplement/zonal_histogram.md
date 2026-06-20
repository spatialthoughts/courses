### Overview

This notebook shows how to perform scalable calculation of landcover area using Zonal Statistics. We implement a Zonal Histogram operation using [`xvec.zonal_stats()`](https://xvec.readthedocs.io/en/stable/zonal_stats.html) function with the `frac`, `unique` and `count` statistics to get the pixel counts of each class within each polygon. Multiplied by the pixel count and pixel area, this gives the absolute area per class per polygon. This method does lazy dask-computation and scales to large regions.

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
  !pip install pystac-client odc-stac rioxarray dask[distributed] \
      jupyter-server-proxy planetary_computer xvec exactextract
```

Import all required libraries. Make sure to import everything at the beginning as certain Xarray extensions are activated on import and registers certain accessors, like `.rio` and `.odc` for Xarray objects.


```python
import exactextract
import geopandas as gpd
import odc.geo.xr
import os
import pandas as pd
import planetary_computer as pc
import pystac_client
import rioxarray as rxr
import xarray as xr
import xvec
from dask.distributed import Client
from odc import stac
from odc.geo.geobox import GeoBox
```

Setup a local Dask cluster. This distributes the computation across multiple workers on your computer.


```python
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

### Load Admin2 Polygons

Read the file containing the Admin2 boundaries exported in Module 1.


```python
admin2_filepath = os.path.join(data_folder, 'admin2.gpkg')

if not os.path.exists(admin2_filepath):
    print(f'Admin2 file not found at {admin2_filepath}. Using default Admin2 regions.')
    admin2_filepath = (
        'https://storage.googleapis.com/spatialthoughts-public-data'
        '/python-remote-sensing/admin2.gpkg'
    )
```

Read the Admin2 GeoPackage.


```python
admin2_gdf = gpd.read_file(admin2_filepath)
admin2_gdf
```

Extract the geometry.


```python
geometry = admin2_gdf.geometry.union_all()
```

### Get ESA WorldCover Data

Search the [Planetary Computer STAC API](https://planetarycomputer.microsoft.com/docs/quickstarts/reading-stac/) for ESA WorldCover 2021 tiles that intersect the Admin2 region.


```python
catalog = pystac_client.Client.open(
    'https://planetarycomputer.microsoft.com/api/stac/v1')

search = catalog.search(
    collections=['esa-worldcover'],
    intersects=admin2_gdf.geometry.union_all(),
    datetime='2021',
)
items = search.item_collection()
items
```

Each STAC item carries the class names, legend colors, and pixel values in its metadata. Extract them now so we can label the results later.


```python
class_list = items[0].assets['map'].extra_fields['classification:classes']
class_dict = {
    c['value']: {'description': c['description'], 'hex': c['color_hint']}
    for c in class_list
}
class_dict
```

Load the matching images as a XArray Dataset. Accessing data from Planetary Computer is free but requires getting a Shared Access Signature (SAS) token and sign the URLs. The planetary_computer Python package provides a simple mechanism for signing the URLs using sign() function.


```python
# Load to XArray
ds = stac.load(
    items,
    bbox=geometry.bounds, # <-- load data only for the bbox
    resolution=10,
    crs='utm',
    chunks={'x': 5000, 'y': 5000},  # <-- use Dask
    patch_url=pc.sign,
    groupby='solar_day',
    preserve_original_order=True
)
ds
```

The landcover classification data is in the map variable. Select it and remove the empty time dimension.


```python
map_data = ds['map'].squeeze()
map_data
```

### Calculate Per-Polygon Landcover Area

Reproject the Admin2 polygons to match the CRS of the raster. `xvec.zonal_stats()` requires both to share the same CRS.


```python
admin2_reprojected = admin2_gdf.to_crs(map_data.rio.crs)
```

Compute zonal statistics using [`xvec.zonal_stats()`](https://xvec.readthedocs.io/en/stable/zonal_stats.html) with the `exactextract` backend.

- `frac` — the weighted fraction of each polygon's area covered by each unique class value.
- `unique` - unique class values in the same order as `frac`.
- `count` — total weighted pixel count within the polygon.

This call triggers Dask computation.


```python
%%time
aggregated = map_data.xvec.zonal_stats(
    admin2_reproj.geometry,
    x_coords='x',
    y_coords='y',
    stats=['frac', 'unique', 'count'],
    method='exactextract'
)
aggregated
```

Add the `adm2_name` attribute as a coordinate so it is carried through to the GeoDataFrame.


```python
aggregated['adm2_name'] = ('geometry', admin2_reprojected['adm2_name'].values)
aggregated = aggregated.assign_coords({'adm2_name': aggregated['adm2_name']})
aggregated
```


```python
aggregated_df = aggregated.to_dataframe('values').reset_index()
aggregated_df
```

Convert to a GeoDataFrame and expand the `frac` dict column into one row per polygon per class. The `frac` values for each polygon sum to 1.0, so `frac[c] × count × pixel_area_m2` gives the area in m² for class `c`.


```python
pixel_area_m2 = 100.0  # 10 m × 10 m

pivoted = (
    aggregated_df.pivot(index=['geometry', 'adm2_name'],
                        columns='zonal_statistics', 
                        values='values')
    .rename_axis(None, axis=1)
    .reset_index()
)

exploded = pivoted.explode(['frac', 'unique'])
exploded['class_value'] = exploded['unique'].astype(int)
exploded = exploded[exploded['class_value'].isin(class_dict)].copy()
exploded['class_name'] = exploded['class_value'].map(
    {k: v['description'] for k, v in class_dict.items()})
exploded['area_km2'] = (
    exploded['frac'].astype(float) * exploded['count'].astype(float)
    * pixel_area_m2 / 1e6
)

all_class_names = [v['description'] for v in class_dict.values()]

# Convert to a wide table with one column per class, filling missing values with 0
wide = (
    exploded.pivot_table(index=['adm2_name', 'geometry'], 
                        columns='class_name', 
                        values='area_km2', aggfunc='sum')
    .rename_axis(None, axis=1)
    .reindex(columns=all_class_names, fill_value=0)
    .reset_index()
)

result_gdf = gpd.GeoDataFrame(wide, crs=admin2_reproj.crs)
result_gdf
```

Save the results as a GeoPackage file.


```python
output_path = os.path.join(output_folder, 'admin2_landcover_area.gpkg')
result_gdf.to_file(output_path, driver='GPKG')
```
