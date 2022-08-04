# Visualizing Rasters

[Xarray](http://xarray.pydata.org/) is an evolution of rasterio and is inspired by libraries like pandas to work with raster datasets. It is particularly suited for working with multi-dimensional time-series raster datasets. It also integrates tightly with [dask](https://dask.org/) that allows one to scale raster data processing using parallel computing.

[rioxarray](https://corteva.github.io/rioxarray/stable/index.html) is an extension of xarray that makes it easy to work with geospatial rasters. You can install the `rioxarray` package from the `conda-forge` channel. 

This notebook shows how we can replicate the analysis from the [Working with RasterIO](#working-with-rasterio) exercise and also covers raster data visualization using `matplotlib`. 

### XArray and rioxarray Basics

We start by reading a single SRTM tile containing elevation values.


```python
import os
import numpy as np
data_pkg_path = 'data'
srtm_dir = 'srtm'
filename = 'N28E087.hgt'
path = os.path.join(data_pkg_path, srtm_dir, filename)
```

By convention, `rioxarray` is imported as `rxr`


```python
import rioxarray as rxr
```

The `open_rasterio()` method is able to read any data source supported by `rasterio` library.


```python
rds = rxr.open_rasterio(path)
```

The result is a `xarray.DataArray` object.


```python
type(rds)
```




    xarray.core.dataarray.DataArray



You can access the pixel values using the `values` property which returns the array’s data as a numpy array.


```python
rds.values
```




    array([[[5217, 5211, 5208, ..., 5097, 5098, 5089],
            [5206, 5201, 5200, ..., 5080, 5075, 5069],
            [5199, 5194, 5191, ..., 5063, 5055, 5048],
            ...,
            [5347, 5345, 5343, ..., 5747, 5750, 5757],
            [5338, 5338, 5336, ..., 5737, 5740, 5747],
            [5332, 5331, 5332, ..., 5734, 5736, 5744]]], dtype=int16)



A `xarray.DataArray` object also contains 1 or more `coordinates`. Each coordinate is a 1-dimensional array representing values along one of the data axes. In case of the 1-band SRTM elevation data, we have 3 coordinates - `x`, `y` and `band`.


```python
rds.coords
```




    Coordinates:
      * band         (band) int64 1
      * x            (x) float64 87.0 87.0 87.0 87.0 87.0 ... 88.0 88.0 88.0 88.0
      * y            (y) float64 29.0 29.0 29.0 29.0 29.0 ... 28.0 28.0 28.0 28.0
        spatial_ref  int64 0



A key feature of `xarray` is the ability to access slices of the dataset using [index lookup](http://xarray.pydata.org/en/stable/user-guide/indexing.html) methods. For example, we can slice the main dataset and get the data for Band1 using the `sel()` method.


```python
band1 = rds.sel(band=1)
```

The raster metadata is stored in the [`rio`](https://corteva.github.io/rioxarray/stable/rioxarray.html#rioxarray-rio-accessors) accessor. This is enabled by the `rioxarray` library which provides geospatial functions on top of `xarray`. 


```python
print('CRS:', rds.rio.crs)
print('Resolution:', rds.rio.resolution())
print('Bounds:', rds.rio.bounds())
print('Width:', rds.rio.width)
print('Height:', rds.rio.height)
```

    CRS: EPSG:4326
    Resolution: (0.0002777777777777778, -0.0002777777777777778)
    Bounds: (86.99986111111112, 27.999861111111112, 88.00013888888888, 29.000138888888888)
    Width: 3601
    Height: 3601


### Merging Rasters

Now that you understand the basic data structure of *xarray* and the &rio* extension, let's use it to process some data. We will take 4 individual SRTM tiles and merge them to a single GeoTiff. You will note that `rioxarray` handles the CRS and transform much better - taking care of internal details and providing a simple API.

> Remember to always import `rioxarray` even if you are using sub-modules. Importing `rioxarray` activates the `rio` accessor which is required for all operations.


```python
import rioxarray as rxr
from rioxarray.merge import merge_arrays
```

Define input and output paths.


```python
srtm_path = os.path.join(data_pkg_path, 'srtm')
all_files = os.listdir(srtm_path)
output_filename = 'merged.tif'
output_dir = 'output'
output_path = os.path.join(output_dir, output_filename)
```

Open each source file using `open_rasterio()` method and store the resulting datasets in a list.


```python
datasets = []
for file in all_files:
    path = os.path.join(srtm_path, file)
    datasets.append(rxr.open_rasterio(path))
```

Use the `merge_arrays()` method from the `rioxarray.merge` module to merge the rasters.


```python
merged = merge_arrays(datasets)
```

Finally, save the merged array to disk as a GeoTiff file.


```python
merged.rio.to_raster(output_path)
```

### Visualizing Rasters using Matplotlib

`xarray` plotting functionality is built on top of the the popular `matplotlib` library. 


```python
%matplotlib inline
import matplotlib.pyplot as plt
```

You cna visualize any `DataArray` object by calling `plot()` method. Here we create a row of 4 plots and render each of the source SRTM rasters. We can use the `cmap` option to specify a color ramp. Here we are using the built-in *Greys* ramp. Appending **_r** gives us the inverted ramp with blacks representing lower elevation values.


```python
fig, axes = plt.subplots(1, 4)
fig.set_size_inches(15,3)
plt.tight_layout()
for index, dataset in enumerate(datasets):
    ax = axes[index]
    dataset.plot(ax=ax, cmap='Greys_r')
    ax.axis('off')
    filename = all_files[index]
    ax.set_title(filename)
```


    
![](python-dataviz-output/python-dataviz-output/06_visualizing_rasters_files/06_visualizing_rasters_32_0.png)
    


Similarly, we can visualize the merged raster.


```python
fig, ax = plt.subplots()
fig.set_size_inches(12, 10)
merged.plot(ax=ax, cmap='Greys_r')
ax.set_title('merged')
plt.show()
```


    
![](python-dataviz-output/python-dataviz-output/06_visualizing_rasters_files/06_visualizing_rasters_34_0.png)
    



```python
merged
```




<div><svg style="position: absolute; width: 0; height: 0; overflow: hidden">
<defs>
<symbol id="icon-database" viewBox="0 0 32 32">
<path d="M16 0c-8.837 0-16 2.239-16 5v4c0 2.761 7.163 5 16 5s16-2.239 16-5v-4c0-2.761-7.163-5-16-5z"></path>
<path d="M16 17c-8.837 0-16-2.239-16-5v6c0 2.761 7.163 5 16 5s16-2.239 16-5v-6c0 2.761-7.163 5-16 5z"></path>
<path d="M16 26c-8.837 0-16-2.239-16-5v6c0 2.761 7.163 5 16 5s16-2.239 16-5v-6c0 2.761-7.163 5-16 5z"></path>
</symbol>
<symbol id="icon-file-text2" viewBox="0 0 32 32">
<path d="M28.681 7.159c-0.694-0.947-1.662-2.053-2.724-3.116s-2.169-2.030-3.116-2.724c-1.612-1.182-2.393-1.319-2.841-1.319h-15.5c-1.378 0-2.5 1.121-2.5 2.5v27c0 1.378 1.122 2.5 2.5 2.5h23c1.378 0 2.5-1.122 2.5-2.5v-19.5c0-0.448-0.137-1.23-1.319-2.841zM24.543 5.457c0.959 0.959 1.712 1.825 2.268 2.543h-4.811v-4.811c0.718 0.556 1.584 1.309 2.543 2.268zM28 29.5c0 0.271-0.229 0.5-0.5 0.5h-23c-0.271 0-0.5-0.229-0.5-0.5v-27c0-0.271 0.229-0.5 0.5-0.5 0 0 15.499-0 15.5 0v7c0 0.552 0.448 1 1 1h7v19.5z"></path>
<path d="M23 26h-14c-0.552 0-1-0.448-1-1s0.448-1 1-1h14c0.552 0 1 0.448 1 1s-0.448 1-1 1z"></path>
<path d="M23 22h-14c-0.552 0-1-0.448-1-1s0.448-1 1-1h14c0.552 0 1 0.448 1 1s-0.448 1-1 1z"></path>
<path d="M23 18h-14c-0.552 0-1-0.448-1-1s0.448-1 1-1h14c0.552 0 1 0.448 1 1s-0.448 1-1 1z"></path>
</symbol>
</defs>
</svg>
<style>/* CSS stylesheet for displaying xarray objects in jupyterlab.
 *
 */

:root {
  --xr-font-color0: var(--jp-content-font-color0, rgba(0, 0, 0, 1));
  --xr-font-color2: var(--jp-content-font-color2, rgba(0, 0, 0, 0.54));
  --xr-font-color3: var(--jp-content-font-color3, rgba(0, 0, 0, 0.38));
  --xr-border-color: var(--jp-border-color2, #e0e0e0);
  --xr-disabled-color: var(--jp-layout-color3, #bdbdbd);
  --xr-background-color: var(--jp-layout-color0, white);
  --xr-background-color-row-even: var(--jp-layout-color1, white);
  --xr-background-color-row-odd: var(--jp-layout-color2, #eeeeee);
}

html[theme=dark],
body[data-theme=dark],
body.vscode-dark {
  --xr-font-color0: rgba(255, 255, 255, 1);
  --xr-font-color2: rgba(255, 255, 255, 0.54);
  --xr-font-color3: rgba(255, 255, 255, 0.38);
  --xr-border-color: #1F1F1F;
  --xr-disabled-color: #515151;
  --xr-background-color: #111111;
  --xr-background-color-row-even: #111111;
  --xr-background-color-row-odd: #313131;
}

.xr-wrap {
  display: block !important;
  min-width: 300px;
  max-width: 700px;
}

.xr-text-repr-fallback {
  /* fallback to plain text repr when CSS is not injected (untrusted notebook) */
  display: none;
}

.xr-header {
  padding-top: 6px;
  padding-bottom: 6px;
  margin-bottom: 4px;
  border-bottom: solid 1px var(--xr-border-color);
}

.xr-header > div,
.xr-header > ul {
  display: inline;
  margin-top: 0;
  margin-bottom: 0;
}

.xr-obj-type,
.xr-array-name {
  margin-left: 2px;
  margin-right: 10px;
}

.xr-obj-type {
  color: var(--xr-font-color2);
}

.xr-sections {
  padding-left: 0 !important;
  display: grid;
  grid-template-columns: 150px auto auto 1fr 20px 20px;
}

.xr-section-item {
  display: contents;
}

.xr-section-item input {
  display: none;
}

.xr-section-item input + label {
  color: var(--xr-disabled-color);
}

.xr-section-item input:enabled + label {
  cursor: pointer;
  color: var(--xr-font-color2);
}

.xr-section-item input:enabled + label:hover {
  color: var(--xr-font-color0);
}

.xr-section-summary {
  grid-column: 1;
  color: var(--xr-font-color2);
  font-weight: 500;
}

.xr-section-summary > span {
  display: inline-block;
  padding-left: 0.5em;
}

.xr-section-summary-in:disabled + label {
  color: var(--xr-font-color2);
}

.xr-section-summary-in + label:before {
  display: inline-block;
  content: '►';
  font-size: 11px;
  width: 15px;
  text-align: center;
}

.xr-section-summary-in:disabled + label:before {
  color: var(--xr-disabled-color);
}

.xr-section-summary-in:checked + label:before {
  content: '▼';
}

.xr-section-summary-in:checked + label > span {
  display: none;
}

.xr-section-summary,
.xr-section-inline-details {
  padding-top: 4px;
  padding-bottom: 4px;
}

.xr-section-inline-details {
  grid-column: 2 / -1;
}

.xr-section-details {
  display: none;
  grid-column: 1 / -1;
  margin-bottom: 5px;
}

.xr-section-summary-in:checked ~ .xr-section-details {
  display: contents;
}

.xr-array-wrap {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: 20px auto;
}

.xr-array-wrap > label {
  grid-column: 1;
  vertical-align: top;
}

.xr-preview {
  color: var(--xr-font-color3);
}

.xr-array-preview,
.xr-array-data {
  padding: 0 5px !important;
  grid-column: 2;
}

.xr-array-data,
.xr-array-in:checked ~ .xr-array-preview {
  display: none;
}

.xr-array-in:checked ~ .xr-array-data,
.xr-array-preview {
  display: inline-block;
}

.xr-dim-list {
  display: inline-block !important;
  list-style: none;
  padding: 0 !important;
  margin: 0;
}

.xr-dim-list li {
  display: inline-block;
  padding: 0;
  margin: 0;
}

.xr-dim-list:before {
  content: '(';
}

.xr-dim-list:after {
  content: ')';
}

.xr-dim-list li:not(:last-child):after {
  content: ',';
  padding-right: 5px;
}

.xr-has-index {
  font-weight: bold;
}

.xr-var-list,
.xr-var-item {
  display: contents;
}

.xr-var-item > div,
.xr-var-item label,
.xr-var-item > .xr-var-name span {
  background-color: var(--xr-background-color-row-even);
  margin-bottom: 0;
}

.xr-var-item > .xr-var-name:hover span {
  padding-right: 5px;
}

.xr-var-list > li:nth-child(odd) > div,
.xr-var-list > li:nth-child(odd) > label,
.xr-var-list > li:nth-child(odd) > .xr-var-name span {
  background-color: var(--xr-background-color-row-odd);
}

.xr-var-name {
  grid-column: 1;
}

.xr-var-dims {
  grid-column: 2;
}

.xr-var-dtype {
  grid-column: 3;
  text-align: right;
  color: var(--xr-font-color2);
}

.xr-var-preview {
  grid-column: 4;
}

.xr-var-name,
.xr-var-dims,
.xr-var-dtype,
.xr-preview,
.xr-attrs dt {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding-right: 10px;
}

.xr-var-name:hover,
.xr-var-dims:hover,
.xr-var-dtype:hover,
.xr-attrs dt:hover {
  overflow: visible;
  width: auto;
  z-index: 1;
}

.xr-var-attrs,
.xr-var-data {
  display: none;
  background-color: var(--xr-background-color) !important;
  padding-bottom: 5px !important;
}

.xr-var-attrs-in:checked ~ .xr-var-attrs,
.xr-var-data-in:checked ~ .xr-var-data {
  display: block;
}

.xr-var-data > table {
  float: right;
}

.xr-var-name span,
.xr-var-data,
.xr-attrs {
  padding-left: 25px !important;
}

.xr-attrs,
.xr-var-attrs,
.xr-var-data {
  grid-column: 1 / -1;
}

dl.xr-attrs {
  padding: 0;
  margin: 0;
  display: grid;
  grid-template-columns: 125px auto;
}

.xr-attrs dt,
.xr-attrs dd {
  padding: 0;
  margin: 0;
  float: left;
  padding-right: 10px;
  width: auto;
}

.xr-attrs dt {
  font-weight: normal;
  grid-column: 1;
}

.xr-attrs dt:hover span {
  display: inline-block;
  background: var(--xr-background-color);
  padding-right: 10px;
}

.xr-attrs dd {
  grid-column: 2;
  white-space: pre-wrap;
  word-break: break-all;
}

.xr-icon-database,
.xr-icon-file-text2 {
  display: inline-block;
  vertical-align: middle;
  width: 1em;
  height: 1.5em !important;
  stroke-width: 0;
  stroke: currentColor;
  fill: currentColor;
}
</style><pre class='xr-text-repr-fallback'>&lt;xarray.DataArray (band: 1, y: 7201, x: 7201)&gt;
array([[[4916, 4926, 4931, ..., 5097, 5098, 5089],
        [4919, 4932, 4928, ..., 5080, 5075, 5069],
        [4919, 4928, 4935, ..., 5063, 5055, 5048],
        ...,
        [ 368,  368,  366, ..., 1905, 1919, 1937],
        [ 364,  364,  362, ..., 1913, 1930, 1944],
        [ 360,  359,  357, ..., 1918, 1930, 1942]]], dtype=int16)
Coordinates:
  * x            (x) float64 86.0 86.0 86.0 86.0 86.0 ... 88.0 88.0 88.0 88.0
  * y            (y) float64 29.0 29.0 29.0 29.0 29.0 ... 27.0 27.0 27.0 27.0
  * band         (band) int64 1
    spatial_ref  int64 0
Attributes:
    _FillValue:    -32768
    scale_factor:  1.0
    add_offset:    0.0
    units:         m</pre><div class='xr-wrap' style='display:none'><div class='xr-header'><div class='xr-obj-type'>xarray.DataArray</div><div class='xr-array-name'></div><ul class='xr-dim-list'><li><span class='xr-has-index'>band</span>: 1</li><li><span class='xr-has-index'>y</span>: 7201</li><li><span class='xr-has-index'>x</span>: 7201</li></ul></div><ul class='xr-sections'><li class='xr-section-item'><div class='xr-array-wrap'><input id='section-7c0ff821-f71f-4fcf-acc3-549fa0df4f42' class='xr-array-in' type='checkbox' checked><label for='section-7c0ff821-f71f-4fcf-acc3-549fa0df4f42' title='Show/hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-array-preview xr-preview'><span>4916 4926 4931 4929 4929 4931 4934 ... 1877 1887 1904 1918 1930 1942</span></div><div class='xr-array-data'><pre>array([[[4916, 4926, 4931, ..., 5097, 5098, 5089],
        [4919, 4932, 4928, ..., 5080, 5075, 5069],
        [4919, 4928, 4935, ..., 5063, 5055, 5048],
        ...,
        [ 368,  368,  366, ..., 1905, 1919, 1937],
        [ 364,  364,  362, ..., 1913, 1930, 1944],
        [ 360,  359,  357, ..., 1918, 1930, 1942]]], dtype=int16)</pre></div></div></li><li class='xr-section-item'><input id='section-139aed7f-43e2-44e5-8a0c-e410896cd9ee' class='xr-section-summary-in' type='checkbox'  checked><label for='section-139aed7f-43e2-44e5-8a0c-e410896cd9ee' class='xr-section-summary' >Coordinates: <span>(4)</span></label><div class='xr-section-inline-details'></div><div class='xr-section-details'><ul class='xr-var-list'><li class='xr-var-item'><div class='xr-var-name'><span class='xr-has-index'>x</span></div><div class='xr-var-dims'>(x)</div><div class='xr-var-dtype'>float64</div><div class='xr-var-preview xr-preview'>86.0 86.0 86.0 ... 88.0 88.0 88.0</div><input id='attrs-cbe3d953-dcf5-47e2-8d34-7d4c4d5efcaa' class='xr-var-attrs-in' type='checkbox' disabled><label for='attrs-cbe3d953-dcf5-47e2-8d34-7d4c4d5efcaa' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-bd160714-dbab-41ab-b311-5f60587a2ac3' class='xr-var-data-in' type='checkbox'><label for='data-bd160714-dbab-41ab-b311-5f60587a2ac3' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'></dl></div><div class='xr-var-data'><pre>array([86.      , 86.000278, 86.000556, ..., 87.999444, 87.999722, 88.      ])</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span class='xr-has-index'>y</span></div><div class='xr-var-dims'>(y)</div><div class='xr-var-dtype'>float64</div><div class='xr-var-preview xr-preview'>29.0 29.0 29.0 ... 27.0 27.0 27.0</div><input id='attrs-a854fbda-b0df-4bf8-919c-491d6805ffef' class='xr-var-attrs-in' type='checkbox' disabled><label for='attrs-a854fbda-b0df-4bf8-919c-491d6805ffef' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-f0ce5441-82da-4315-8e98-c02d6c8e375a' class='xr-var-data-in' type='checkbox'><label for='data-f0ce5441-82da-4315-8e98-c02d6c8e375a' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'></dl></div><div class='xr-var-data'><pre>array([29.      , 28.999722, 28.999444, ..., 27.000556, 27.000278, 27.      ])</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span class='xr-has-index'>band</span></div><div class='xr-var-dims'>(band)</div><div class='xr-var-dtype'>int64</div><div class='xr-var-preview xr-preview'>1</div><input id='attrs-8553d860-d248-4d55-bc25-54aaf9585420' class='xr-var-attrs-in' type='checkbox' disabled><label for='attrs-8553d860-d248-4d55-bc25-54aaf9585420' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-01c44796-4321-44e4-a4df-7063c8b14840' class='xr-var-data-in' type='checkbox'><label for='data-01c44796-4321-44e4-a4df-7063c8b14840' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'></dl></div><div class='xr-var-data'><pre>array([1])</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span>spatial_ref</span></div><div class='xr-var-dims'>()</div><div class='xr-var-dtype'>int64</div><div class='xr-var-preview xr-preview'>0</div><input id='attrs-f0f2c514-2ee3-4610-a838-dd78366230e7' class='xr-var-attrs-in' type='checkbox' ><label for='attrs-f0f2c514-2ee3-4610-a838-dd78366230e7' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-332820ac-21b8-45b6-ad53-c29b5d4d61e9' class='xr-var-data-in' type='checkbox'><label for='data-332820ac-21b8-45b6-ad53-c29b5d4d61e9' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'><dt><span>crs_wkt :</span></dt><dd>GEOGCS[&quot;WGS 84&quot;,DATUM[&quot;WGS_1984&quot;,SPHEROID[&quot;WGS 84&quot;,6378137,298.257223563,AUTHORITY[&quot;EPSG&quot;,&quot;7030&quot;]],AUTHORITY[&quot;EPSG&quot;,&quot;6326&quot;]],PRIMEM[&quot;Greenwich&quot;,0,AUTHORITY[&quot;EPSG&quot;,&quot;8901&quot;]],UNIT[&quot;degree&quot;,0.0174532925199433,AUTHORITY[&quot;EPSG&quot;,&quot;9122&quot;]],AXIS[&quot;Latitude&quot;,NORTH],AXIS[&quot;Longitude&quot;,EAST],AUTHORITY[&quot;EPSG&quot;,&quot;4326&quot;]]</dd><dt><span>semi_major_axis :</span></dt><dd>6378137.0</dd><dt><span>semi_minor_axis :</span></dt><dd>6356752.314245179</dd><dt><span>inverse_flattening :</span></dt><dd>298.257223563</dd><dt><span>reference_ellipsoid_name :</span></dt><dd>WGS 84</dd><dt><span>longitude_of_prime_meridian :</span></dt><dd>0.0</dd><dt><span>prime_meridian_name :</span></dt><dd>Greenwich</dd><dt><span>geographic_crs_name :</span></dt><dd>WGS 84</dd><dt><span>grid_mapping_name :</span></dt><dd>latitude_longitude</dd><dt><span>spatial_ref :</span></dt><dd>GEOGCS[&quot;WGS 84&quot;,DATUM[&quot;WGS_1984&quot;,SPHEROID[&quot;WGS 84&quot;,6378137,298.257223563,AUTHORITY[&quot;EPSG&quot;,&quot;7030&quot;]],AUTHORITY[&quot;EPSG&quot;,&quot;6326&quot;]],PRIMEM[&quot;Greenwich&quot;,0,AUTHORITY[&quot;EPSG&quot;,&quot;8901&quot;]],UNIT[&quot;degree&quot;,0.0174532925199433,AUTHORITY[&quot;EPSG&quot;,&quot;9122&quot;]],AXIS[&quot;Latitude&quot;,NORTH],AXIS[&quot;Longitude&quot;,EAST],AUTHORITY[&quot;EPSG&quot;,&quot;4326&quot;]]</dd><dt><span>GeoTransform :</span></dt><dd>85.99986111111112 0.0002777777777777778 0.0 29.000138888888888 0.0 -0.0002777777777777778</dd></dl></div><div class='xr-var-data'><pre>array(0)</pre></div></li></ul></div></li><li class='xr-section-item'><input id='section-1ecde97f-b58f-4774-90d7-6800bfce2b45' class='xr-section-summary-in' type='checkbox'  checked><label for='section-1ecde97f-b58f-4774-90d7-6800bfce2b45' class='xr-section-summary' >Attributes: <span>(4)</span></label><div class='xr-section-inline-details'></div><div class='xr-section-details'><dl class='xr-attrs'><dt><span>_FillValue :</span></dt><dd>-32768</dd><dt><span>scale_factor :</span></dt><dd>1.0</dd><dt><span>add_offset :</span></dt><dd>0.0</dd><dt><span>units :</span></dt><dd>m</dd></dl></div></li></ul></div></div>




```python
bands, rows, cols = np.where(merged == np.max(merged))
band = bands[0]
row = rows[0]
col = cols[0]
print(band, row, col)
```

    0 3640 3332



```python
result = merged.isel(band=band, x=col, y=row)
lat = result.y.values
lon = result.x.values
elevation = int(result)
print(lat, lon, elevation)
```

    27.988888888888887 86.92555555555556 8748



```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(12, 12)
merged.plot(ax=ax, cmap='viridis')
ax.plot(lon, lat, '^r', markersize=11)
ax.annotate('Mt. Everest (elevation:{}m)'.format(elevation),
            xy=(lon, lat), xycoords='data',
            xytext=(20, 20), textcoords='offset points',
            arrowprops=dict(arrowstyle='->', color='black')
            )

output_folder = 'output'
output_path = os.path.join(output_folder, 'mt_everest.png')
plt.savefig(output_path, dpi=300)

plt.show()
```


    
![](python-dataviz-output/python-dataviz-output/06_visualizing_rasters_files/06_visualizing_rasters_38_0.png)
    

