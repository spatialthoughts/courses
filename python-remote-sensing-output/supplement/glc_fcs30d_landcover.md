The [Global Land Cover by Fine Classification System at 30m (GLC_FCS30D)](https://zenodo.org/records/8239305) is a dynamic land cover product produced by the Chinese Academy of Sciences. It provides a high-resolution landcover time-series derived from the Landsat archive (1984-2022) at 30m resolution with 35 classes.

This notebook shows how to access, visualize and reclassify GLC_FCS30D land cover data for a region of interest using cloud-optimized GeoTIFF data hosted on OpenLandMap.

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
use_google_drive = False

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
  !pip install rioxarray dask[distributed] odc-stac \
    jupyter-server-proxy
```

Import all required libraries.


```python
import geopandas as gpd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
import pyproj
import rioxarray as rxr
from matplotlib import cm
from odc import stac

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

#### Load GLC-FCS30 Data


```python
data_url = (
    'https://s3.openlandmap.org/arco/'
    'lc_glc.fcs30d_c_30m_s_20210101_20211231_go_epsg.4326_v20231026.tif')
glc_fcs_ds = rxr.open_rasterio(
    data_url,
    chunks={'x': 1024, 'y': 1024},  # Explicitly define chunk sizes
)
glc_fcs_ds
```

This is a global raster at 30m resolution available as a single COG. We can clip and reproject the data to get the subset for our region of interest.


```python
bbox = aoi_gdf.geometry.total_bounds
glc_fcs_ds = glc_fcs_ds.rio.clip_box(*bbox)
glc_fcs_ds = glc_fcs_ds.odc.reproject('utm')
glc_fcs_ds
```


```python
glc_fcs_da = glc_fcs_ds.squeeze()
glc_fcs_da
```


```python
%%time
glc_fcs_da = glc_fcs_da.compute()
```

Clip the data to geometry. Before we clip, we need to reproject the `aoi_gdf` to the same CRS as the data.


```python
aoi_gdf_reprojected = aoi_gdf.to_crs(glc_fcs_da.rio.crs)
glc_fcs_da_clipped = glc_fcs_da.rio.clip(aoi_gdf_reprojected.geometry)
```

#### Visualize the Data

To create a meaningful legend, we create a dictionary of class names and colors for the landcover classes.


```python
glc_fcs_class_dict = {
    10: {'description': 'Rainfed cropland', 'hex': 'ffff64'},
    11: {'description': 'Herbaceous cover cropland', 'hex': 'ffff64'},
    12: {'description': 'Tree/shrub cover (Orchard) cropland', 'hex': 'ffff00'},
    20: {'description': 'Irrigated cropland', 'hex': 'aaf0f0'},
    51: {'description': 'Open evergreen broadleaved forest', 'hex': '4c7300'},
    52: {'description': 'Closed evergreen broadleaved forest', 'hex': '006400'},
    61: {'description': 'Open deciduous broadleaved forest', 'hex': 'aac800'},
    62: {'description': 'Closed deciduous broadleaved forest', 'hex': '00a000'},
    71: {'description': 'Open evergreen needle-leaved forest', 'hex': '005000'},
    72: {'description': 'Closed evergreen needle-leaved forest', 'hex': '003c00'},
    81: {'description': 'Open deciduous needle-leaved forest', 'hex': '286400'},
    82: {'description': 'Closed deciduous needle-leaved forest', 'hex': '285000'},
    91: {'description': 'Open mixed leaf forest', 'hex': 'a0b432'},
    92: {'description': 'Closed mixed leaf forest', 'hex': '788200'},
    120: {'description': 'Shrubland', 'hex': '966400'},
    121: {'description': 'Evergreen shrubland', 'hex': '964b00'},
    122: {'description': 'Deciduous shrubland', 'hex': '966400'},
    130: {'description': 'Grassland', 'hex': 'ffb432'},
    140: {'description': 'Lichens and mosses', 'hex': 'ffdcd2'},
    150: {'description': 'Sparse vegetation', 'hex': 'ffebaf'},
    152: {'description': 'Sparse shrubland', 'hex': 'ffd278'},
    153: {'description': 'Sparse herbaceous', 'hex': 'ffebaf'},
    181: {'description': 'Swamp', 'hex': '00a884'},
    182: {'description': 'Marsh', 'hex': '73ffdf'},
    183: {'description': 'Flooded flat', 'hex': '9ebbd7'},
    184: {'description': 'Saline', 'hex': '828282'},
    185: {'description': 'Mangrove', 'hex': 'f57ab6'},
    186: {'description': 'Salt marsh', 'hex': '66cdab'},
    187: {'description': 'Tidal flat', 'hex': '444f89'},
    190: {'description': 'Impervious surfaces', 'hex': 'c31400'},
    200: {'description': 'Bare areas', 'hex': 'fff5d7'},
    201: {'description': 'Consolidated bare areas', 'hex': 'dcdcdc'},
    202: {'description': 'Unconsolidated bare areas', 'hex': 'fff5d7'},
    210: {'description': 'Water body', 'hex': '0046c8'},
    220: {'description': 'Permanent ice and snow', 'hex': 'ffffff'},
}
```

Create a preview and plot.


```python
import matplotlib.patches as mpatches

# Create a preview
glc_fcs_da_preview = glc_fcs_da_clipped.rio.reproject(
    glc_fcs_da_clipped.rio.crs, resolution=100
)

colors_map = ['#000000'] * 256
for key, value in glc_fcs_class_dict.items():
    colors_map[key] = f'#{value["hex"]}'
colors_map[0] = (0, 0, 0, 0)  # transparent for nodata
glc_cmap = matplotlib.colors.ListedColormap(colors_map)
normalizer = matplotlib.colors.Normalize(vmin=0, vmax=255)

fig, ax = plt.subplots(1, 1)
fig.set_size_inches(10, 10) # Increased width to accommodate 2-column legend

glc_fcs_da_preview.plot(ax=ax, cmap=glc_cmap,
                        norm=normalizer, add_colorbar=False)

# # Create custom legend handles
legend_handles = []
for class_id in sorted(glc_fcs_class_dict.keys()): # Ensure consistent order
    class_info = glc_fcs_class_dict[class_id]
    hex_color = f'#{class_info["hex"]}'
    description = class_info["description"]
    handle = mpatches.Patch(color=hex_color, label=f'{description} ({class_id})')
    legend_handles.append(handle)

# Add the legend with 2 columns
ax.legend(handles=legend_handles,
          loc='center left',
          bbox_to_anchor=(1.05, 0.5),
          ncol=1,
          fontsize='small',
          )

ax.set_axis_off()
ax.set_aspect('equal')
ax.set_title('Landcover Classes from GLC_FCS30D')

fig.tight_layout() # Adjust layout to prevent labels from being cut off
plt.show()
```


    
![](python-remote-sensing-output/supplement/glc_fcs30d_landcover_files/glc_fcs30d_landcover_31_0.png)
    

