The [Global Building Atlas (GBA)](https://essd.copernicus.org/articles/17/6647/2025/) is an open, high-resolution dataset featuring 3D models and footprints for over 2.75 billion buildings worldwide. It provides Level of Detail 1 (LoD1) representations that capture basic building shape and height for all the buildings. This data has been processed into cloud-optimized GeoParquet files and is available on [Source Cooperative](https://source.coop/tge-labs/globalbuildingatlas-lod1).

This notebook shows how to query this dataset using DuckDB and extract a subset for your region of interest.

#### Setup

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
  !pip install lonboard
```

Import packages.


```python
import duckdb
import geopandas as gpd
from lonboard import viz
import os
```

#### Load Area of Interest

Read the file containing the city boundary.


```python
aoi_filepath = os.path.join(data_folder, 'aoi.geojson')

if not os.path.exists(aoi_filepath):
    print(f'AOI file not found at {aoi_filepath}. Using default AOI.')
    aoi_filepath = ('https://storage.googleapis.com/spatialthoughts-public-data'
                    '/python-remote-sensing/aoi.geojson')
```

Read the GeoJSON.


```python
aoi_gdf = gpd.read_file(aoi_filepath)
```

Extract the geometry.


```python
geometry = aoi_gdf.geometry.union_all()
geometry
```

#### Query GlobalBuildingAtlas LoD1 Dataset

We initialize DuckDB. Source Cooperative datasets are hosted on Amazon S3 so weset some s3 parameters to access their data catalog.


```python
coop_con = duckdb.connect()
coop_con.execute('INSTALL spatial; LOAD spatial;')
coop_con.execute('INSTALL httpfs; LOAD httpfs;')
# Uncomment the following lines if you get SSL errors when accessing S3 data
#coop_con.execute('SET s3_region='us-west-2';')
#coop_con.execute('SET s3_url_style='path';')
```

The source data is split into 922 tiles - each covering a 5° x 5° tiles. To choose the right-tile for our AOI, we query the index file from [HuggingFace](https://huggingface.co/datasets/zhu-xlab/GBA.LoD1).


```python
dataset_base = ('s3://us-west-2.opendata.source.coop'
                '/tge-labs/globalbuildingatlas-lod1')
```


```python
# Load the tile index
index_url = ('https://huggingface.co/datasets/zhu-xlab/GBA.LoD1'
             '/resolve/main/representative/lod1.geojson')
tiles = gpd.read_file(index_url)

# Tiles whose footprint actually intersects the AOI
intersecting = tiles[tiles.intersects(geometry)]
basenames = intersecting['tile'].str.split('/').str[-1]

files = [f'{dataset_base}/{b}.parquet' for b in basenames]
print(len(files), 'tile(s):', list(files))
```

Extract the bounding box of our geometry


```python
bbox = geometry.bounds
xmin, ymin, xmax, ymax = bbox
```

Query using DuckDB and load the results as a GeoDataFrame.


```python
file_list = ', '.join(f'{f}' for f in files)
query = f'''
SELECT source, height, bbox, ST_AsWKB(geometry) AS geometry
FROM read_parquet('{file_list}')
WHERE
      struct_extract(bbox, 'xmax') >= {xmin}
  AND struct_extract(bbox, 'xmin') <= {xmax}
  AND struct_extract(bbox, 'ymax') >= {ymin}
  AND struct_extract(bbox, 'ymin') <= {ymax}
'''

result = coop_con.sql(query).df()

buildings_gdf = gpd.GeoDataFrame(
    result,
    geometry=gpd.GeoSeries.from_wkb(
        result['geometry'].apply(bytes)
    ),
    crs='EPSG:4326'
)
buildings_gdf
```

Clip the GeoDataFrame to the geometry.


```python
buildings_gdf = buildings_gdf[buildings_gdf.intersects(geometry)]
```

#### Visualize the Results


```python
viz(buildings_gdf)
```

#### Save the Results

We can save the selected subset as a GeoParquet file.


```python
output_file = f'gba_buildings.parquet'
output_path = os.path.join(output_folder, output_file)
buildings_gdf.to_parquet(output_path, index=False)
print(f'Wrote {output_path}')
```
