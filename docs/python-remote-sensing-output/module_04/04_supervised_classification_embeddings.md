### Overview


Embeddings are a way to compress large amounts of information into a smaller set of features that represent meaningful semantics. Instead of raw pixel values, each location is represented by a dense vector that captures the semantic content of the landscape. [AlphaEarth Foundations (AEF) Embeddings](https://aef-loader.readthedocs.io/en/latest/) is an openly available global dataset of satellite embeddings derived from multiple earth observation datasets, accessible via [Source Cooperative](https://source.coop/). The [`aef-loader`](https://aef-loader.readthedocs.io/en/latest/) package provides a convenient Python interface to query and stream these embeddings without downloading the entire dataset.

Embeddings can be used as input features to the classification model and results in higher accuracy outputs We will perform supervised land cover classification of AEF Embeddings using a Random Forest classifier and generate a classified image for the chosen region of interest.

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
if environment in ['colab', 'colab_enterprise']:
    !pip install rioxarray scikit-learn aef-loader dask[distributed]
    # Due to version conflict, you maybe prompted to
    # restart the runtime after the installation
    # After restarting proceed to run all the cells from the top again
```

Import all required libraries. Make sure to import everything at the beginning as certain Xarray extensions are activated on import and registers certain accesors, like `.rio` and `.odc` for Xarray objects.


```python
import asyncio
import dask.array as da
import geopandas as gpd
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pyproj
import rasterio
import rioxarray as rxr
import xarray as xr
from aef_loader import AEFIndex, VirtualTiffReader, DataSource
from aef_loader.utils import dequantize_aef, reproject_datatree
from odc.geo.geobox import GeoBox
from pyproj import Transformer
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
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

### Load Area of Interest

Read the file containing the city boundary.


```python
aoi_filepath = os.path.join(data_folder, 'aoi.geojson')

if not os.path.exists(aoi_filepath):
    print(f'AOI file not found at {aoi_filepath}. Using default AOI.')
    aoi_filepath = ('https://storage.googleapis.com/spatialthoughts-public-data'
                    '/python-remote-sensing/aoi.geojson')

aoi_gdf = gpd.read_file(aoi_filepath)
geometry = aoi_gdf.geometry.union_all()
geometry
```

### Load Training Data

The training data is a set of Ground Control Points (GCPs) — point features, each labeled with a land cover class. We load the GeoJSON file with GeoPandas.


```python
gcp_filepath = os.path.join(data_folder, 'gcps.geojson')

if not os.path.exists(gcp_filepath):
    print(f'GCP file not found at {gcp_filepath}. Using default GCPs.')
    gcp_filepath = (
        'https://storage.googleapis.com/spatialthoughts-public-data/'
        'python-remote-sensing/gcps.geojson'
    )

gcp_gdf = gpd.read_file(gcp_filepath)
gcp_gdf.head()
```


```python
gcp_gdf['landcover'].value_counts(sort=False)
```


```python
class_colors = {
    0: '#cc6d8f', # Urban
    1: '#ffc107', # Bare
    2: '#1e88e5', # Water
    3: '#004d40', # Vegetation
}

class_names = {
    0: 'Urban',
    1: 'Bare',
    2: 'Water',
    3: 'Vegetation'
}
```


```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(7,7)
aoi_gdf.plot(
    ax=ax,
    facecolor='none',
    edgecolor='#969696')

# Plot the GCPs
for class_label, group in gcp_gdf.groupby('landcover'):
    group.plot(
        ax=ax,
        color=class_colors.get(class_label, 'red'),
        markersize=10,
        label=class_names.get(class_label, f'Unknown Class {class_label}')
    )

ax.legend(loc='upper right')
ax.set_title('Area of Interest with Training Samples')
ax.set_axis_off()
plt.show()
```


    
![](python-remote-sensing-output/module_04/04_supervised_classification_embeddings_files/04_supervised_classification_embeddings_19_0.png)
    


### Load the Satellite Embeddings

We now use the `aef-loader` package to load all the matching tiles of AlphaEarth Foundations Satellite Embeddings from Source Cooperative for the chosen year. This Lazily load the tiles as a XArray DataArray that we can fetch and process in chunks using Dask.

Create a `odc.geo.geobox.GeoBox` object which is a representation of the bounding box with a specific CRS and pixel grid.


```python
year = 2023
bbox = geometry.bounds

```


```python
aoi = pyproj.aoi.AreaOfInterest(*bbox)
utm_crs_list = pyproj.database.query_utm_crs_info(datum_name='WGS 84', area_of_interest=aoi)
target_crs = f'EPSG:{utm_crs_list[0].code}'
print(f'Target CRS: {target_crs}')
```


```python
# Transform bbox from EPSG:4326 to chosen crs
transformer = Transformer.from_crs('EPSG:4326', target_crs, always_xy=True)
x_min, y_min = transformer.transform(bbox[0], bbox[1])
x_max, y_max = transformer.transform(bbox[2], bbox[3])

geobox = GeoBox.from_bbox(
    bbox=(x_min, y_min, x_max, y_max),
    crs=target_crs,
    resolution=10,
)
```


```python
index = AEFIndex(source=DataSource.SOURCE_COOP)
await index.download()

# Query for tiles
tiles = await index.query(
    bbox=bbox,
    years=(year),
)
# Load tiles organized by UTM zone
async with VirtualTiffReader() as reader:
    tree = await reader.open_tiles_by_zone(tiles)

# Depending on the region, there maybe multiple
# tiles spanning different UTM zones
# Reproject all the tiles to the target GeoBox
# with the chosen projection and pixel resolution
combined = reproject_datatree(tree, target_geobox=geobox)
embeddings = combined.embeddings
embeddings
```

The embeddings are saved as 8-bit integer values to save space. We use the `dequantize_aef` helper function provided by `aef-loader` to convert them to the original 32-bit floating point values.


```python
embeddings_year = embeddings.isel(time=0)
embeddings_float = dequantize_aef(embeddings_year)
embeddings_float
```


```python
embeddings_da = embeddings_float.chunk({'y': 1024, 'x': 1024})
embeddings_da
```

We reproject the training points to match the composite CRS, then overlay them on an RGB preview of the composite. This lets us verify that the training points cover the expected land cover types.

### Extract Embeddings at Training Samples




```python
gcp_gdf_reprojected = gcp_gdf.to_crs(embeddings_da.rio.crs)
x_coords = gcp_gdf_reprojected.geometry.x.values
y_coords = gcp_gdf_reprojected.geometry.y.values

# Create xarray DataArrays for indexing with a 'gcp_id' dimension
# This dimension will match the order of the gcp_gdf for easy association
gcp_ids = np.arange(len(gcp_gdf))

gcp_embeddings = embeddings_da.sel(
    x=xr.DataArray(x_coords, dims='gcp_id'),
    y=xr.DataArray(y_coords, dims='gcp_id'),
    method='nearest'
)

# Add landcover labels as a coordinate to the extracted embeddings
gcp_embeddings = gcp_embeddings.assign_coords(
    landcover=('gcp_id', gcp_gdf['landcover'].values)
)

# Display the extracted embeddings for verification
gcp_embeddings
```


```python
%%time
gcp_embeddings = gcp_embeddings.compute()
```

### Train a Classifier

We can now train a classifier with these extracted features. Scikit-learn has a wide-array of classifiers that we can choose from. For most remote sensing applications, [Random Forest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html) is the preferred classifier. However, a good choice for low-shot classification (classification using a very small number of examples, like our example), is [k-Nearest Neighbors (kNN)](https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.KNeighborsClassifier.html). In a kNN classification, labeled examples are used to “partition” or cluster the embedding space, assigning a label for each pixel based on the label(s) of its closest neighbor(s) in the embedding space. Embeddings lend themselves very well to such partitioning. Let’s train a kNN classifier with our training data


```python
# Prepare the data for the classifier
X = gcp_embeddings.values.T # Transpose to have (n_samples, n_features)
y = gcp_embeddings['landcover'].values

# Initialize the KNeighborsClassifier
# Using n_neighbors=5 as a common starting point
classifier = KNeighborsClassifier(n_neighbors=5, weights='distance')

# Train the classifier
classifier.fit(X, y)
```

### Classify the Image



```python
emb_dask = embeddings_da.chunk({'band': -1}).data  # (bands, y, x)

def predict_block(block, model):
    bands, h, w = block.shape
    pixels = block.reshape(bands, -1).T.astype(np.float64)  # (n_pixels, bands)
    valid = ~np.isnan(pixels).any(axis=1)
    result = np.full(h * w, np.nan)
    if valid.any():
        result[valid] = model.predict(pixels[valid]).astype(float)
    return result.reshape(h, w)

predicted_2d = da.map_blocks(
    predict_block,
    emb_dask,
    model=classifier,
    dtype=np.float64,
    drop_axis=0,
)

classified = xr.DataArray(
    predicted_2d,
    coords={'y': embeddings_float.y, 'x': embeddings_float.x},
    dims=['y', 'x'],
    name='landcover'
).rio.write_crs(embeddings_float.rio.crs)
classified
```


```python
%%time
# Compute the predicted landcover map
classified = classified.compute()
classified
```

### Visualize the Classification


```python
aoi_gdf_reprojected = aoi_gdf.to_crs(classified.rio.crs)
classified_clipped = classified.rio.clip(aoi_gdf_reprojected.geometry)
```


```python
sorted_labels = sorted(class_colors.keys())
cmap = mcolors.ListedColormap([class_colors[c] for c in sorted_labels])
cmap.set_bad(alpha=0)
norm = mcolors.BoundaryNorm(
    [i - 0.5 for i in range(len(sorted_labels) + 1)], cmap.N)

preview = classified_clipped.rio.reproject(
    classified_clipped.rio.crs, resolution=100)

fig, ax = plt.subplots(1, 1)
fig.set_size_inches(7, 7)
preview.plot.imshow(ax=ax, cmap=cmap, norm=norm, add_colorbar=False)
ax.legend(
    handles=[mpatches.Patch(
        color=class_colors[c],
        label=class_names[c]) for c in sorted_labels],
    loc='upper right'
)
ax.set_title(f'Classified Image (Embeddings)')
ax.set_axis_off()
ax.set_aspect('equal')
plt.show()
```


    
![](python-remote-sensing-output/module_04/04_supervised_classification_embeddings_files/04_supervised_classification_embeddings_40_0.png)
    


### Save Classified Image

We finally save the results as a local Cloud-Optimized GeoTIFF file.


```python
def write_cog_with_colormap(data_array, output_path, color_table):
    if data_array.dtype != np.dtype('uint8'):
        raise TypeError(f'data_array must be uint8 for a color table to attach')

    # Write to a temp file, add color table, then convert to COG
    tmp_path = output_path + '.tmp.tif'
    data_array.rio.to_raster(tmp_path)

    with rasterio.open(tmp_path) as src:
        profile = src.profile.copy()
        profile['driver'] = 'COG'
        data = src.read(1)
        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(data, 1)
            dst.write_colormap(1, color_table)

    os.remove(tmp_path)
```


```python
# Build rasterio color table from the class_colors hex dict
color_table = {
    label: tuple(int(c * 255) for c in mcolors.to_rgb(hex_color))
    for label, hex_color in class_colors.items()
}

# Cast to uint8 (labels 0-3 fit; use 255 as nodata)
classified_uint8 = (
    classified_clipped
    .fillna(255)
    .astype(np.uint8)
    .rio.write_nodata(255)
)

output_file = f'classification_embeddings.tif'
output_path = os.path.join(output_folder, output_file)
write_cog_with_colormap(classified_uint8, output_path, color_table)
print(f'Wrote {output_path}')
```
