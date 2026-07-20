### Overview

We will prepare a multi-band composite containing spectral bands, spectral indices, elevation and slope. When the composite is used to extract training features for machine learning models, each band adds a different context for the model.


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
%%capture
if environment in ['colab', 'colab_enterprise']:
    !pip install pystac-client odc-stac rioxarray dask['distributed'] botocore \
      jupyter-server-proxy planetary_computer xarray-spatial
```

Import all required libraries. Make sure to import everything at the beginning as certain Xarray extensions are activated on import and registers certain accesors, like `.rio` and `.odc` for Xarray objects.


```python
import dask.array as da
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import os
import pystac_client
import rioxarray as rxr
from shapely.geometry import box
import shutil
import tempfile
import xarray as xr
from odc.stac import configure_s3_access, load
from osgeo import gdal
import planetary_computer as pc
from xrspatial import slope
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

aoi_filepath
```

Read the GeoJSON and extract the geometry.


```python
aoi_gdf = gpd.read_file(aoi_filepath)
geometry = aoi_gdf.geometry.union_all()
geometry

```

### Search and Load Sentinel-2 Imagery

We search the Earth Search STAC catalog for Sentinel-2 L2A scenes covering our AOI and load them as a lazy XArray Dataset using Dask.


```python
catalog = pystac_client.Client.open(
    'https://earth-search.aws.element84.com/v1')

configure_s3_access(aws_unsigned=True)

# Search for images
# To ensure the process runs quickly, we will select images
# from a specific time range and with low cloud cover
year = 2023
start_month = 4
end_month = 5
time_range = f'{year}-{start_month:02d}/{year}-{end_month:02d}'

search = catalog.search(
    collections=['sentinel-2-c1-l2a'],
    intersects=geometry,
    datetime=time_range,
    query={'eo:cloud_cover': {'lt': 30}},
)
items = search.item_collection()
```

Load the matching scenes as a lazy XArray Dataset.


```python
ds = load(
    items,
    bands=['red', 'green', 'blue', 'nir', 'swir16', 'swir22', 'scl'],
    resolution=10,
    crs='utm',
    bbox=geometry.bounds,
    chunks={'x': 1024, 'y': 1024},  # Explicitly define chunk sizes
    groupby='solar_day',
)
ds
```


```python
# Mask nodata (Sentinel-2 uses 0 as nodata)
ds = ds.where(ds != 0)

# Apply scale and offset to spectral bands
scale = 0.0001
offset = -0.1
data_bands = [b for b in ds.data_vars if b != 'scl']
for band in data_bands:
    ds[band] = ds[band] * scale + offset

# Apply cloud mask using SCL band
# 3=cloud shadow, 8=cloud medium probability, 9=cloud high probability, 10=thin cirrus
cloud_mask = ds.scl.isin([3, 8, 9, 10])
ds = ds[data_bands].where(~cloud_mask)
ds
```

### Create Median Composite

Aggregate all cloud-masked scenes into a single median composite. The median effectively removes any remaining cloud and shadow artifacts that pass the SCL mask.


```python
composite = ds.median(dim='time')
composite
```

### Calculate Spectral Indices

We compute five spectral indices that are useful for mapping urban land cover and water bodies.

- NDVI: `(NIR − Red) / (NIR + Red)`
- NDBI: `(SWIR1 − NIR) / (SWIR1 + NIR)`
- BSI: `((SWIR1 + Red) − (NIR + Blue)) / ((SWIR1 + Red) + (NIR + Blue))`
- MNDWI: `(Green − SWIR1) / (Green + SWIR1)`
- NDWI: `(Green − NIR) / (Green + NIR)`


```python
red    = composite['red']
green  = composite['green']
blue   = composite['blue']
nir    = composite['nir']
swir16 = composite['swir16']

composite['ndvi']  = (nir - red)    / (nir + red)
composite['ndbi']  = (swir16 - nir) / (swir16 + nir)
composite['bsi'] = (
    ((swir16 + red) - (nir + blue)) /
    ((swir16 + red) + (nir + blue))
)
composite['mndwi'] = (green - swir16) / (green + swir16)
composite['ndwi']  = (green - nir)    / (green + nir)

composite
```

### Add Elevation Data

We query Microsoft’s Planetary Computer Data Catalog and load the [ALOS World 3D - 30m](https://planetarycomputer.microsoft.com/dataset/alos-dem#overview) elevation data.




```python
catalog = pystac_client.Client.open(
    'https://planetarycomputer.microsoft.com/api/stac/v1')

search = catalog.search(
    collections=['alos-dem'],
    intersects=geometry,
)
items = search.item_collection()
items
```

We will add the resulting data as a new band to the composite. To ensure the data is aligned with the pixel grid of the composite, we extract the [GeoBox](https://odc-geo.readthedocs.io/en/latest/intro-geobox.html) of the composite and use it to load the items.


```python
geobox = composite.odc.geobox
geobox
```


```python
chunks = dict(zip(composite['red'].dims, composite['red'].data.chunksize))
chunks
```


```python
# Load to XArray
dem_ds = load(
    items,
    geobox=geobox, # <--- Match pixel grid
    chunks=chunks,  # <-- Match dask chunks
    patch_url=pc.sign,
    groupby='solar_day',
    preserve_original_order=True
)
dem_ds

```

We remove the extra `time` dimension to create a 2D DataArray.


```python
elevation_da = dem_ds.data.squeeze()
elevation_da
```

We use [`xrspatial.slope.slope()`](https://xarray-spatial.readthedocs.io/en/latest/reference/_autosummary/xrspatial.slope.slope.html) function to calculate the slope.


```python
slope_da = slope(elevation_da)
slope_da
```

Add the data to the composite.


```python
composite[['elevation', 'slope']] = elevation_da, slope_da
composite
```

### Add Coordinate as Bands

We can also add X and Y coordinates as input parameters - which helps the machine learning model learn spatial patterns. We use [`dask.array.broadcast_to()`](https://docs.dask.org/en/latest/generated/dask.array.broadcast_to.html) function to get a Dask array of X and Y coordinates and assign them as variables. We get 2 new variables `x_coord` and `y_coord` in the composite.


```python
# Get the chunk sizes for x and y dimensions
y_chunks, x_chunks = composite['red'].data.chunks

x_vals = composite.x.values
y_vals = composite.y.values

# Create Dask arrays for x and y coordinates
x_1d = da.from_array(x_vals, chunks=x_chunks)
y_1d = da.from_array(y_vals, chunks=y_chunks)

# Turn the 1D coordinate arrays into 2D arrays
# that match the shape of the composite
xx_da = da.broadcast_to(
    x_1d[None, :], (composite.sizes['y'], composite.sizes['x']))
yy_da = da.broadcast_to(
    y_1d[:, None], (composite.sizes['y'], composite.sizes['x']))

composite = composite.assign(
    x_coord=(('y', 'x'), xx_da),
    y_coord=(('y', 'x'), yy_da),

composite
```


```python
print(f'DataSet size: {composite.nbytes/1e6:.2f} MB.')
```

### Clip and Export the Composite

We first convert it to a DataArray using the `to_array()` method. All the variables will be converted to a new dimension. Since our variables are image bands, we give the name of the new dimesion as band.


```python
composite_da = composite.to_array('band')
composite_da = composite_da.rio.write_nodata(np.nan)
composite_da
```

### Tile and Export the Composite

Writing a large multi-band composite in one shot can exceed available memory, since it forces the entire Dask graph (all bands, full extent) to materialize at once. To avoid this, we only tile the export when the composite is large: if it is smaller than `TILE_SIZE` pixels in both dimensions, we export it as a single file as before. Otherwise, we split the AOI into a grid of tiles, and compute/clip/write one tile at a time to a local temporary folder. We then mosaic the local tiles into a single Cloud-Optimized GeoTIFF and copy just that one file to `output_folder`.


```python
TILE_SIZE = 5000  # pixels

x_size = composite_da.sizes['x']
y_size = composite_da.sizes['y']
tiled_export = x_size >= TILE_SIZE or y_size >= TILE_SIZE

print(f'Composite size: {x_size} x {y_size} pixels')
print(f'Tiled export: {tiled_export}')
```

If the composite is small enough, we clip it to the AOI, compute it, and save it as a single Cloud-Optimized GeoTIFF using the rioxarray accessor. Otherwise, we build a grid of tiles over the AOI and, for each tile, use [`clip_box()`](https://corteva.github.io/rioxarray/stable/rioxarray.html#rioxarray.raster_array.RasterArray.clip_box) for a lazy windowed read, `.compute()` to materialize just that tile, and [`clip()`](https://corteva.github.io/rioxarray/stable/rioxarray.html#rioxarray.raster_array.RasterArray.clip) to trim it to the exact AOI boundary. Each tile is saved locally, then [`gdal.BuildVRT()`](https://gdal.org/en/stable/programs/gdalbuildvrt.html) and [`gdal.Translate()`](https://gdal.org/en/stable/programs/gdal_translate.html) mosaic the tiles into a single local COG, which we copy to `output_folder`.


```python
aoi_gdf_reproj = aoi_gdf.to_crs(composite_da.rio.crs)

output_file = 'multiband_composite.tif'
local_output_path = os.path.join(output_folder, output_file)

if not tiled_export:
    print('Exporting composite as a single COG')
    composite_da = composite_da.compute()
    composite_clipped = composite_da.rio.clip(aoi_gdf_reproj.geometry)
    composite_clipped.rio.to_raster(local_output_path, driver='COG')
else:
    print('Exporting composite as tiled COGs')
    left, bottom, right, top = composite_da.rio.bounds()
    res_x = (right - left) / x_size
    tile_size_m = TILE_SIZE * res_x

    minx, miny, maxx, maxy = aoi_gdf_reproj.total_bounds
    xs = np.arange(minx, maxx, tile_size_m)
    ys = np.arange(miny, maxy, tile_size_m)

    tiles = [
        box(x, y, x + tile_size_m, y + tile_size_m)
        for y in sorted(ys, reverse=True)
        for x in xs
    ]
    grid = gpd.GeoDataFrame(geometry=tiles, crs=composite_da.rio.crs)
    grid = grid[grid.intersects(aoi_gdf_reproj.union_all())].reset_index(drop=True)
    grid['tile_id'] = [
        f'tile_{(i // len(ys)) + 1:02d}_{(i % len(ys)) + 1:02d}'
        for i in grid.index
    ]
    print(f'{len(grid)} tiles intersect the AOI')

    with tempfile.TemporaryDirectory() as tmp_dir:
        tile_paths = []

        for _, row in grid.iterrows():
            print(f'Processing tile {row["tile_id"]}')
            tile_id = row['tile_id']
            tile_bounds = row.geometry.bounds

            # Pull only this tile into memory
            tile = composite_da.rio.clip_box(*tile_bounds).compute()

            try:
                tile_clipped = tile.rio.clip(aoi_gdf_reproj.geometry)
            except Exception:
                continue

            tile_path = os.path.join(tmp_dir, f'{tile_id}.tif')
            tile_clipped.rio.to_raster(tile_path, driver='COG')
            tile_paths.append(tile_path)
            print(f'Wrote tile {tile_id}')

        # Mosaic the local tiles into a single local COG
        vrt_path = os.path.join(tmp_dir, 'mosaic.vrt')
        vrt = gdal.BuildVRT(vrt_path, tile_paths)
        vrt.FlushCache()
        vrt = None

        mosaic_path = os.path.join(tmp_dir, output_file)
        gdal.Translate(mosaic_path, vrt_path, format='COG')

        # Copy just the final mosaic to the output folder
        shutil.copy(mosaic_path, local_output_path)

print(f'Wrote {local_output_path}')
```
