### Creating Animated Maps

We take the dataset for 2017 solar eclipse and animate the path of the solar eclipse.

<img src='https://courses.spatialthoughts.com/images/python_dataviz/eclipse_animation.gif' width=600/>

#### Setup and Data Download

The following blocks of code will install the required packages and download the datasets to your Colab environment.


```python
%%capture
if 'google.colab' in str(get_ipython()):
  !pip install contextily
```


```python
import requests
import contextily as cx
import geopandas as gpd
import os
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import shapely
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
      with requests.get(url, stream=True, allow_redirects=True) as r:
          with open(filename, 'wb') as f:
              for chunk in r.iter_content(chunk_size=8192):
                  f.write(chunk)
      print('Downloaded', filename)
```


```python
path_shapefile = 'upath17'
umbra_shapefile = 'umbra17'
shapefile_exts = ['.shp', '.shx', '.dbf', '.prj']
data_url = 'https://github.com/spatialthoughts/python-dataviz-web/releases/' \
  'download/eclipse/'

for shapefile in [path_shapefile, umbra_shapefile]:
  for ext in shapefile_exts:
    url = data_url + shapefile + ext
    download(url)
```

#### Data Pre-Processing


```python
path_shapefile_path = os.path.join(data_folder, path_shapefile + '.shp')
path_gdf = gpd.read_file(path_shapefile_path)
```


```python
umbra_shapefile_path = os.path.join(data_folder, umbra_shapefile + '.shp')
umbra_gdf = gpd.read_file(umbra_shapefile_path)
```


```python
crs = 'EPSG:9311'

path_reprojected = path_gdf.to_crs(crs)
umbra_reprojected = umbra_gdf.to_crs(crs)

# Use the bounding box coordinates for continental us
usa = shapely.geometry.box(-125, 24, -66, 49)
usa_gdf = gpd.GeoDataFrame(geometry=[usa], crs='EPSG:4326')
usa_gdf_reprojected = usa_gdf.to_crs(crs)
bounds = usa_gdf_reprojected.total_bounds
```


```python
path_boundary = path_reprojected.geometry.unary_union
umbra_subset = umbra_reprojected[umbra_reprojected.geometry.intersects(path_boundary)]
```

#### Creating Animation

We use Matplotlibs `FuncAnimation` function from the `animation` module to create an animation with each frame showing the position of the umbra through the solar eclipse.

Reference: [`matplotlib.animation.FuncAnimation`](https://matplotlib.org/stable/api/_as_gen/matplotlib.animation.FuncAnimation.html)


```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(15,7)

def animate(i):
    ax.clear()
    # Set the bounds
    ax.set_xlim(bounds[0], bounds[2])
    ax.set_ylim(bounds[1], bounds[3])
    # Get the point from the points list at index i
    umbra_filtered = umbra_subset.iloc[i:i+1]

    path_reprojected.plot(
      ax=ax,
      facecolor='#969696',
      edgecolor='none',
      alpha=0.5)
    umbra_filtered.plot(
      ax=ax,
      facecolor='#252525',
      edgecolor='none')
    cx.add_basemap(ax,
      crs=path_reprojected.crs,
      source=cx.providers.OpenTopoMap,
      zoom=5)
    ax.set_axis_off()
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    time = umbra_filtered.iloc[0].Time
    text = 'Time: {} UTC'.format(time)
    ax.text(0.05, 0.20, text, transform=ax.transAxes, fontsize=16,
            verticalalignment='top', bbox=props)
    ax.set_title('2017 Total Solar Eclipse Path', size = 18)

ani = FuncAnimation(fig, animate, frames=len(umbra_subset),
                    interval=500, repeat=True, cache_frame_data=True)
plt.close()
```


```python
output_folder = 'output'
output_path = os.path.join(output_folder, 'solar_eclipse.gif')

ani.save(output_path, writer=PillowWriter(fps=5))
plt.close()
```
