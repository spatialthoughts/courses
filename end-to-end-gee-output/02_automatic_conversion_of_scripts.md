[geemap](https://github.com/giswqs/geemap) is an open-source Python package that comes with many helpful features that help you use Earth Engine effectively in Python.

It comes with a function that can help you translate your javascript earth engine code to Python automatically.

> The reverse is also possible. The [Open Earth Engine Library (OEEL)](https://www.open-geocomputing.org/OpenEarthEngineLibrary/#.Python.run) allows you to run Python code in the Earth Engine Code Editor.

The `geemap` package is pre-installed in Colab.




```python
import geemap
import ee
```

#### Initialization

First of all, you need to run the following cells to initialize the API and authorize your account. You must have a Google Cloud Project associated with your GEE account. Replace the `cloud_project` with your own project from [Google Cloud Console](https://console.cloud.google.com/).


```python
cloud_project = 'spatialthoughts'

try:
    ee.Initialize(project=cloud_project)
except:
    ee.Authenticate()
    ee.Initialize(project=cloud_project)
```

#### Automatic Conversion using GUI

`geemap` comes with a user interface that can be used to interactively do code conversion. Let's try to convert the following Javascript code to Python.

```
var geometry = ee.Geometry.Point([77.60412933051538, 12.952912912328241]);
var s2 = ee.ImageCollection('COPERNICUS/S2_HARMONIZED');

var rgbVis = {min: 0.0, max: 3000, bands: ['B4', 'B3', 'B2']};

var filtered = s2.filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30))
  .filter(ee.Filter.date('2019-01-01', '2020-01-01'))
  .filter(ee.Filter.bounds(geometry));
  
var medianComposite = filtered.median();

Map.centerObject(geometry, 10);
Map.addLayer(medianComposite, rgbVis, 'Median Composite');
```

Run the cell below to load the map widget. Once the map widget loads, click the *Toolbar* icon in the top-right corner and select the *Convert Earth Engine Javascript to Python* tool. Paste your Javascript code and click *Convert*.


```python
Map = geemap.Map(width=800)
Map
```

You will see the auto-converted code displayed. Copy and paste it into a new cell and run it. Your code will be run using the GEE Python API.




```python
geometry = ee.Geometry.Point([77.60412933051538, 12.952912912328241])
s2 = ee.ImageCollection('COPERNICUS/S2_HARMONIZED')

rgbVis = {'min': 0.0, 'max': 3000, 'bands': ['B4', 'B3', 'B2']}

filtered = s2.filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30)) \
  .filter(ee.Filter.date('2019-01-01', '2020-01-01')) \
  .filter(ee.Filter.bounds(geometry))

medianComposite = filtered.median()

Map.centerObject(geometry, 10)
Map.addLayer(medianComposite, rgbVis, 'Median Composite')

```

If your code loads any layers, they will be loaded on the map widget. To display it, open a new code cell and just type `Map` to display the widget.


```python
Map
```

#### Automatic Conversion using Code

`geemap` offers a function `js_snippet_to_py()` that can be used to perform the conversion using code. This is useful for batch conversions. To use this, we first create a string with the javascript code.


```python
javascript_code = """
var geometry = ee.Geometry.Point([107.61303468448624, 12.130969369851766]);
Map.centerObject(geometry, 12)
var s2 = ee.ImageCollection('COPERNICUS/S2_HARMONIZED')
var rgbVis = {
  min: 0.0,
  max: 3000,
  bands: ['B4', 'B3', 'B2'],
};

var filtered = s2
  .filter(ee.Filter.date('2019-01-01', '2020-01-01'))
  .filter(ee.Filter.bounds(geometry))

// Load the Cloud Score+ collection
var csPlus = ee.ImageCollection('GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED');
var csPlusBands = csPlus.first().bandNames();

// We need to add Cloud Score + bands to each Sentinel-2
// image in the collection
// This is done using the linkCollection() function
var filteredS2WithCs = filtered.linkCollection(csPlus, csPlusBands);

// Function to mask pixels with low CS+ QA scores.
function maskLowQA(image) {
  var qaBand = 'cs';
  var clearThreshold = 0.5;
  var mask = image.select(qaBand).gte(clearThreshold);
  return image.updateMask(mask);
}


var filteredMasked = filteredS2WithCs
  .map(maskLowQA);

// Write a function that computes NDVI for an image and adds it as a band
function addNDVI(image) {
  var ndvi = image.normalizedDifference(['B5', 'B4']).rename('ndvi');
  return image.addBands(ndvi);
}

var withNdvi = filteredMasked.map(addNDVI);

var composite = withNdvi.median()
palette = [
  'CE7E45', 'DF923D', 'F1B555', 'FCD163', '99B718',
  '74A901', '66A000', '529400', '3E8601', '207401', '056201',
  '004C00', '023B01', '012E01', '011D01', '011301'];

ndviVis = {min:0, max:0.7, palette: palette }
Map.addLayer(withNdvi.select('ndvi'), ndviVis, 'NDVI Composite')

"""
```


```python
lines = geemap.js_snippet_to_py(
    javascript_code, add_new_cell=False,
    import_ee=True, import_geemap=True, show_map=True)
for line in lines:
    print(line.rstrip())
```

The automatic conversion works great. Review it and paste it to the cell below.

> Note: The automatic conversion uses the variable `m` for the map instead of `Map`.


```python
import ee
import geemap

m = geemap.Map()

geometry = ee.Geometry.Point([107.61303468448624, 12.130969369851766])
m.centerObject(geometry, 12)
s2 = ee.ImageCollection('COPERNICUS/S2_HARMONIZED')
rgbVis = {
  'min': 0.0,
  'max': 3000,
  'bands': ['B4', 'B3', 'B2'],
}

filtered = s2 \
  .filter(ee.Filter.date('2019-01-01', '2020-01-01')) \
  .filter(ee.Filter.bounds(geometry))

# Load the Cloud Score+ collection
csPlus = ee.ImageCollection('GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED')
csPlusBands = csPlus.first().bandNames()

# We need to add Cloud Score + bands to each Sentinel-2
# image in the collection
# This is done using the linkCollection() function
filteredS2WithCs = filtered.linkCollection(csPlus, csPlusBands)

# Function to mask pixels with low CS+ QA scores.
def maskLowQA(image):
  qaBand = 'cs'
  clearThreshold = 0.5
  mask = image.select(qaBand).gte(clearThreshold)
  return image.updateMask(mask)

filteredMasked = filteredS2WithCs \
  .map(maskLowQA)

# Write a function that computes NDVI for an image and adds it as a band
def addNDVI(image):
  ndvi = image.normalizedDifference(['B5', 'B4']).rename('ndvi')
  return image.addBands(ndvi)

withNdvi = filteredMasked.map(addNDVI)

composite = withNdvi.median()
palette = [
  'CE7E45', 'DF923D', 'F1B555', 'FCD163', '99B718',
  '74A901', '66A000', '529400', '3E8601', '207401', '056201',
  '004C00', '023B01', '012E01', '011D01', '011301']

ndviVis = {'min':0, 'max':0.7, 'palette': palette }
m.addLayer(withNdvi.select('ndvi'), ndviVis, 'NDVI Composite')

m
```

### Exercise

Take the Javascript code snippet below and use `geemap` to automatically convert it to Python.

---

```
var admin2 = ee.FeatureCollection("FAO/GAUL_SIMPLIFIED_500m/2015/level2");

var karnataka = admin2.filter(ee.Filter.eq('ADM1_NAME', 'Karnataka'))

var visParams = {color: 'red'}
Map.centerObject(karnataka)
Map.addLayer(karnataka, visParams, 'Karnataka Districts')
```
---
