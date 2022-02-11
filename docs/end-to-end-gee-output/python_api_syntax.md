Coming from the programming in Earth Engine through the Code Editor, you will need to slightly adapt your scripts to be able to run in Python. For the bulk of your code, you will be using Earth Engine API's server-side objects and functions - which will be exactly the same in Python. You only need to make a few syntactical changes.

[Here's the full list](https://developers.google.com/earth-engine/python_install#syntax) of differences. Most important ones are elaborated below

#### Initialization

First of all, you need to run the following cells to initialize the API and authorize your account. You will be prompted to sign-in to the account and allow access to *View and Manage your Earth Engine data*. Once you approve, you will get an a verification code that needs to be entered at the prompt. This step needs to be done just once per session.


```python
import ee
```


```python
ee.Authenticate()
```


```python
ee.Initialize()
```

#### Variables

Python code doesn't use the 'var' keyword

```
var city = 'San Fransico'
var state = 'California'
print(city, state)

var population = 881549
print(population)
```


```python
city = 'San Fransico'
state = 'California'
print(city, state)

population = 881549
print(population)
```

#### Line Continuation

Python doesn't use a semi-colon for line ending. To indicate line-continuation you need to use the \\ character

```
var s2 = ee.ImageCollection('COPERNICUS/S2');
var filtered = s2.filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30))
  .filter(ee.Filter.date('2019-01-01', '2019-12-31'));
```


```python
s2 = ee.ImageCollection('COPERNICUS/S2')
filtered = s2 \
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30)) \
    .filter(ee.Filter.date('2019-01-01', '2019-12-31')) 
```

#### Functions

Instead of the `function` keyword, Python uses the `def` keyword. Also the in-line functions are defined using `lambda` anonymous functions.

In the example below, also now the `and` operator - which is capitalized as `And` in Python version to avoid conflict with the built-in `and` operator. The same applies to `Or` and `Not` operators. `true`, `false`, `null` in Python are also spelled as `True`, `False` and `None`.

```
function maskS2clouds(image) {
  var qa = image.select('QA60')
  var cloudBitMask = 1 << 10;
  var cirrusBitMask = 1 << 11;
  var mask = qa.bitwiseAnd(cloudBitMask).eq(0).and(
             qa.bitwiseAnd(cirrusBitMask).eq(0))
  return image.updateMask(mask)//.divide(10000)
      .select("B.*")
      .copyProperties(image, ["system:time_start"])
}
```


```python
def maskS2clouds(image):
  qa = image.select('QA60')
  cloudBitMask = 1 << 10
  cirrusBitMask = 1 << 11
  mask = qa.bitwiseAnd(cloudBitMask).eq(0).And(
             qa.bitwiseAnd(cirrusBitMask).eq(0))
  return image.updateMask(mask) \
      .select("B.*") \
      .copyProperties(image, ["system:time_start"])
```

#### Function Arguments

Named arguments to Earth Engine functions need to be in quotes. Also when passing the named arguments as a dictionary, it needs to be passed using the `**` keyword.

```
var gaul = ee.FeatureCollection("FAO/GAUL/2015/level1");
var gfsad = ee.Image("USGS/GFSAD1000_V0");
var wheatrice = gfsad.select('landcover').eq(1)
var uttarpradesh = gaul.filter(ee.Filter.eq('ADM1_NAME', 'Uttar Pradesh'))
var points = wheatrice.selfMask().stratifiedSample(
    {numPoints:100, region:uttarpradesh, geometries: true})
```



```python
gaul = ee.FeatureCollection("FAO/GAUL/2015/level1")
gfsad = ee.Image("USGS/GFSAD1000_V0")
wheatrice = gfsad.select('landcover').eq(1)
uttarpradesh = gaul.filter(ee.Filter.eq('ADM1_NAME', 'Uttar Pradesh'))
points = wheatrice.selfMask().stratifiedSample(**
    {'numPoints':100, 'region':uttarpradesh, 'geometries': True})
print(points.getInfo())

```

#### In-line functions

The syntax for defining in-line functions is also slightly different. You need to use the `lambda` keyword

```
var points = points.map(function(feature) {
  return ee.Feature(feature.geometry(), {'id': feature.id()})
})
```


```python
points = points.map(lambda feature: ee.Feature(feature.geometry(), {'id': feature.id()} ))
```

#### Printing Values

The `print()` function syntax is the same. But you must remember that in the Code Editor when you cann `print`, the value of the server object is fetched and then printed. You must do that explicitely by calling `getInfo()` on any server-side object.

```
print(points.first()
```


```python
print(points.first().getInfo())
```

#### Automatic Conversion of Scripts

[geemap](https://github.com/giswqs/geemap) is an open-source PYthon package that comes with many helpful features that help you use Earth Engine effectively in Python. 

It comes with a function that can help you translate your javascript earth engine code to Python automatically.

The automatic conversion works great, but it is not perfect. You may have to tweak the output a bit. An important filter that is missing from the Python API is the `ee.Filter.bounds()`. You can use an alternative `ee.Filter.intersects('.geo', geometry)` instead.


```python
import geemap
```


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
geemap.js_snippet_to_py(javascript_code)
```


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
  .filter(ee.Filter.intersects('.geo', geometry)) \
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
