### Overview

In this section, we will explore cloud-native vector datasets and use [DuckDB](https://duckdb.org/) to query and load data directly from cloud. We also use [Lonboard](https://developmentseed.org/lonboard/latest/) for interactively visualizing query results.

### Overview of the Task

We will query and load an Administrative Boundaries dataset provided by FieldMaps as a cloud-native GeoParquet file. We will interactively query and save the required boudary polygon for our analysis.

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

print(f'Environment: {environment}')
```

If we are on Google Colab, install the required packages. Local runtimes are expected to have the packages already installed.


```python
%%capture
if environment in ['colab', 'colab_enterprise']:
  !pip install lonboard
```

Import packages.


```python
import duckdb
import geopandas as gpd
from lonboard import viz
import os
```

### DuckDB

DuckDb is a modern high-performance database engine that allows querying large files easily. It has built-in support for spatial data and can be used to query large remote spatial files without downloading it first.

We initialize DuckDB and enable the spatial extension.


```python
con = duckdb.connect()
con.install_extension('spatial')
con.load_extension('spatial')
```

### Query Remote Dataset

[FieldMaps](https://fieldmaps.io/data/) provides open datasets of global administrative boundaries from multiple providers. We will query the Admin2 boundaries from GeoBoundaries in the GeoParquet format. The souce data is a 2 GB `.parquet` file containing 48000+ polygons. Instead of downloading this, we can query it and extract just the subset we require.


```python
parquet_url = 'https://data.fieldmaps.io/edge-matched/open/intl/adm2_polygons.parquet'
```

DuckDB supports standard SQL syntax for querying. Let's check some basic information about the dataset.


```python
query = f'''
SELECT COUNT(*) FROM read_parquet('{parquet_url}')
'''
result = con.sql(query).fetchone()
print('Total Features', result)
```

We can use `DESCRIBE` clause to get the available columns. We can turn the results of any query to a DataFrame using the `.df()`.


```python
query = f'''
    DESCRIBE SELECT * FROM read_parquet('{parquet_url}')
'''
columns = con.sql(query).df()
columns
```

We can now form a query to find all all Admin1 names (States/Provinces) in a specific country. We will use this in the next step to fetch all Admin2 regions within a specific Admin1 area. The `adm0_src` uses the [3-digit ISO code](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) for each country.



```python
country = 'IND'

query = f'''
SELECT DISTINCT adm1_name
FROM read_parquet('{parquet_url}')
WHERE adm0_src = '{country}'
ORDER BY adm1_name
'''

admin1_df = con.sql(query).df()
admin1_df
```

Notice that the dataset has a `geometry` column which stores the layer geometry. We can now query for all Admin2 polygons within our chosen Admin1 region. Also since Parquet is a columnar format, so it is efficient to fetch only the required columns.


```python
adm1_name = 'Karnataka'

query = f'''
SELECT adm1_name, adm1_id, adm2_name, adm2_id, ST_AsWKB(geometry) AS geometry
FROM read_parquet('{parquet_url}')
WHERE
  adm0_src = '{country}' and
  adm1_name = '{adm1_name}'
'''

admin2_df = con.sql(query).df()
```

We turn the results into a GeoPandas GeoDataFrame by specifying the geometry column and the CRS.


```python
admin2_gdf = gpd.GeoDataFrame(
    admin2_df,
    geometry=gpd.GeoSeries.from_wkb(admin2_df['geometry'].apply(bytes)),
    crs='EPSG:4326')
admin2_gdf
```

We can visualize the Admin2 polygons.


```python
viz(admin2_gdf)
```

### Save the Results

We can save the selected subset as a GeoPackage. We can now save it as a file. 

On Google Colab, data saved to the local filesystem will be deleted when the runtime is disconnected. It is recommended to save it to permanent cloud storage so you will have access to it later. 

Google Colab has a built-in integration with Google Drive and provides the easiest solution for storing persistent data. The following cell mounts your Google Drive in the Colab runtime. If you do not want to use Google Drive, set `use_google_drive=False` and it will be saved on the local filesystem that you can download.


```python
import os

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
    output_folder = 'output'

if not os.path.exists(output_folder):
    os.mkdir(output_folder)

print(f'Environment: {environment}')
print(f'Output folder: {output_folder}')
```


```python
output_filename = 'admin2.gpkg'
output_path = os.path.join(output_folder, output_filename)
admin2_gdf.to_file(output_path)
print(f'Saved to {output_path}')
```

### Exercise

[Overture Maps](https://overturemaps.org/) provides free and open map data curated from sources like OpenStreetMap. The entire dataset is available in cloud-native [GeoParquet format](https://docs.overturemaps.org/getting-data/cloud-sources/).

Extract the boundary for your selected city and save it to your output directory in GeoJSON format as `aoi.geojson`.


```python
aoi_filepath = os.path.join(output_folder, 'aoi.geojson')
```

#### Tips

Use the cells below with the starter code.

* Search for your city/region of interest using [Overture Explorer](https://explore.overturemaps.org/) and replace the name, country and region with your own area of interest.
* Cities are not uniformly represented across the world. Some cities are tagged as *locality* while others with *county* or *localadmin*. The SQL query below tries to capture all the variations, but if you get no matches, you can relax the query by commenting out some lines by prefixing it with `--`.
* By default the boundary tagged as `locality` will be picked. To see other options comment the line starting with `LIMIT 1`.



```python
country_iso2 = 'IN'
city_name = 'Bengaluru'
region = 'IN-KA'
```


```python
# Overture does monthly releases of their dataset
# Find the latest release at https://stac.overturemaps.org/
OVERTURE_RELEASE = '2026-05-20.0'

s3_path = (
        f's3://overturemaps-us-west-2/release/{OVERTURE_RELEASE}/'
        'theme=divisions/type=division_area/*'
    )

query = f'''
  SELECT
      id,
      names.primary AS primary_name,
      names.common.en AS common_name,
      subtype,
      country,
      region,
      ST_AsWKB(geometry) AS geometry
  FROM read_parquet(
      '{s3_path}',
      filename=true,
      hive_partitioning=1
  )
  WHERE subtype in ('locality', 'county', 'localadmin', 'region') AND
  country = '{country_iso2}' AND
  region = '{region}' AND
  (names.primary ILIKE '{city_name}' OR names.common.en ILIKE '{city_name}') AND
  is_land = true          -- exclude maritime extensions
  ORDER BY
    -- prefer 'locality' over other types
    CASE subtype WHEN 'locality' THEN 0 ELSE 1 END
  LIMIT 1
'''

results = con.sql(query).df()
results
```

View the resulting boundary.


```python
aoi_gdf = gpd.GeoDataFrame(
    results,
    geometry=gpd.GeoSeries.from_wkb(results['geometry'].apply(bytes)),
    crs='EPSG:4326'
)

viz(aoi_gdf)
```
