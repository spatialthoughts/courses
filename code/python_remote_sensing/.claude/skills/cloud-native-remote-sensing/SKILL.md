---
name: cloud-native-remote-sensing
description: Guide for writing cloud-native remote sensing code in Python using the patterns from this course. Invoke at the start of a session before writing or editing any analysis code — e.g. when creating a new notebook, adding a new workflow, or debugging an existing one. Apply these patterns and best practices when helping with remote sensing analysis.
---

# Cloud-Native Remote Sensing Guide

## Stack

- `pystac_client` — STAC catalog search
- `odc.stac` (`odc-stac`) — load STAC items to XArray
- `xarray` + `rioxarray` — raster data model and geospatial ops
- `dask` / `dask.distributed` — lazy parallel computation
- `geopandas` — vector data
- `duckdb` — querying cloud-native vector files (GeoParquet, Parquet)
- `scikit-learn` — machine learning and classification
- `xvec` + `exactextract` — zonal statistics

---

## Coding Best Practices

- Import all required packages at the beginning and keep all the imports sorted alphabetically.
- Add a Markdown cell before each code cell with a brief explanation and link to the function(s) in the official documentation.

---

## Dask Setup

Always create a local Dask cluster at the start:

```python
from dask.distributed import Client
client = Client()
```

- Defer processing as much as you can. Prefer dask-aware ops, such as `rioxarray`'s `clip_box()` over `clip()`.
- Never call `.compute()` until the lazy graph is fully built (all masking, indexing, calculations done). Compute once at the end.
- Order of preference for computations:
    1. Built-in XArray functions — e.g. `median()`, `resample()`
    2. Built-in Dask array functions — e.g. `da.histogram()`
    3. Custom functions via `map_blocks()` for third-party libraries that work with NumPy arrays. We prefer this over `apply_ufunc()` because of simpler syntax.
    4. Custom functions via `apply_ufunc()` for third-party libraries that work with NumPy arrays
    5. Custom functions via `dask.delayed()` for arbitrary Python code (slowest, least efficient)

---

## XArray Setup

- Always use vectorized functions and broadcasting to avoid iterations — e.g. `scene[data_bands].where(~mask)` instead of a per-band loop.
- Prefer Python packages from the XArray ecosystem.

---

## STAC Search Pattern

```python
import pystac_client
from odc.stac import configure_s3_access, load

# Earth Search (AWS, free)
catalog = pystac_client.Client.open('https://earth-search.aws.element84.com/v1')
configure_s3_access(aws_unsigned=True)

# Planetary Computer (Azure, requires signed URLs)
import planetary_computer as pc
catalog = pystac_client.Client.open('https://planetarycomputer.microsoft.com/api/stac/v1')
# add patch_url=pc.sign to stac.load()

# Build bbox from a point
km2deg = 1.0 / 111
r = radius_km * km2deg
bbox = (lon - r, lat - r, lon + r, lat + r)

# Search
search = catalog.search(
    collections=['sentinel-2-c1-l2a'],
    bbox=bbox,                          # or intersects=geometry
    datetime='2023',                    # year, range '2023-01/2023-06', or ISO datetime
    query={
        'eo:cloud_cover': {'lt': 30},
        's2:nodata_pixel_percentage': {'lt': 10},
    },
    sortby=[{'field': 'properties.eo:cloud_cover', 'direction': 'asc'}]
)
items = search.item_collection()
```

When searching for a dataset, search the STAC Catalogs to fetch names and descriptions.

Key STAC Catalogs:
- Earth Search: `https://earth-search.aws.element84.com/v1/`
- Microsoft Planetary Computer: `https://planetarycomputer.microsoft.com/api/stac/v1/`
- NASA CMR: `https://cmr.earthdata.nasa.gov/cloudstac/`
- OpenLandMap: `https://s3.eu-central-1.wasabisys.com/stac/openlandmap/catalog.json`

If the dataset is not in the above, search `https://stacindex.org/catalogs`.

---

## Loading STAC Items to XArray

```python
ds = load(
    items,
    bands=['red', 'green', 'blue', 'nir', 'scl'],
    resolution=10,
    crs='utm',           # auto-selects UTM zone for the region
    bbox=bbox,           # always pass bbox to limit data loaded
    chunks={'x': 1024, 'y': 1024},  # Explicitly define chunk sizes
    groupby='solar_day', # deduplicates scenes from same day
    preserve_original_order=True,  # keeps search sort order
    # patch_url=pc.sign  # for Planetary Computer only
)
```

**Do not use `chunks={}` and then call `.rechunk()` — set explicit chunks in `load()` for large datasets.**

---

## Sentinel-2 Preprocessing

Always apply in this order after loading:

```python
# 1. Mask nodata (S2 uses 0 as nodata)
ds = ds.where(ds != 0)

# 2. Apply scale/offset to spectral bands (post Jan 25 2022 scenes)
scale = 0.0001
offset = -0.1
data_bands = [b for b in ds.data_vars if b != 'scl']
for band in data_bands:
    ds[band] = ds[band] * scale + offset

# 3. Apply cloud mask using SCL band
# SCL classes to mask: 3=cloud shadow, 8=cloud medium, 9=cloud high, 10=cirrus
cloud_mask = ds.scl.isin([3, 8, 9, 10])
ds = ds[data_bands].where(~cloud_mask)
```

---

## Spectral Indices

```python
scene_da = ds.to_array('band')  # Dataset -> DataArray with 'band' dim

red    = scene_da.sel(band='red')
nir    = scene_da.sel(band='nir')
green  = scene_da.sel(band='green')
swir16 = scene_da.sel(band='swir16')

ndvi  = (nir - red) / (nir + red)
mndwi = (green - swir16) / (green + swir16)
savi  = 1.5 * ((nir - red) / (nir + red + 0.5))

# Add back to dataset as a variable
ds['ndvi'] = ndvi
```

---

## Median Composite

```python
median = ds.median(dim='time')          # lazy
rgb = median[['red', 'green', 'blue']]
rgb = rgb.compute()                     # triggers Dask computation
```

---

## Visualization

Always convert Dataset to DataArray before plotting:

```python
da = rgb.to_array('band')

# Downsampled preview (avoid plotting full-resolution)
preview = da.rio.reproject(da.rio.crs, resolution=300)

fig, ax = plt.subplots(1, 1)
fig.set_size_inches(5, 5)
preview.sel(band=['red', 'green', 'blue']).plot.imshow(
    ax=ax,
    robust=True,   # 2nd-98th percentile stretch; or use vmin/vmax=0,0.3
)
ax.set_axis_off()
ax.set_aspect('equal')
ax.set_title('...')
plt.show()
```

Manual percentile stretch:

```python
vmin, vmax = np.nanpercentile(preview.values, (1, 95))
```

---

## Time-Series Extraction at a Point

```python
import pyproj

# Convert lat/lon to dataset CRS
transformer = pyproj.Transformer.from_crs('EPSG:4326', ds.rio.crs, always_xy=True)
x, y = transformer.transform(longitude, latitude)

# Lazy nearest-pixel query (no compute yet)
ts = ds['ndvi'].interp(y=y, x=x, method='nearest')
ts = ts.compute()

# Resample + interpolate gaps + smooth
ts_resampled = ts.resample(time='5d').mean().chunk({'time': -1})
ts_interpolated = ts_resampled.interpolate_na('time', use_coordinate=False)
ts_smoothed = ts_interpolated.rolling(time=3, min_periods=1, center=True).mean()
```

---

## DuckDB — Querying Cloud-Native Vector Data

```python
import duckdb
con = duckdb.connect()
con.install_extension('spatial')
con.load_extension('spatial')

# Query a remote GeoParquet/Parquet file without downloading it
query = '''
SELECT adm2_name, ST_AsWKB(geometry) AS geometry
FROM read_parquet('https://...')
WHERE country = 'USA' AND adm1_name = 'California'
'''
df = con.sql(query).df()

# Convert result to GeoDataFrame
gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.GeoSeries.from_wkb(df['geometry'].apply(bytes)),
    crs='EPSG:4326'
)
```

Overture Maps city boundary query pattern:

```python
OVERTURE_RELEASE = '2026-05-20.0'
s3_path = f's3://overturemaps-us-west-2/release/{OVERTURE_RELEASE}/theme=divisions/type=division_area/*'
query = f"""
  SELECT id, names.primary AS primary_name, subtype,
         country, region, ST_AsWKB(geometry) AS geometry
  FROM read_parquet('{s3_path}', filename=true, hive_partitioning=1)
  WHERE subtype IN ('locality', 'county', 'localadmin')
    AND country = 'IN' AND region = 'IN-KA'
    AND names.primary ILIKE 'Bengaluru'
    AND is_land = true
  ORDER BY CASE subtype WHEN 'locality' THEN 0 ELSE 1 END
  LIMIT 1
"""
```

---

## Reclassifying/Remapping a Raster

Use `xrspatial.classify.reclassify` for reclassifying landcover data. Bins define **upper bounds** — each value falling in `(prev_bin, bin]` is mapped to the corresponding `new_value`. NaN is preserved automatically.

```python
from xrspatial.classify import reclassify
import numpy as np

# bins: sorted upper bounds; new_values: output class for each bin
bins =       [20,  92, 122, 130, 140, 153, 183, 184, 185, 187, 190, 202, 210, np.inf]
new_values = [40,  10,  20,  30, 100,  60,  90,  60,  95,  90,  50,  60,  80,     70]

reclassified = reclassify(da, bins=bins, new_values=new_values, name='reclassify')
```

- `len(bins)` must equal `len(new_values)`.
- Use `np.inf` as the last bin to catch all remaining values.
- Gaps between class values (e.g. values that don't exist in the data) are harmless — they just fall into the nearest bin range.

---

## Calculating Area from a Landcover Raster

```python
import numpy as np

# For small regions: use .values directly
data = map_data_clipped.values
bins = unique_class_values + [unique_class_values[-1] + 1]
counts, _ = np.histogram(data, bins=bins)

# For large regions: use Dask histogram (avoids OOM)
import dask.array as da
dask_arr = map_data.data
counts, _ = da.histogram(dask_arr, bins=bins)
counts = counts.compute()

pixel_area_m2 = resolution_m ** 2
area_df = pd.DataFrame({'class_value': unique_class_values, 'area_m2': counts * pixel_area_m2})
```

---

## Zonal Statistics

```python
import xvec, exactextract

# Reproject polygons to raster CRS first
zones_reproj = zones_gdf.to_crs(raster_da.rio.crs)

# Clip raster to bounds (window-reads COG, stays lazy)
bounds = zones_reproj.total_bounds
raster_clipped = raster_da.rio.clip_box(*bounds)

# Compute zonal stats
aggregated = raster_clipped.xvec.zonal_stats(
    zones_reproj.geometry,
    x_coords='x', y_coords='y',
    stats=['sum'],          # or 'mean', 'max', etc.
    method='exactextract'
)

# Convert back to GeoDataFrame
result_gdf = aggregated.xvec.to_geodataframe(name='value', geometry='geometry')
```

---

## Supervised Classification (Satellite Embeddings)

```python
from aef_loader import AEFIndex, VirtualTiffReader, DataSource
from aef_loader.utils import dequantize_aef, reproject_datatree
from odc.geo.geobox import GeoBox
from sklearn.neighbors import KNeighborsClassifier
import dask.array as da

# Load AlphaEarth Foundations embeddings
index = AEFIndex(source=DataSource.SOURCE_COOP)
await index.download()
tiles = await index.query(bbox=bbox, years=(year,))
async with VirtualTiffReader() as reader:
    tree = await reader.open_tiles_by_zone(tiles)
combined = reproject_datatree(tree, target_geobox=geobox)
embeddings = dequantize_aef(combined.embeddings.isel(time=0))

# Extract embeddings at training points (GCPs)
gcp_embeddings = embeddings.sel(
    x=xr.DataArray(gcp_x_coords, dims='gcp_id'),
    y=xr.DataArray(gcp_y_coords, dims='gcp_id'),
    method='nearest'
).compute()

# Train kNN classifier (good for small labeled datasets)
X = gcp_embeddings.values.T   # (n_samples, n_features)
y = gcp_labels
clf = KNeighborsClassifier(n_neighbors=5, weights='distance', n_jobs=1)
clf.fit(X, y)

# Apply to full image via Dask map_blocks
emb_dask = da.moveaxis(embeddings.data, 0, -1)   # (y, x, bands)
ny, nx, nb = emb_dask.shape
emb_2d = emb_dask.reshape(-1, nb).rechunk({0: 'auto', 1: -1})

predicted_1d = emb_2d.map_blocks(
    lambda block, clf: clf.predict(block),
    clf=clf, dtype=np.int32, drop_axis=1
)
predicted = xr.DataArray(
    predicted_1d.reshape(ny, nx),
    coords={'y': embeddings.y, 'x': embeddings.x},
    dims=['y', 'x']
).compute()
```

---

## Saving Outputs

```python
# Raw scientific output (preserves reflectance values)
da.rio.to_raster('output.tif', driver='COG')

# Visualized RGBA output (for display/basemaps)
ds_rgb = da.to_dataset(dim='band')
rgba = ds_rgb.odc.to_rgba(vmin=vmin, vmax=vmax)
rgba.odc.write_cog('visualized.tif')
```

---

## Auto-select UTM Zone

```python
import pyproj

bbox = gdf.geometry.total_bounds   # (minx, miny, maxx, maxy)
aoi = pyproj.aoi.AreaOfInterest(*bbox)
utm_crs_list = pyproj.database.query_utm_crs_info(datum_name='WGS 84', area_of_interest=aoi)
utm_crs = pyproj.CRS.from_epsg(utm_crs_list[0].code)
```

---

## Common Gotchas

- Sentinel-2 SCL band must **not** have scale/offset applied — filter it from `data_bands` before scaling.
- `stac.load()` with `chunks={}` gives Dask arrays but without explicit chunk size may OOM on large regions — set `chunks={'x': 1024, 'y': 1024}` explicitely.
- `preserve_original_order=True` in `stac.load()` is needed to keep the sort order from the STAC search (e.g. least-cloudy first).
- After `groupby='solar_day'` the `time` dimension is sorted ascending — use the item timestamp to index the desired scene, not its original position.
- When pre-filtering STAC items from OpenLandMap or similar catalogs, the `bbox` metadata may be unreliable — use `shapely` `.intersects()` to filter items before passing to `stac.load()`.
- `rioxarray` ops (`.clip()`, `.to_raster()`) require the CRS to be set — check `da.rio.crs` before calling these.
