### Overview
Spectral indices are core to many remote sensing analysis. In this section, we will learn how can we perform calculations using XArray.

We will take a single Sentinel-2 scene and calculate spectral indices like NDVI, MNDWI and SAVI.

### Setup and Data Download
The following blocks of code will install the required packages and download the datasets to your Colab environment.


```python
%%capture
if 'google.colab' in str(get_ipython()):
    !pip install pystac-client odc-stac rioxarray dask jupyter-server-proxy
```


```python
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import os
import pandas as pd
import pystac_client
import rioxarray as rxr
import xarray as xr
from odc import stac
```


```python
from dask.distributed import Client
client = Client()  # set up local cluster on the machine
client
```

    INFO:distributed.scheduler:State start
    INFO:distributed.scheduler:  Scheduler at:     tcp://127.0.0.1:43679
    INFO:distributed.scheduler:  dashboard at:  http://127.0.0.1:8787/status
    INFO:distributed.scheduler:Registering Worker plugin shuffle
    INFO:distributed.nanny:        Start Nanny at: 'tcp://127.0.0.1:41323'
    INFO:distributed.nanny:        Start Nanny at: 'tcp://127.0.0.1:45735'
    INFO:distributed.scheduler:Register worker addr: tcp://127.0.0.1:44307 name: 1
    INFO:distributed.scheduler:Starting worker compute stream, tcp://127.0.0.1:44307
    INFO:distributed.core:Starting established connection to tcp://127.0.0.1:37432
    INFO:distributed.scheduler:Register worker addr: tcp://127.0.0.1:45943 name: 0
    INFO:distributed.scheduler:Starting worker compute stream, tcp://127.0.0.1:45943
    INFO:distributed.core:Starting established connection to tcp://127.0.0.1:37440
    INFO:distributed.scheduler:Receive client connection: Client-9646bf49-c17e-11f0-8db5-0242ac1c000c
    INFO:distributed.core:Starting established connection to tcp://127.0.0.1:37448





<div>
    <div style="width: 24px; height: 24px; background-color: #e1e1e1; border: 3px solid #9D9D9D; border-radius: 5px; position: absolute;"> </div>
    <div style="margin-left: 48px;">
        <h3 style="margin-bottom: 0px;">Client</h3>
        <p style="color: #9D9D9D; margin-bottom: 0px;">Client-9646bf49-c17e-11f0-8db5-0242ac1c000c</p>
        <table style="width: 100%; text-align: left;">

        <tr>

            <td style="text-align: left;"><strong>Connection method:</strong> Cluster object</td>
            <td style="text-align: left;"><strong>Cluster type:</strong> distributed.LocalCluster</td>

        </tr>


            <tr>
                <td style="text-align: left;">
                    <strong>Dashboard: </strong> <a href="http://127.0.0.1:8787/status" target="_blank">http://127.0.0.1:8787/status</a>
                </td>
                <td style="text-align: left;"></td>
            </tr>


        </table>




            <details>
            <summary style="margin-bottom: 20px;"><h3 style="display: inline;">Cluster Info</h3></summary>
            <div class="jp-RenderedHTMLCommon jp-RenderedHTML jp-mod-trusted jp-OutputArea-output">
    <div style="width: 24px; height: 24px; background-color: #e1e1e1; border: 3px solid #9D9D9D; border-radius: 5px; position: absolute;">
    </div>
    <div style="margin-left: 48px;">
        <h3 style="margin-bottom: 0px; margin-top: 0px;">LocalCluster</h3>
        <p style="color: #9D9D9D; margin-bottom: 0px;">925ff783</p>
        <table style="width: 100%; text-align: left;">
            <tr>
                <td style="text-align: left;">
                    <strong>Dashboard:</strong> <a href="http://127.0.0.1:8787/status" target="_blank">http://127.0.0.1:8787/status</a>
                </td>
                <td style="text-align: left;">
                    <strong>Workers:</strong> 2
                </td>
            </tr>
            <tr>
                <td style="text-align: left;">
                    <strong>Total threads:</strong> 2
                </td>
                <td style="text-align: left;">
                    <strong>Total memory:</strong> 12.67 GiB
                </td>
            </tr>

            <tr>
    <td style="text-align: left;"><strong>Status:</strong> running</td>
    <td style="text-align: left;"><strong>Using processes:</strong> True</td>
</tr>


        </table>

        <details>
            <summary style="margin-bottom: 20px;">
                <h3 style="display: inline;">Scheduler Info</h3>
            </summary>

            <div style="">
    <div>
        <div style="width: 24px; height: 24px; background-color: #FFF7E5; border: 3px solid #FF6132; border-radius: 5px; position: absolute;"> </div>
        <div style="margin-left: 48px;">
            <h3 style="margin-bottom: 0px;">Scheduler</h3>
            <p style="color: #9D9D9D; margin-bottom: 0px;">Scheduler-41139618-478b-4ad0-b1c7-d73fdd6c3367</p>
            <table style="width: 100%; text-align: left;">
                <tr>
                    <td style="text-align: left;">
                        <strong>Comm:</strong> tcp://127.0.0.1:43679
                    </td>
                    <td style="text-align: left;">
                        <strong>Workers:</strong> 0 
                    </td>
                </tr>
                <tr>
                    <td style="text-align: left;">
                        <strong>Dashboard:</strong> <a href="http://127.0.0.1:8787/status" target="_blank">http://127.0.0.1:8787/status</a>
                    </td>
                    <td style="text-align: left;">
                        <strong>Total threads:</strong> 0
                    </td>
                </tr>
                <tr>
                    <td style="text-align: left;">
                        <strong>Started:</strong> Just now
                    </td>
                    <td style="text-align: left;">
                        <strong>Total memory:</strong> 0 B
                    </td>
                </tr>
            </table>
        </div>
    </div>

    <details style="margin-left: 48px;">
        <summary style="margin-bottom: 20px;">
            <h3 style="display: inline;">Workers</h3>
        </summary>


        <div style="margin-bottom: 20px;">
            <div style="width: 24px; height: 24px; background-color: #DBF5FF; border: 3px solid #4CC9FF; border-radius: 5px; position: absolute;"> </div>
            <div style="margin-left: 48px;">
            <details>
                <summary>
                    <h4 style="margin-bottom: 0px; display: inline;">Worker: 0</h4>
                </summary>
                <table style="width: 100%; text-align: left;">
                    <tr>
                        <td style="text-align: left;">
                            <strong>Comm: </strong> tcp://127.0.0.1:45943
                        </td>
                        <td style="text-align: left;">
                            <strong>Total threads: </strong> 1
                        </td>
                    </tr>
                    <tr>
                        <td style="text-align: left;">
                            <strong>Dashboard: </strong> <a href="http://127.0.0.1:37037/status" target="_blank">http://127.0.0.1:37037/status</a>
                        </td>
                        <td style="text-align: left;">
                            <strong>Memory: </strong> 6.34 GiB
                        </td>
                    </tr>
                    <tr>
                        <td style="text-align: left;">
                            <strong>Nanny: </strong> tcp://127.0.0.1:41323
                        </td>
                        <td style="text-align: left;"></td>
                    </tr>
                    <tr>
                        <td colspan="2" style="text-align: left;">
                            <strong>Local directory: </strong> /tmp/dask-scratch-space/worker-__tp8p8k
                        </td>
                    </tr>





                </table>
            </details>
            </div>
        </div>

        <div style="margin-bottom: 20px;">
            <div style="width: 24px; height: 24px; background-color: #DBF5FF; border: 3px solid #4CC9FF; border-radius: 5px; position: absolute;"> </div>
            <div style="margin-left: 48px;">
            <details>
                <summary>
                    <h4 style="margin-bottom: 0px; display: inline;">Worker: 1</h4>
                </summary>
                <table style="width: 100%; text-align: left;">
                    <tr>
                        <td style="text-align: left;">
                            <strong>Comm: </strong> tcp://127.0.0.1:44307
                        </td>
                        <td style="text-align: left;">
                            <strong>Total threads: </strong> 1
                        </td>
                    </tr>
                    <tr>
                        <td style="text-align: left;">
                            <strong>Dashboard: </strong> <a href="http://127.0.0.1:44101/status" target="_blank">http://127.0.0.1:44101/status</a>
                        </td>
                        <td style="text-align: left;">
                            <strong>Memory: </strong> 6.34 GiB
                        </td>
                    </tr>
                    <tr>
                        <td style="text-align: left;">
                            <strong>Nanny: </strong> tcp://127.0.0.1:45735
                        </td>
                        <td style="text-align: left;"></td>
                    </tr>
                    <tr>
                        <td colspan="2" style="text-align: left;">
                            <strong>Local directory: </strong> /tmp/dask-scratch-space/worker-k30lv_0q
                        </td>
                    </tr>





                </table>
            </details>
            </div>
        </div>


    </details>
</div>

        </details>
    </div>
</div>
            </details>


    </div>
</div>



If you are running this notebook in Colab, you will need to create and use a proxy URL to see the dashboard running on the local server.


```python
if 'google.colab' in str(get_ipython()):
    from google.colab import output
    port_to_expose = 8787  # This is the default port for Dask dashboard
    print(output.eval_js(f'google.colab.kernel.proxyPort({port_to_expose})'))

```

    https://8787-m-s-3l9rk32t0d95d-b.us-central1-0.prod.colab.dev


### Get a Sentinel-2 Scene

We define a location and time of interest to get some satellite imagery.


```python
latitude = 27.163
longitude = 82.608
year = 2023
```


```python
# Define a small bounding box around the chosen point
km2deg = 1.0 / 111
x, y = (longitude, latitude)
r = 1 * km2deg  # radius in degrees
bbox = (x - r, y - r, x + r, y + r)
```

Search the catalog for matching items.


```python
# Query the STAC Catalog
catalog = pystac_client.Client.open(
    'https://earth-search.aws.element84.com/v1')

search = catalog.search(
    collections=['sentinel-2-c1-l2a'],
    bbox=bbox,
    datetime=f'{year}',
    query={'eo:cloud_cover': {'lt': 30}, 's2:nodata_pixel_percentage': {'lt': 10}},
    sortby=[{'field': 'properties.eo:cloud_cover', 'direction': 'asc'}]

)
items = search.item_collection()

# Load to XArray
ds = stac.load(
    items,
    bands=['red', 'green', 'blue', 'nir', 'swir16'],
    resolution=10,
    chunks={},  # <-- use Dask
    groupby='solar_day',
    preserve_original_order=True
)

# Select the first scene
timestamp = pd.to_datetime(items[0].properties['datetime']).tz_convert(None)
scene = ds.sel(time=timestamp)
# Mask nodata values
scene = scene.where(scene != 0)
# Apply scale/offset
scale = 0.0001
offset = -0.1
scene = scene*scale + offset
```

### Visualize the Scene

To visualize our Dataset, we first convert it to a DataArray using the `to_array()` method. All the variables will be converted to a new dimension. Since our variables are image bands, we give the name of the new dimesion as band.



```python
scene_da = scene.to_array('band')
```

Rather than loading the entire scene into memory, we resample it to a lower resolution preview and render it.


```python
preview = scene_da.rio.reproject(
    scene.rio.crs, resolution=300
)

fig, ax = plt.subplots(1, 1)
fig.set_size_inches(5,5)
preview.sel(band=['red', 'green', 'blue']).plot.imshow(
    ax=ax,
    robust=True)
ax.set_title('RGB Visualization')
ax.set_axis_off()
ax.set_aspect('equal')
plt.show()
```


    
![](python-remote-sensing-output/solutions/03_calculating_indices_files/03_calculating_indices_17_0.png)
    


We can also view a False Color Composite (FCC) with a different combination of spectral bands.


```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(5,5)
preview.sel(band=['nir', 'red', 'green']).plot.imshow(
    ax=ax,
    robust=True)
ax.set_title('NRG Visualization')
ax.set_axis_off()
plt.show()
```


    
![](python-remote-sensing-output/solutions/03_calculating_indices_files/03_calculating_indices_19_0.png)
    


### Calculate Spectral Indices

The Normalized Difference Vegetation Index (NDVI) is calculated using the following formula:

`NDVI = (NIR - Red)/(NIR + Red)`

Where:
*   NIR = Near-Infrared band reflectance
*   Red = Red band reflectance


```python
red = scene_da.sel(band='red')
nir = scene_da.sel(band='nir')

ndvi = (nir - red)/(nir + red)
ndvi
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
<style>/* CSS stylesheet for displaying xarray objects in notebooks */

:root {
  --xr-font-color0: var(
    --jp-content-font-color0,
    var(--pst-color-text-base rgba(0, 0, 0, 1))
  );
  --xr-font-color2: var(
    --jp-content-font-color2,
    var(--pst-color-text-base, rgba(0, 0, 0, 0.54))
  );
  --xr-font-color3: var(
    --jp-content-font-color3,
    var(--pst-color-text-base, rgba(0, 0, 0, 0.38))
  );
  --xr-border-color: var(
    --jp-border-color2,
    hsl(from var(--pst-color-on-background, white) h s calc(l - 10))
  );
  --xr-disabled-color: var(
    --jp-layout-color3,
    hsl(from var(--pst-color-on-background, white) h s calc(l - 40))
  );
  --xr-background-color: var(
    --jp-layout-color0,
    var(--pst-color-on-background, white)
  );
  --xr-background-color-row-even: var(
    --jp-layout-color1,
    hsl(from var(--pst-color-on-background, white) h s calc(l - 5))
  );
  --xr-background-color-row-odd: var(
    --jp-layout-color2,
    hsl(from var(--pst-color-on-background, white) h s calc(l - 15))
  );
}

html[theme="dark"],
html[data-theme="dark"],
body[data-theme="dark"],
body.vscode-dark {
  --xr-font-color0: var(
    --jp-content-font-color0,
    var(--pst-color-text-base, rgba(255, 255, 255, 1))
  );
  --xr-font-color2: var(
    --jp-content-font-color2,
    var(--pst-color-text-base, rgba(255, 255, 255, 0.54))
  );
  --xr-font-color3: var(
    --jp-content-font-color3,
    var(--pst-color-text-base, rgba(255, 255, 255, 0.38))
  );
  --xr-border-color: var(
    --jp-border-color2,
    hsl(from var(--pst-color-on-background, #111111) h s calc(l + 10))
  );
  --xr-disabled-color: var(
    --jp-layout-color3,
    hsl(from var(--pst-color-on-background, #111111) h s calc(l + 40))
  );
  --xr-background-color: var(
    --jp-layout-color0,
    var(--pst-color-on-background, #111111)
  );
  --xr-background-color-row-even: var(
    --jp-layout-color1,
    hsl(from var(--pst-color-on-background, #111111) h s calc(l + 5))
  );
  --xr-background-color-row-odd: var(
    --jp-layout-color2,
    hsl(from var(--pst-color-on-background, #111111) h s calc(l + 15))
  );
}

.xr-wrap {
  display: block !important;
  min-width: 300px;
  max-width: 700px;
  line-height: 1.6;
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
.xr-obj-name,
.xr-group-name {
  margin-left: 2px;
  margin-right: 10px;
}

.xr-group-name::before {
  content: "📁";
  padding-right: 0.3em;
}

.xr-group-name,
.xr-obj-type {
  color: var(--xr-font-color2);
}

.xr-sections {
  padding-left: 0 !important;
  display: grid;
  grid-template-columns: 150px auto auto 1fr 0 20px 0 20px;
  margin-block-start: 0;
  margin-block-end: 0;
}

.xr-section-item {
  display: contents;
}

.xr-section-item input {
  display: inline-block;
  opacity: 0;
  height: 0;
  margin: 0;
}

.xr-section-item input + label {
  color: var(--xr-disabled-color);
  border: 2px solid transparent !important;
}

.xr-section-item input:enabled + label {
  cursor: pointer;
  color: var(--xr-font-color2);
}

.xr-section-item input:focus + label {
  border: 2px solid var(--xr-font-color0) !important;
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
  content: "►";
  font-size: 11px;
  width: 15px;
  text-align: center;
}

.xr-section-summary-in:disabled + label:before {
  color: var(--xr-disabled-color);
}

.xr-section-summary-in:checked + label:before {
  content: "▼";
}

.xr-section-summary-in:checked + label > span {
  display: none;
}

.xr-section-summary,
.xr-section-inline-details {
  padding-top: 4px;
}

.xr-section-inline-details {
  grid-column: 2 / -1;
}

.xr-section-details {
  display: none;
  grid-column: 1 / -1;
  margin-top: 4px;
  margin-bottom: 5px;
}

.xr-section-summary-in:checked ~ .xr-section-details {
  display: contents;
}

.xr-group-box {
  display: inline-grid;
  grid-template-columns: 0px 20px auto;
  width: 100%;
}

.xr-group-box-vline {
  grid-column-start: 1;
  border-right: 0.2em solid;
  border-color: var(--xr-border-color);
  width: 0px;
}

.xr-group-box-hline {
  grid-column-start: 2;
  grid-row-start: 1;
  height: 1em;
  width: 20px;
  border-bottom: 0.2em solid;
  border-color: var(--xr-border-color);
}

.xr-group-box-contents {
  grid-column-start: 3;
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
  content: "(";
}

.xr-dim-list:after {
  content: ")";
}

.xr-dim-list li:not(:last-child):after {
  content: ",";
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
  border-color: var(--xr-background-color-row-odd);
  margin-bottom: 0;
  padding-top: 2px;
}

.xr-var-item > .xr-var-name:hover span {
  padding-right: 5px;
}

.xr-var-list > li:nth-child(odd) > div,
.xr-var-list > li:nth-child(odd) > label,
.xr-var-list > li:nth-child(odd) > .xr-var-name span {
  background-color: var(--xr-background-color-row-odd);
  border-color: var(--xr-background-color-row-even);
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

.xr-index-preview {
  grid-column: 2 / 5;
  color: var(--xr-font-color2);
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
.xr-var-data,
.xr-index-data {
  display: none;
  border-top: 2px dotted var(--xr-background-color);
  padding-bottom: 20px !important;
  padding-top: 10px !important;
}

.xr-var-attrs-in + label,
.xr-var-data-in + label,
.xr-index-data-in + label {
  padding: 0 1px;
}

.xr-var-attrs-in:checked ~ .xr-var-attrs,
.xr-var-data-in:checked ~ .xr-var-data,
.xr-index-data-in:checked ~ .xr-index-data {
  display: block;
}

.xr-var-data > table {
  float: right;
}

.xr-var-data > pre,
.xr-index-data > pre,
.xr-var-data > table > tbody > tr {
  background-color: transparent !important;
}

.xr-var-name span,
.xr-var-data,
.xr-index-name div,
.xr-index-data,
.xr-attrs {
  padding-left: 25px !important;
}

.xr-attrs,
.xr-var-attrs,
.xr-var-data,
.xr-index-data {
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
.xr-icon-file-text2,
.xr-no-icon {
  display: inline-block;
  vertical-align: middle;
  width: 1em;
  height: 1.5em !important;
  stroke-width: 0;
  stroke: currentColor;
  fill: currentColor;
}

.xr-var-attrs-in:checked + label > .xr-icon-file-text2,
.xr-var-data-in:checked + label > .xr-icon-database,
.xr-index-data-in:checked + label > .xr-icon-database {
  color: var(--xr-font-color0);
  filter: drop-shadow(1px 1px 5px var(--xr-font-color2));
  stroke-width: 0.8px;
}
</style><pre class='xr-text-repr-fallback'>&lt;xarray.DataArray (y: 10980, x: 10980)&gt; Size: 482MB
dask.array&lt;truediv, shape=(10980, 10980), dtype=float32, chunksize=(10980, 10980), chunktype=numpy.ndarray&gt;
Coordinates:
  * y            (y) float64 88kB 3.1e+06 3.1e+06 3.1e+06 ... 2.99e+06 2.99e+06
  * x            (x) float64 88kB 6e+05 6e+05 6e+05 ... 7.098e+05 7.098e+05
    spatial_ref  int32 4B 32644
    time         datetime64[ns] 8B 2023-12-24T05:21:10.640000</pre><div class='xr-wrap' style='display:none'><div class='xr-header'><div class='xr-obj-type'>xarray.DataArray</div><div class='xr-obj-name'></div><ul class='xr-dim-list'><li><span class='xr-has-index'>y</span>: 10980</li><li><span class='xr-has-index'>x</span>: 10980</li></ul></div><ul class='xr-sections'><li class='xr-section-item'><div class='xr-array-wrap'><input id='section-3221ec8d-eaa0-4eb9-b4af-c6e801459d45' class='xr-array-in' type='checkbox' checked><label for='section-3221ec8d-eaa0-4eb9-b4af-c6e801459d45' title='Show/hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-array-preview xr-preview'><span>dask.array&lt;chunksize=(10980, 10980), meta=np.ndarray&gt;</span></div><div class='xr-array-data'><table>
    <tr>
        <td>
            <table style="border-collapse: collapse;">
                <thead>
                    <tr>
                        <td> </td>
                        <th> Array </th>
                        <th> Chunk </th>
                    </tr>
                </thead>
                <tbody>

                    <tr>
                        <th> Bytes </th>
                        <td> 459.90 MiB </td>
                        <td> 459.90 MiB </td>
                    </tr>

                    <tr>
                        <th> Shape </th>
                        <td> (10980, 10980) </td>
                        <td> (10980, 10980) </td>
                    </tr>
                    <tr>
                        <th> Dask graph </th>
                        <td colspan="2"> 1 chunks in 51 graph layers </td>
                    </tr>
                    <tr>
                        <th> Data type </th>
                        <td colspan="2"> float32 numpy.ndarray </td>
                    </tr>
                </tbody>
            </table>
        </td>
        <td>
        <svg width="170" height="170" style="stroke:rgb(0,0,0);stroke-width:1" >

  <!-- Horizontal lines -->
  <line x1="0" y1="0" x2="120" y2="0" style="stroke-width:2" />
  <line x1="0" y1="120" x2="120" y2="120" style="stroke-width:2" />

  <!-- Vertical lines -->
  <line x1="0" y1="0" x2="0" y2="120" style="stroke-width:2" />
  <line x1="120" y1="0" x2="120" y2="120" style="stroke-width:2" />

  <!-- Colored Rectangle -->
  <polygon points="0.0,0.0 120.0,0.0 120.0,120.0 0.0,120.0" style="fill:#ECB172A0;stroke-width:0"/>

  <!-- Text -->
  <text x="60.000000" y="140.000000" font-size="1.0rem" font-weight="100" text-anchor="middle" >10980</text>
  <text x="140.000000" y="60.000000" font-size="1.0rem" font-weight="100" text-anchor="middle" transform="rotate(-90,140.000000,60.000000)">10980</text>
</svg>
        </td>
    </tr>
</table></div></div></li><li class='xr-section-item'><input id='section-258be0ef-66c6-4c33-a91e-e3dd02d9bbc3' class='xr-section-summary-in' type='checkbox'  checked><label for='section-258be0ef-66c6-4c33-a91e-e3dd02d9bbc3' class='xr-section-summary' >Coordinates: <span>(4)</span></label><div class='xr-section-inline-details'></div><div class='xr-section-details'><ul class='xr-var-list'><li class='xr-var-item'><div class='xr-var-name'><span class='xr-has-index'>y</span></div><div class='xr-var-dims'>(y)</div><div class='xr-var-dtype'>float64</div><div class='xr-var-preview xr-preview'>3.1e+06 3.1e+06 ... 2.99e+06</div><input id='attrs-affb1aa7-d7c1-43e6-bf61-c114de327da4' class='xr-var-attrs-in' type='checkbox' ><label for='attrs-affb1aa7-d7c1-43e6-bf61-c114de327da4' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-40a37e0d-6c67-4c6e-a88a-3ad22bf3a8aa' class='xr-var-data-in' type='checkbox'><label for='data-40a37e0d-6c67-4c6e-a88a-3ad22bf3a8aa' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'><dt><span>units :</span></dt><dd>metre</dd><dt><span>resolution :</span></dt><dd>-10.0</dd><dt><span>crs :</span></dt><dd>EPSG:32644</dd></dl></div><div class='xr-var-data'><pre>array([3100015., 3100005., 3099995., ..., 2990245., 2990235., 2990225.])</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span class='xr-has-index'>x</span></div><div class='xr-var-dims'>(x)</div><div class='xr-var-dtype'>float64</div><div class='xr-var-preview xr-preview'>6e+05 6e+05 ... 7.098e+05 7.098e+05</div><input id='attrs-c3317121-c818-4029-806e-28567ca56e1b' class='xr-var-attrs-in' type='checkbox' ><label for='attrs-c3317121-c818-4029-806e-28567ca56e1b' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-e6fcb03b-834f-4506-addc-72a942b0c16d' class='xr-var-data-in' type='checkbox'><label for='data-e6fcb03b-834f-4506-addc-72a942b0c16d' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'><dt><span>units :</span></dt><dd>metre</dd><dt><span>resolution :</span></dt><dd>10.0</dd><dt><span>crs :</span></dt><dd>EPSG:32644</dd></dl></div><div class='xr-var-data'><pre>array([600005., 600015., 600025., ..., 709775., 709785., 709795.])</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span>spatial_ref</span></div><div class='xr-var-dims'>()</div><div class='xr-var-dtype'>int32</div><div class='xr-var-preview xr-preview'>32644</div><input id='attrs-1e306efe-5e06-41aa-a9b1-33c0ba172dfe' class='xr-var-attrs-in' type='checkbox' ><label for='attrs-1e306efe-5e06-41aa-a9b1-33c0ba172dfe' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-8bebadcd-9945-40b8-9f62-f28423d25b81' class='xr-var-data-in' type='checkbox'><label for='data-8bebadcd-9945-40b8-9f62-f28423d25b81' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'><dt><span>spatial_ref :</span></dt><dd>PROJCRS[&quot;WGS 84 / UTM zone 44N&quot;,BASEGEOGCRS[&quot;WGS 84&quot;,ENSEMBLE[&quot;World Geodetic System 1984 ensemble&quot;,MEMBER[&quot;World Geodetic System 1984 (Transit)&quot;],MEMBER[&quot;World Geodetic System 1984 (G730)&quot;],MEMBER[&quot;World Geodetic System 1984 (G873)&quot;],MEMBER[&quot;World Geodetic System 1984 (G1150)&quot;],MEMBER[&quot;World Geodetic System 1984 (G1674)&quot;],MEMBER[&quot;World Geodetic System 1984 (G1762)&quot;],MEMBER[&quot;World Geodetic System 1984 (G2139)&quot;],MEMBER[&quot;World Geodetic System 1984 (G2296)&quot;],ELLIPSOID[&quot;WGS 84&quot;,6378137,298.257223563,LENGTHUNIT[&quot;metre&quot;,1]],ENSEMBLEACCURACY[2.0]],PRIMEM[&quot;Greenwich&quot;,0,ANGLEUNIT[&quot;degree&quot;,0.0174532925199433]],ID[&quot;EPSG&quot;,4326]],CONVERSION[&quot;UTM zone 44N&quot;,METHOD[&quot;Transverse Mercator&quot;,ID[&quot;EPSG&quot;,9807]],PARAMETER[&quot;Latitude of natural origin&quot;,0,ANGLEUNIT[&quot;degree&quot;,0.0174532925199433],ID[&quot;EPSG&quot;,8801]],PARAMETER[&quot;Longitude of natural origin&quot;,81,ANGLEUNIT[&quot;degree&quot;,0.0174532925199433],ID[&quot;EPSG&quot;,8802]],PARAMETER[&quot;Scale factor at natural origin&quot;,0.9996,SCALEUNIT[&quot;unity&quot;,1],ID[&quot;EPSG&quot;,8805]],PARAMETER[&quot;False easting&quot;,500000,LENGTHUNIT[&quot;metre&quot;,1],ID[&quot;EPSG&quot;,8806]],PARAMETER[&quot;False northing&quot;,0,LENGTHUNIT[&quot;metre&quot;,1],ID[&quot;EPSG&quot;,8807]]],CS[Cartesian,2],AXIS[&quot;(E)&quot;,east,ORDER[1],LENGTHUNIT[&quot;metre&quot;,1]],AXIS[&quot;(N)&quot;,north,ORDER[2],LENGTHUNIT[&quot;metre&quot;,1]],USAGE[SCOPE[&quot;Navigation and medium accuracy spatial referencing.&quot;],AREA[&quot;Between 78°E and 84°E, northern hemisphere between equator and 84°N, onshore and offshore. China. India. Kazakhstan. Kyrgyzstan. Nepal. Russian Federation. Sri Lanka.&quot;],BBOX[0,78,84,84]],ID[&quot;EPSG&quot;,32644]]</dd><dt><span>crs_wkt :</span></dt><dd>PROJCRS[&quot;WGS 84 / UTM zone 44N&quot;,BASEGEOGCRS[&quot;WGS 84&quot;,ENSEMBLE[&quot;World Geodetic System 1984 ensemble&quot;,MEMBER[&quot;World Geodetic System 1984 (Transit)&quot;],MEMBER[&quot;World Geodetic System 1984 (G730)&quot;],MEMBER[&quot;World Geodetic System 1984 (G873)&quot;],MEMBER[&quot;World Geodetic System 1984 (G1150)&quot;],MEMBER[&quot;World Geodetic System 1984 (G1674)&quot;],MEMBER[&quot;World Geodetic System 1984 (G1762)&quot;],MEMBER[&quot;World Geodetic System 1984 (G2139)&quot;],MEMBER[&quot;World Geodetic System 1984 (G2296)&quot;],ELLIPSOID[&quot;WGS 84&quot;,6378137,298.257223563,LENGTHUNIT[&quot;metre&quot;,1]],ENSEMBLEACCURACY[2.0]],PRIMEM[&quot;Greenwich&quot;,0,ANGLEUNIT[&quot;degree&quot;,0.0174532925199433]],ID[&quot;EPSG&quot;,4326]],CONVERSION[&quot;UTM zone 44N&quot;,METHOD[&quot;Transverse Mercator&quot;,ID[&quot;EPSG&quot;,9807]],PARAMETER[&quot;Latitude of natural origin&quot;,0,ANGLEUNIT[&quot;degree&quot;,0.0174532925199433],ID[&quot;EPSG&quot;,8801]],PARAMETER[&quot;Longitude of natural origin&quot;,81,ANGLEUNIT[&quot;degree&quot;,0.0174532925199433],ID[&quot;EPSG&quot;,8802]],PARAMETER[&quot;Scale factor at natural origin&quot;,0.9996,SCALEUNIT[&quot;unity&quot;,1],ID[&quot;EPSG&quot;,8805]],PARAMETER[&quot;False easting&quot;,500000,LENGTHUNIT[&quot;metre&quot;,1],ID[&quot;EPSG&quot;,8806]],PARAMETER[&quot;False northing&quot;,0,LENGTHUNIT[&quot;metre&quot;,1],ID[&quot;EPSG&quot;,8807]]],CS[Cartesian,2],AXIS[&quot;(E)&quot;,east,ORDER[1],LENGTHUNIT[&quot;metre&quot;,1]],AXIS[&quot;(N)&quot;,north,ORDER[2],LENGTHUNIT[&quot;metre&quot;,1]],USAGE[SCOPE[&quot;Navigation and medium accuracy spatial referencing.&quot;],AREA[&quot;Between 78°E and 84°E, northern hemisphere between equator and 84°N, onshore and offshore. China. India. Kazakhstan. Kyrgyzstan. Nepal. Russian Federation. Sri Lanka.&quot;],BBOX[0,78,84,84]],ID[&quot;EPSG&quot;,32644]]</dd><dt><span>semi_major_axis :</span></dt><dd>6378137.0</dd><dt><span>semi_minor_axis :</span></dt><dd>6356752.314245179</dd><dt><span>inverse_flattening :</span></dt><dd>298.257223563</dd><dt><span>reference_ellipsoid_name :</span></dt><dd>WGS 84</dd><dt><span>longitude_of_prime_meridian :</span></dt><dd>0.0</dd><dt><span>prime_meridian_name :</span></dt><dd>Greenwich</dd><dt><span>geographic_crs_name :</span></dt><dd>WGS 84</dd><dt><span>horizontal_datum_name :</span></dt><dd>World Geodetic System 1984 ensemble</dd><dt><span>projected_crs_name :</span></dt><dd>WGS 84 / UTM zone 44N</dd><dt><span>grid_mapping_name :</span></dt><dd>transverse_mercator</dd><dt><span>latitude_of_projection_origin :</span></dt><dd>0.0</dd><dt><span>longitude_of_central_meridian :</span></dt><dd>81.0</dd><dt><span>false_easting :</span></dt><dd>500000.0</dd><dt><span>false_northing :</span></dt><dd>0.0</dd><dt><span>scale_factor_at_central_meridian :</span></dt><dd>0.9996</dd><dt><span>GeoTransform :</span></dt><dd>600000 10 0 3100020 0 -10</dd></dl></div><div class='xr-var-data'><pre>array(32644, dtype=int32)</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span>time</span></div><div class='xr-var-dims'>()</div><div class='xr-var-dtype'>datetime64[ns]</div><div class='xr-var-preview xr-preview'>2023-12-24T05:21:10.640000</div><input id='attrs-743516e9-6043-48aa-a153-1c5b32e3563a' class='xr-var-attrs-in' type='checkbox' disabled><label for='attrs-743516e9-6043-48aa-a153-1c5b32e3563a' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-73b7da22-cacf-43a8-afc6-f7eebae1beed' class='xr-var-data-in' type='checkbox'><label for='data-73b7da22-cacf-43a8-afc6-f7eebae1beed' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'></dl></div><div class='xr-var-data'><pre>array(&#x27;2023-12-24T05:21:10.640000000&#x27;, dtype=&#x27;datetime64[ns]&#x27;)</pre></div></li></ul></div></li></ul></div></div>



Let’s visualize the results.


```python
ndvi_preview = ndvi.rio.reproject(
    ndvi.rio.crs, resolution=300
)
cbar_kwargs = {
    'orientation':'horizontal',
    'fraction': 0.025,
    'pad': 0.05,
    'extend':'neither'
}
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(5,5)
ndvi_preview.plot.imshow(
    ax=ax,
    cmap='Greens',
    robust=True,
    cbar_kwargs=cbar_kwargs)
ax.set_title('NDVI')
ax.set_axis_off()
plt.show()
```


    
![](python-remote-sensing-output/solutions/03_calculating_indices_files/03_calculating_indices_24_0.png)
    


The Modified Normalized Difference Water Index (MNDWI) is calculated using the following formula:

`MNDWI = (Green - SWIR1)/(Green + SWIR1)`

Where:
*   Green = Green band reflectance
*   SWIR1 = Short-wave infrared band 1 reflectance


```python
green = scene_da.sel(band='green')
swir16 = scene_da.sel(band='swir16')
mndwi = (green - swir16)/(green + swir16)
```

The Soil Adjusted Vegetation Index (SAVI) is calculated using the following formula:


`SAVI = (1 + L) * ((NIR - Red)/(NIR + Red + L))`

Where:
*   NIR = Near-Infrared band reflectance
*   Red = Red band reflectance
*   L = Soil brightness correction factor (typically 0.5 for moderate vegetation)


```python
savi = 1.5 * ((nir - red) / (nir + red + 0.5))
```

### Save the Computed Indices

Rather than saving it to the temporary machine where Colab is running, we can save it to our own Google Drive. This will ensure the image will be available to us even after existing Google Colab.

Run the following cell to authenticate and mount the Google Drive.


```python
from google.colab import drive
drive.mount('/content/drive')
```


```python
drive_folder_root = 'MyDrive'
output_folder = 'data'
output_folder_path = os.path.join(
    '/content/drive', drive_folder_root, output_folder)

# Check if Google Drive is mounted
if not os.path.exists('/content/drive'):
    print("Google Drive is not mounted. Please run the cell above to mount your drive.")
else:
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)
```


```python
files = {
    'ndvi.tif': ndvi,
    'mndwi.tif': mndwi,
    'savi.tif': savi
}

for file in files:
  output_path = os.path.join(output_folder_path, file)
  files[file].rio.to_raster(output_path, driver='COG')
  print(f'Saved {file} to {output_path}')
```

### Exercise
Apply a threshold to the NDVI values to create a binary raster.

Hint:

Xarray offers two different `where()` functions.

* [`xarray.DataArray.where`](https://docs.xarray.dev/en/stable/generated/xarray.DataArray.where.html): Applies a condition and sets the non-matching values to NaN
* [`xarray.where`](https://docs.xarray.dev/en/stable/generated/xarray.where.html): Applies a condition and allows you to set both matching and non-matching values.

Use the `xr.where()` function to set matching values to 1 and non-matching values to 0.


```python
threshold = 0.5
# Create a new array 'vegeration' where all NDVI values
#  greater than the threshold is 1 and others are 0
```


```python
vegetation = xr.where(ndvi > threshold, 1, 0).astype('byte')
```


```python
vegetation.values
```




    array([[1, 1, 1, ..., 1, 1, 1],
           [1, 1, 1, ..., 1, 1, 0],
           [1, 1, 1, ..., 1, 1, 1],
           ...,
           [0, 0, 0, ..., 0, 0, 0],
           [0, 0, 0, ..., 0, 0, 0],
           [0, 0, 0, ..., 0, 0, 0]], dtype=int8)



Let's visualize the `vegetation` data array using a custom colormap where 0 is white and 1 is green.


```python
# Resample for preview
vegetation_preview = vegetation.rio.reproject(
    vegetation.rio.crs, resolution=300
)

# Create a custom colormap: 0=white, 1=green
colors = [(1, 1, 1), (0, 0.5, 0)]  # White to Green
cmap = mcolors.ListedColormap(colors)

fig, ax = plt.subplots(1, 1)
fig.set_size_inches(5,5)
vegetation_preview.plot.imshow(
    ax=ax,
    cmap=cmap,
    add_colorbar=False)
ax.set_title('Vegetation')
ax.set_axis_off()
ax.set_aspect('equal')
plt.show()
```

We can also apply multiple thresholds.

| NDVI Range | Class |
| ---------- | ----- |
| < 0        | 1     |
| >=0 and < 0.5        | 2     |
| >=0.5        | 3     |


```python
vegetation_classes = xr.where(
    ndvi < 0, # Condition 1: ndvi < 0
    1,
    xr.where(
        ndvi > 0.5, # Condition 2: ndvi > 0.5
        3,
        2 # Else (0 <= ndvi <= 0.5)
    )
).astype('byte')
vegetation_classes
```


```python
vegetation_classes.values
```




    array([[3, 3, 3, ..., 3, 3, 3],
           [3, 3, 3, ..., 3, 3, 2],
           [3, 3, 3, ..., 3, 3, 3],
           ...,
           [2, 2, 2, ..., 2, 2, 2],
           [2, 2, 2, ..., 2, 2, 2],
           [2, 2, 2, ..., 2, 2, 2]], dtype=int8)


