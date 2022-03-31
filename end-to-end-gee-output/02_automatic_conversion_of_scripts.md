[geemap](https://github.com/giswqs/geemap) is an open-source Python package that comes with many helpful features that help you use Earth Engine effectively in Python. 

It comes with a function that can help you translate your javascript earth engine code to Python automatically.

Google Colab doesn't come pre-installed with the package, so we install it via pip.


```python
try:
    import geemap
except ModuleNotFoundError:
    if 'google.colab' in str(get_ipython()):
        print('geemap not found, installing via pip in Google Colab...')
        !pip install geemap --quiet
        import geemap
    else:
        print('geemap not found, please install via conda in your environment')
```

The automatic conversion of code is done by calling the `geemap.js_snippet_to_py()` function. We first create a string with the javascript code.


```python
javascript_code = """
var geometry = ee.Geometry.Point([107.61303468448624, 12.130969369851766]);
Map.centerObject(geometry, 12)
var s2 = ee.ImageCollection("COPERNICUS/S2")
var rgbVis = {
  min: 0.0,
  max: 3000,
  bands: ['B4', 'B3', 'B2'],
};

// Write a function for Cloud masking
function maskS2clouds(image) {
  var qa = image.select('QA60')
  var cloudBitMask = 1 << 10;
  var cirrusBitMask = 1 << 11;
  var mask = qa.bitwiseAnd(cloudBitMask).eq(0).and(
             qa.bitwiseAnd(cirrusBitMask).eq(0))
  return image.updateMask(mask)
      .select("B.*")
      .copyProperties(image, ["system:time_start"])
}
 
var filtered = s2
  .filter(ee.Filter.date('2019-01-01', '2019-12-31'))
  .filter(ee.Filter.bounds(geometry))
  .map(maskS2clouds)
  

// Write a function that computes NDVI for an image and adds it as a band
function addNDVI(image) {
  var ndvi = image.normalizedDifference(['B5', 'B4']).rename('ndvi');
  return image.addBands(ndvi);
}

var withNdvi = filtered.map(addNDVI);

var composite = withNdvi.median()
palette = [
  'FFFFFF', 'CE7E45', 'DF923D', 'F1B555', 'FCD163', '99B718',
  '74A901', '66A000', '529400', '3E8601', '207401', '056201',
  '004C00', '023B01', '012E01', '011D01', '011301'];

ndviVis = {min:0, max:0.5, palette: palette }
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


```python
import ee
import geemap
Map = geemap.Map()

geometry = ee.Geometry.Point([107.61303468448624, 12.130969369851766])
Map.centerObject(geometry, 12)
s2 = ee.ImageCollection("COPERNICUS/S2")
rgbVis = {
  'min': 0.0,
  'max': 3000,
  'bands': ['B4', 'B3', 'B2'],
}

# Write a function for Cloud masking
def maskS2clouds(image):
  qa = image.select('QA60')
  cloudBitMask = 1 << 10
  cirrusBitMask = 1 << 11
  mask = qa.bitwiseAnd(cloudBitMask).eq(0).And(
             qa.bitwiseAnd(cirrusBitMask).eq(0))
  return image.updateMask(mask) \
      .select("B.*") \
      .copyProperties(image, ["system:time_start"])

filtered = s2 \
  .filter(ee.Filter.date('2019-01-01', '2019-12-31')) \
  .filter(ee.Filter.bounds(geometry)) \
  .map(maskS2clouds)

# Write a function that computes NDVI for an image and adds it as a band
def addNDVI(image):
  ndvi = image.normalizedDifference(['B5', 'B4']).rename('ndvi')
  return image.addBands(ndvi)

withNdvi = filtered.map(addNDVI)

composite = withNdvi.median()
palette = [
  'FFFFFF', 'CE7E45', 'DF923D', 'F1B555', 'FCD163', '99B718',
  '74A901', '66A000', '529400', '3E8601', '207401', '056201',
  '004C00', '023B01', '012E01', '011D01', '011301']

ndviVis = {'min':0, 'max':0.5, 'palette': palette }
Map.addLayer(withNdvi.select('ndvi'), ndviVis, 'NDVI Composite')
Map
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


```python

```
