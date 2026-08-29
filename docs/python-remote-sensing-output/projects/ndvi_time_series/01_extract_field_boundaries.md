### Overview

We will build a sample dataset of real farm field boundaries for a district in Karnataka. These field boundaries will be used as our Areas of Interest (AOIs) in the following notebooks where we extract an NDVI time-series for each field.

### Overview of the Task

We first select an Admin2 (district) boundary for Karnataka using the FieldMaps administrative boundaries GeoParquet file. We then query the [Global Fields of The World (FTW)](https://beta.source.coop/repositories/ftw/global-data/description/) dataset - a global field boundary dataset derived from Sentinel-2 imagery - for all fields within the district. Finally, we filter out small fields, take a random sample and save the result to Google Drive.

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
    drive_data_folder = 'python-remote-sensing/projects/ndvi_time_series'
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
  !pip install lonboard
```

Import all required libraries.


```python
import duckdb
import geopandas as gpd
import numpy as np
import os
from lonboard import viz
```

### Select the Target Admin Boundary

[FieldMaps](https://fieldmaps.io/data/) provides open datasets of global administrative boundaries. We use [DuckDB](https://duckdb.org/) to query the Admin2 boundaries GeoParquet file directly from the cloud and select a single district in Karnataka as our target.

Initialize DuckDB and enable the spatial extension.


```python
con = duckdb.connect()
con.install_extension('spatial')
con.load_extension('spatial')
```

The source is a single large GeoParquet file containing global Admin2 boundaries.


```python
parquet_url = 'https://data.fieldmaps.io/edge-matched/open/intl/adm2_polygons.parquet'
```

Query all Admin2 districts within the state of Karnataka, India. `adm0_src` is the [3-digit ISO code](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) for the country.


```python
country = 'IND'
adm1_name = 'Karnātaka'

query = f'''
SELECT adm1_name, adm1_id, adm2_name, adm2_id, ST_AsWKB(geometry) AS geometry
FROM read_parquet('{parquet_url}')
WHERE
  adm0_src = '{country}' and
  adm1_name = '{adm1_name}'
'''

admin2_df = con.sql(query).df()
admin2_df
```

Convert the query result to a GeoPandas GeoDataFrame.


```python
admin2_gdf = gpd.GeoDataFrame(
    admin2_df,
    geometry=gpd.GeoSeries.from_wkb(admin2_df['geometry'].apply(bytes)),
    crs='EPSG:4326')
admin2_gdf
```

Visualize all the districts of Karnataka to see the exact `adm2_name` spelling for the district you want to pick.


```python
viz(admin2_gdf)
```

Set the name of the district you want to use as your target boundary.


```python
selected = 'Mysore'
```

Filter the GeoDataFrame to the selected district.


```python
target_gdf = admin2_gdf[admin2_gdf['adm2_name'] == selected].reset_index(drop=True)
target_gdf
```

Visualize the selected district boundary.


```python
viz(target_gdf)
```

Extract the bounding box and geometry of the selected district. We will use these to query field boundaries in the next section.


```python
bbox = target_gdf.total_bounds
xmin, ymin, xmax, ymax = bbox
district_geometry = target_gdf.geometry.union_all()
```

### Extract Field Boundaries

Taylor Geospatial and the Microsoft AI for Good Lab have mapped field boundaries across the world using Sentinel-2 imagery, released as [Global Fields of The World (FTW)](https://beta.source.coop/repositories/ftw/global-data/description/) on Source Cooperative. We query this dataset directly from cloud storage using DuckDB, restricting the query to our selected district.

Source Cooperative datasets are hosted on Amazon S3. We create a separate DuckDB connection and configure S3 access.


```python
coop_con = duckdb.connect()
coop_con.execute("INSTALL spatial; LOAD spatial;")
coop_con.execute("INSTALL httpfs; LOAD httpfs;")
coop_con.execute("SET s3_endpoint='data.source.coop';")
coop_con.execute("SET s3_url_style='path';")
coop_con.execute("SET s3_region='us-east-1';")
coop_con.execute("SET s3_access_key_id='';")
coop_con.execute("SET s3_secret_access_key='';")
coop_con.execute("SET s3_use_ssl=true;")
```

Path to the FTW field predictions, partitioned as Parquet files.


```python
s3_path = 's3://ftw/global-data/predictions/vectors/alpha/results/*.parquet'
```

Query all fields (`label = 'field'`) whose bounding box overlaps our district's bounding box, for the most recent full year of predictions.


```python
year = 2025

query = f'''
SELECT
    time, label, bbox,
    ST_AsWKB(geometry) AS geometry
FROM read_parquet('{s3_path}', hive_partitioning=1)
WHERE label = 'field'
  AND struct_extract(bbox, 'xmax') >= {xmin}
  AND struct_extract(bbox, 'xmin') <= {xmax}
  AND struct_extract(bbox, 'ymax') >= {ymin}
  AND struct_extract(bbox, 'ymin') <= {ymax}
  AND time >= '{year}-01-01'
  AND time < '{year + 1}-01-01'
'''

result = coop_con.sql(query).df()
len(result)
```

Convert the query result to a GeoDataFrame.


```python
fields_gdf = gpd.GeoDataFrame(
    result,
    geometry=gpd.GeoSeries.from_wkb(result['geometry'].apply(bytes)),
    crs='EPSG:4326')
fields_gdf
```

Visualize the queried fields. The query above matches on a bounding-box overlap, so some fields outside the actual district shape are also included.


```python
viz(fields_gdf)
```

### Filter and Sample Fields

We refine the bounding-box query results to the exact district shape, remove fields below a minimum size, and randomly sample a subset for our analysis.

Clip the fields to the exact district boundary using [`gpd.clip()`](https://geopandas.org/en/stable/docs/reference/api/geopandas.clip.html).


```python
fields_clipped = gpd.clip(fields_gdf, target_gdf)
```

Visualize all fields after clipping.


```python
viz(fields_clipped)
```

Compute each field's area in hectares. We reproject to the local UTM zone first so the area is calculated in meters rather than degrees.


```python
utm_crs = fields_clipped.estimate_utm_crs()
fields_clipped['area_ha'] = fields_clipped.geometry.to_crs(utm_crs).area / 10000
```

Keep only the fields within a minimum and maximum size threshold.


```python
min_area_ha = 1
max_area_ha = 5
fields_filtered = fields_clipped[
    (fields_clipped['area_ha'] >= min_area_ha) &
    (fields_clipped['area_ha'] <= max_area_ha)]
print(f'{len(fields_clipped)} fields clipped to district, '
      f'{len(fields_filtered)} fields between {min_area_ha} and {max_area_ha} ha')
```

Randomly sample fields for our analysis.


```python
sample_size = 100
fields_sample = fields_filtered.sample(
    n=min(sample_size, len(fields_filtered)), random_state=42)
len(fields_sample)
```




    100



Visualize the final sample of fields.


```python
viz(fields_sample)
```

The saved field boundaries have no stable identifier. Add one so we can track each field through the extraction below.


```python
fields_sample = fields_sample.reset_index(drop=True)
fields_sample['field_id'] = fields_sample.index
```

### Save the Results

We save the selected district boundary and the sampled field boundaries as a GeoPackage to the output folder.


```python
output_filename = 'selected_admin2.gpkg'
output_path = os.path.join(output_folder, output_filename)
target_gdf.to_file(output_path)
print(f'Saved to {output_path}')
```

    Saved to output/selected_admin2.gpkg



```python
output_filename = 'field_boundaries.gpkg'
output_path = os.path.join(output_folder, output_filename)
fields_sample.to_file(output_path)
print(f'Saved to {output_path}')
```

    Saved to output/field_boundaries.gpkg

