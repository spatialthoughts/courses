### Creating Animated Maps

We take the dataset for 2017 solar eclipse and animate the path of the solar eclipse.

#### Setup and Data Download

The following blocks of code will install the required packages and download the datasets to your Colab environment.


```python
%%capture
if 'google.colab' in str(get_ipython()):
  !apt install libspatialindex-dev
  !pip install fiona shapely pyproj rtree
  !pip install geopandas
  !pip install contextily
```


```python
import contextily as cx
import geopandas as gpd
import os
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
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

path_shapefile = 'upath17'
umbra_shapefile = 'umbra17'
shapefile_exts = ['.shp', '.shx', '.dbf', '.prj']
data_url = 'https://github.com/spatialthoughts/python-dataviz-web/raw/main/data/eclipse/'

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
path_reprojected = path_gdf.to_crs('epsg:3857')
umbra_reprojected = umbra_gdf.to_crs('epsg:3857')
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
plt.tight_layout()

def animate(i):
    ax.clear()
    # Get the point from the points list at index i
    umbra_filtered = umbra_subset.iloc[i:i+1]
    path_reprojected.plot(ax=ax, facecolor='#cccccc', edgecolor='#969696', alpha=0.5)
    cx.add_basemap(ax, crs=path_reprojected.crs, source=cx.providers.OpenTopoMap)
    umbra_filtered.plot(ax=ax, facecolor='#252525', edgecolor='#636363', alpha=0.5)
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
import matplotlib as mpl
mpl.rcParams['animation.embed_limit'] = 2**128
from IPython.display import HTML
HTML(ani.to_jshtml())
```


```python
output_folder = 'output'
output_path = os.path.join(output_folder, 'solar_eclipse.gif')

ani.save(output_path, writer=PillowWriter(fps=5))
```
