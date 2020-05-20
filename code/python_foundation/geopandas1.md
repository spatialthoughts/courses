conda create --name python_foundation
conda activate python_foundation
conda install geopandas


```python
import os
import pandas as pd
from geopandas import GeoDataFrame
from shapely.geometry import Point
```


```python
home_dir = os.path.expanduser('~')
filename = 'worldcities.csv'
folder = 'Downloads/python_geospatial/'
path = os.path.join(home_dir, folder, filename)
print(path)
```

    /Users/ujaval/Downloads/python_geospatial/worldcities.csv



```python
df = pd.read_csv(path)

geometry = [Point(xy) for xy in zip(df.lng, df.lat)]
crs = {'init': 'epsg:4326'}
gdf = GeoDataFrame(df, crs=crs, geometry=geometry)

output_filename = 'cities.shp'
output_path = os.path.join(home_dir, folder, output_filename)

gdf.to_file(driver='ESRI Shapefile', filename=output_path, encoding='utf-8')

output_filename = 'cities.gpkg'
output_path = os.path.join(home_dir, folder, output_filename)

gdf.to_file(driver='GPKG', filename=output_path, encoding='utf-8')
```


```python

```
