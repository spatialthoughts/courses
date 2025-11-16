### Overview

In this section, we will take a single Sentinel-2 L1C scene downloaded from the [Copernicus Browser](https://dataspace.copernicus.eu/) and learn how to read it using XArray, visualize it and compute spectral indices.

### Setup and Data Download

The following blocks of code will install the required packages and download the datasets to your Colab environment.


```python
%%capture
if 'google.colab' in str(get_ipython()):
  !pip install rioxarray
  !pip install jupyter-server-proxy
```


```python
import os
import matplotlib.pyplot as plt
import xarray as xr
import rioxarray as rxr
import zipfile
import geopandas as gpd
```


```python
from dask.distributed import Client
client = Client()  # set up local cluster on the machine
client
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

s2_scene = 'S2A_MSIL1C_20230212T050931_N0509_R019_T43PGQ_20230212T065641.SAFE.zip'
data_url = 'https://storage.googleapis.com/spatialthoughts-public-data/'

download(data_url + 's2/' + s2_scene)

aoi = 'bangalore.geojson'
download(data_url + aoi)

```

### Data Pre-Processing

We first unzip the zip archive and create a XArray Dataset from the individual band images.




```python
s2_filepath = os.path.join(data_folder, s2_scene)

with zipfile.ZipFile(s2_filepath) as zf:
  zf.extractall(data_folder)
```

Sentinel-2 images come as individual JPEG2000 rasters for each band. The image files are located in the `GRANULE/{SCENE_ID}/IMG_DATA/` subfolder. We find the files and read them using `rioxarray`.


```python
import glob
s2_folder = s2_filepath[:-4]

band_files = {}

for filepath in glob.glob(
    os.path.join(s2_folder, 'GRANULE', '*', 'IMG_DATA', '*B*.jp2')):
  filename = os.path.basename(filepath)
  # Extract the part of the filename containing band name such as 'B01'
  band_name = os.path.splitext(filename)[0].split('_')[-1]
  band_files[band_name] = filepath

band_files
```




    {'B05': 'data/S2A_MSIL1C_20230212T050931_N0509_R019_T43PGQ_20230212T065641.SAFE/GRANULE/L1C_T43PGQ_A039913_20230212T051514/IMG_DATA/T43PGQ_20230212T050931_B05.jp2',
     'B8A': 'data/S2A_MSIL1C_20230212T050931_N0509_R019_T43PGQ_20230212T065641.SAFE/GRANULE/L1C_T43PGQ_A039913_20230212T051514/IMG_DATA/T43PGQ_20230212T050931_B8A.jp2',
     'B07': 'data/S2A_MSIL1C_20230212T050931_N0509_R019_T43PGQ_20230212T065641.SAFE/GRANULE/L1C_T43PGQ_A039913_20230212T051514/IMG_DATA/T43PGQ_20230212T050931_B07.jp2',
     'B01': 'data/S2A_MSIL1C_20230212T050931_N0509_R019_T43PGQ_20230212T065641.SAFE/GRANULE/L1C_T43PGQ_A039913_20230212T051514/IMG_DATA/T43PGQ_20230212T050931_B01.jp2',
     'B12': 'data/S2A_MSIL1C_20230212T050931_N0509_R019_T43PGQ_20230212T065641.SAFE/GRANULE/L1C_T43PGQ_A039913_20230212T051514/IMG_DATA/T43PGQ_20230212T050931_B12.jp2',
     'B10': 'data/S2A_MSIL1C_20230212T050931_N0509_R019_T43PGQ_20230212T065641.SAFE/GRANULE/L1C_T43PGQ_A039913_20230212T051514/IMG_DATA/T43PGQ_20230212T050931_B10.jp2',
     'B08': 'data/S2A_MSIL1C_20230212T050931_N0509_R019_T43PGQ_20230212T065641.SAFE/GRANULE/L1C_T43PGQ_A039913_20230212T051514/IMG_DATA/T43PGQ_20230212T050931_B08.jp2',
     'B06': 'data/S2A_MSIL1C_20230212T050931_N0509_R019_T43PGQ_20230212T065641.SAFE/GRANULE/L1C_T43PGQ_A039913_20230212T051514/IMG_DATA/T43PGQ_20230212T050931_B06.jp2',
     'B04': 'data/S2A_MSIL1C_20230212T050931_N0509_R019_T43PGQ_20230212T065641.SAFE/GRANULE/L1C_T43PGQ_A039913_20230212T051514/IMG_DATA/T43PGQ_20230212T050931_B04.jp2',
     'B09': 'data/S2A_MSIL1C_20230212T050931_N0509_R019_T43PGQ_20230212T065641.SAFE/GRANULE/L1C_T43PGQ_A039913_20230212T051514/IMG_DATA/T43PGQ_20230212T050931_B09.jp2',
     'B02': 'data/S2A_MSIL1C_20230212T050931_N0509_R019_T43PGQ_20230212T065641.SAFE/GRANULE/L1C_T43PGQ_A039913_20230212T051514/IMG_DATA/T43PGQ_20230212T050931_B02.jp2',
     'B11': 'data/S2A_MSIL1C_20230212T050931_N0509_R019_T43PGQ_20230212T065641.SAFE/GRANULE/L1C_T43PGQ_A039913_20230212T051514/IMG_DATA/T43PGQ_20230212T050931_B11.jp2',
     'B03': 'data/S2A_MSIL1C_20230212T050931_N0509_R019_T43PGQ_20230212T065641.SAFE/GRANULE/L1C_T43PGQ_A039913_20230212T051514/IMG_DATA/T43PGQ_20230212T050931_B03.jp2'}



Different Sentinel-2 bands have different spatial resolutions. To put them in the same array, their dimensions must match. So we combine bands of similar resolutions and resample others to match them.

* B04, B03, B02 and B08 = 10m
* B12, B11, B07, B06, B05 and B08A = 20m
* B10, B09, B1 = 60m


```python
b4 = rxr.open_rasterio(python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/band_files['B04'], chunks=True)
b3 = rxr.open_rasterio(python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/band_files['B03'], chunks=True)
b2 = rxr.open_rasterio(python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/band_files['B02'], chunks=True)
b8 = rxr.open_rasterio(python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/band_files['B08'], chunks=True)

stack1 = xr.concat([b4, b3, b2, b8], dim='band').assign_coords(
    band=['B04', 'B03', 'B02', 'B08'])
```


```python
b5 = rxr.open_rasterio(python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/band_files['B05'], chunks=True)
b6 = rxr.open_rasterio(python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/band_files['B07'], chunks=True)
b7= rxr.open_rasterio(python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/band_files['B07'], chunks=True)
b8a = rxr.open_rasterio(python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/band_files['B8A'], chunks=True)
b11 = rxr.open_rasterio(python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/band_files['B11'], chunks=True)
b12 = rxr.open_rasterio(python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/band_files['B12'], chunks=True)

stack2 = xr.concat([b5, b6, b7, b8a, b11, b12], dim='band').assign_coords(
    band=['B05', 'B06', 'B07', 'B8A', 'B11', 'B12'])
```

Now we reproject the bands to match the resolution of the 10m bands using `reproject_match()`


```python
stack2 = stack2.rio.reproject_match(stack1)
```

Both band stacks now have the same resolution and hence the same X and Y dimensions. We can now combine them across the `band` dimension. The Sentinel-2 scenes come with NoData value of 0. So we set the correct NoData value before further processing.


```python
scene = xr.concat([stack1, stack2], dim='band')
scene = scene.where(scene != 0)
scene
```

We will clip the scene to the geometry of the GeoJSON file. We must ensure that the projection of the GeoDataFrame and the XArray DataArray match.


```python
aoi_path = os.path.join(data_folder, aoi)
aoi_gdf = gpd.read_file(aoi_path)
geometry = aoi_gdf.to_crs(scene.rio.crs).geometry
clipped = scene.rio.clip(geometry)
clipped
```

Sentinel-2 pixel values need to be converted to reflectances using the following formula:

`ρ   =  (L1C_DN + RADIO_ADD_OFFSET) / QUANTIFICATION_VALUE`

`QUANTIFICATION_VALUE` for all S2 scenes is **10000** and starting from January 22,2023, all new scenes have a `RADIO_ADD_OFFSET` of **-1000**




```python
scaled = (clipped - 1000)/10000
```

### Visualization

We can visualize a 3-band composite image.


```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(5,5)
scaled.sel(band=['B04', 'B03', 'B02']).plot.imshow(
    ax=ax,
    robust=True)
ax.set_title('RGB Visualization')
ax.set_axis_off()
plt.show()
```


    
![](python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/computing_indices_files/computing_indices_24_0.png)
    



```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(5,5)
scaled.sel(band=['B08', 'B04', 'B03']).plot.imshow(
    ax=ax,
    robust=True)
ax.set_title('NRG Visualization')
ax.set_axis_off()
plt.show()
```


    
![](python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/computing_indices_files/computing_indices_25_0.png)
    


### Calculating Indices


```python
red = scaled.sel(band='B04')
nir = scaled.sel(band='B08')

ndvi = (nir - red)/(nir + red)
```

Let's visualize the results.


```python
cbar_kwargs = {
    'orientation':'horizontal',
    'fraction': 0.025,
    'pad': 0.05,
    'extend':'neither'
}
```


```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(5,5)
ndvi.plot.imshow(
    ax=ax,
    cmap='Greens',
    robust=True,
    cbar_kwargs=cbar_kwargs)
ax.set_title('NDVI')
ax.set_axis_off()
plt.show()
```


    
![](python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/computing_indices_files/computing_indices_30_0.png)
    



```python
green = scaled.sel(band='B03')
swir1 = scaled.sel(band='B11')

mndwi = (green - swir1)/(green + swir1)
```


```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(5,5)
mndwi.plot.imshow(
    ax=ax,
    cmap='Blues',
    robust=True,
    cbar_kwargs=cbar_kwargs)
ax.set_title('MNDWI')
ax.set_axis_off()
plt.show()
```

    /usr/local/lib/python3.10/dist-packages/distributed/client.py:3160: UserWarning: Sending large graph of size 328.52 MiB.
    This may cause some slowdown.
    Consider scattering data ahead of time and using futures.
      warnings.warn(



    
![](python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/computing_indices_files/computing_indices_32_1.png)
    



```python
red = scaled.sel(band='B04')
nir = scaled.sel(band='B08')

savi = 1.5 * ((nir - red) / (nir + red + 0.5))
```


```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(5,5)
savi.plot.imshow(
    ax=ax,
    cmap='Greens',
    robust=True,
    cbar_kwargs=cbar_kwargs)
ax.set_title('SAVI')
ax.set_axis_off()
plt.show()
```


    
![](python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/python-remote-sensing-output/computing_indices_files/computing_indices_34_0.png)
    


### Saving the results


```python
files = {
    'clipped.tif': scaled,
    'ndvi.tif': ndvi,
    'mndwi.tif': mndwi,
    'savi.tif': savi
}

for file in files:
  output_path = os.path.join(output_folder, file)
  files[file].rio.to_raster(output_path, driver='COG')
```

### Exercise

Calculate the Normalized Difference Built-Up Index (NDBI) for the image and visualize the built-up area using a 'red' palette

Hint: `NDBI = (SWIR1 – NIR) / (SWIR1 + NIR)`

