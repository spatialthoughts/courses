### Overview

In this section, we will explore cloud-native vector datasets and use [DuckDB](https://duckdb.org/) to query and load data directly from cloud.

### Overview of the Task

We will query and load an Administrative Boundaries dataset provided by FieldMaps as a cloud-native GeoParquet file. We will interactively query and save the required boudary polygon for our analysis.


```python
%%capture
if 'google.colab' in str(get_ipython()):
    !pip install leafmap
```


```python
import duckdb
import geopandas as gpd
import leafmap.foliumap as leafmap
import os
```


```python
data_folder = 'data'
output_folder = 'output'

if not os.path.exists(data_folder):
    os.mkdir(data_folder)
if not os.path.exists(output_folder):
    os.mkdir(output_folder)
```

If you are running this notebook in Colab, you will need to create and use a proxy URL to see the dashboard running on the local server.

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
country = 'USA'

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
adm1_name = 'California'

query = f'''
SELECT adm1_name, adm1_id, adm2_name, adm2_id, ST_AsText(geometry) AS geometry
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
    admin2_df, geometry=gpd.GeoSeries.from_wkt(admin2_df.geometry), crs='EPSG:4326'
)
admin2_gdf
```

We can visualize the Admin2 polygons.


```python
m = leafmap.Map(width=800, height=500)
m.add_gdf(admin2_gdf, layer_name='Admin2', style={'color':'blue', 'weight':0.5})
m.zoom_to_gdf(admin2_gdf)
m
```

Select a single Admin2 region and extract the geometry.


```python
adm2_name = 'San Francisco'
selected = admin2_gdf[admin2_gdf['adm2_name'] == adm2_name]
geometry = selected.geometry.union_all()
geometry
```

### Save the Results

We can save the selected subset as a GeoPackage. Rather than saving it to the temporary machine where Colab is running, we can save it to our own Google Drive. This will ensure the image will be available to us even after existing Google Colab.

Run the following cell to authenticate and mount the Google Drive.


```python
if 'google.colab' in str(get_ipython()):
  from google.colab import drive
  drive.mount('/content/drive')
```


```python
if 'google.colab' in str(get_ipython()):
  drive_folder_root = 'MyDrive'
  output_folder = 'data'
  output_folder_path = os.path.join(
      '/content/drive', drive_folder_root, output_folder)

  # Check if Google Drive is mounted
  if not os.path.exists('/content/drive'):
      print('Google Drive is not mounted. Please run the cell above to mount your drive.')
  else:
      if not os.path.exists(output_folder_path):
          os.makedirs(output_folder_path)
else:
  # Use the local folder
  output_folder_path = output_folder
```


```python
output_filename = 'admin2.gpkg'
output_path = os.path.join(output_folder_path, output_filename)
admin2_gdf.to_file(output_path)
```

### Exercise

[Overture Maps](https://overturemaps.org/) provides free and open map data curated from sources like OpenStreetMap. The entire dataset is available in cloud-native [GeoParquet format](https://docs.overturemaps.org/getting-data/cloud-sources/). We can use it to query and extract city municipal boundary for any city.

Search for your city/region of interest using [Overture Explorer](https://explore.overturemaps.org/) and replace the name, country and region with your own area of interest.

Tips:

* Cities are not uniformly represented across the world. Some cities are tagged as *locality* while others with *county* or *localadmin*. The SQL query below tries to capture all the variations, but if you get no matches, you can relax the query by commenting out some lines by prefixing it with `--`.
  * Comment the line with `region = '{region}'` to search other regions in the country.
  * By default the boundary tagged as `locality` will be picked. To see other options comment the line starting with `LIMIT 1`.



```python
country_iso2 = 'US'
city_name = 'New York'
region = 'US-NY'
```


```python
# Overture does monthly releases of their dataset
# Find the latest release at https://stac.overturemaps.org/
OVERTURE_RELEASE = '2026-04-15.0'

s3_path = (
        f's3://overturemaps-us-west-2/release/{OVERTURE_RELEASE}/'
        'theme=divisions/type=division_area/*'
    )

query = f'''
  SELECT
      id,
      names.primary AS name,
      subtype,
      country,
      region,
      ST_AsText(geometry) AS geometry
  FROM read_parquet(
      '{s3_path}',
      filename=true,
      hive_partitioning=1
  )
  WHERE subtype in ('locality', 'county', 'localadmin', 'region') AND
  country = '{country_iso2}' AND
  region = '{region}' AND
  names.primary ILIKE '{city_name}'
  AND is_land = true          -- exclude maritime extensions
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
city_gdf = gpd.GeoDataFrame(
    results, geometry=gpd.GeoSeries.from_wkt(results.geometry), crs='EPSG:4326'
)

m = leafmap.Map(width=800, height=500)
m.add_gdf(city_gdf, layer_name='City', style={'color':'blue', 'weight':0.5})
m.zoom_to_gdf(city_gdf)
m
```
