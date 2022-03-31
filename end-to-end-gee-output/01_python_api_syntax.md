Coming from the programming in Earth Engine through the Code Editor, you will need to slightly adapt your scripts to be able to run in Python. For the bulk of your code, you will be using Earth Engine API's server-side objects and functions - which will be exactly the same in Python. You only need to make a few syntactical changes.

[Here's the full list](https://developers.google.com/earth-engine/python_install#syntax) of differences.

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

### Exercise

Take the Javascript code snippet below and write the equiavalent Python code in the cell below.

- **Hint1**: Chaining of filters require the use of line continuation character `\`
- **Hint2**: Printing of server-side objects requires calling `.getInfo()` on the object

The correct code should print the value **30**.

---

```
var geometry = ee.Geometry.Point([77.60412933051538, 12.952912912328241]);

var s2 = ee.ImageCollection('COPERNICUS/S2');

var filtered = s2.filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30))
  .filter(ee.Filter.date('2019-01-01', '2020-01-01'))
  .filter(ee.Filter.bounds(geometry));
  
print(filtered.size());
```
---


```python
import ee
ee.Authenticate()
ee.Initialize()
```
