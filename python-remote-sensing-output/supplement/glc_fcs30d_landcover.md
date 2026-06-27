The [Global Land Cover by Fine Classification System at 30m (GLC_FCS30D)](https://zenodo.org/records/8239305) is a dynamic land cover product produced by the Chinese Academy of Sciences. This notebook shows how to access, visualize and reclassify GLC_FCS30D land cover data for a region of interest using cloud-optimized GeoTIFF data hosted on OpenLandMap.

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
  !pip install rioxarray dask[distributed] jupyter-server-proxy
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

### GLC-FCS30


```python
data_url = 'https://s3.openlandmap.org/arco/lc_glc.fcs30d_c_30m_s_20210101_20211231_go_epsg.4326_v20231026.tif'
glc_fcs_ds = rxr.open_rasterio(
    data_url, 
    chunks={'x': 1024, 'y': 1024},  # Explicitly define chunk sizes
)
glc_fcs_ds
```


```python
glc_fcs_da = glc_fcs_ds.squeeze()
glc_fcs_da
```


```python
bbox = aoi_gdf.geometry.total_bounds
glc_fcs_da_subset = glc_fcs_da.rio.clip_box(*bbox)
glc_fcs_da_subset
```


```python
%%time
glc_fcs_da_subset = glc_fcs_da_subset.compute()
```


```python
aoi = pyproj.aoi.AreaOfInterest(*bbox)
utm_crs_list = pyproj.database.query_utm_crs_info(datum_name='WGS 84', area_of_interest=aoi)
utm_crs = pyproj.CRS.from_epsg(utm_crs_list[0].code)
utm_crs
```


```python
glc_fcs_da_clipped = glc_fcs_da_subset.astype('float32').rio.clip(aoi_gdf.geometry)
glc_fcs_da_reprojected = glc_fcs_da_clipped.rio.reproject(utm_crs)
glc_fcs_da_reprojected
```


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

colors = ['#000000'] * 256
for key, value in glc_fcs_class_dict.items():
    colors[key] = f'#{value["hex"]}'
colors[0] = (0, 0, 0, 0)  # transparent for nodata
glc_cmap = matplotlib.colors.ListedColormap(colors)
normalizer = matplotlib.colors.Normalize(vmin=0, vmax=255)

unique_classes = sorted(glc_fcs_class_dict.keys())
boundaries = [(unique_classes[i + 1] + unique_classes[i]) / 2
              for i in range(len(unique_classes) - 1)]
boundaries = [0] + boundaries + [255]
ticks = [(boundaries[i + 1] + boundaries[i]) / 2
         for i in range(len(boundaries) - 1)]
tick_labels = [f'{v["description"]} ({k})' for k, v in glc_fcs_class_dict.items()]

fig, ax = plt.subplots(1, 1)
fig.set_size_inches(12, 14)

glc_fcs_da_clipped.plot(ax=ax, cmap=glc_cmap, norm=normalizer)

colorbar = fig.colorbar(
    cm.ScalarMappable(norm=normalizer, cmap=glc_cmap),
    boundaries=boundaries,
    values=unique_classes,
    cax=fig.axes[1].axes,
)
colorbar.set_ticks(ticks, labels=tick_labels)

ax.set_axis_off()
ax.set_title('Landcover Classes from GLC_FCS30D')
```
