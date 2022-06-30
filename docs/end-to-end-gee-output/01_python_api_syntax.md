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

javascript code:
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

#### Earth Engine Objects

You can create Earth Engine objects using the ``ee`` functions the same way.


```python
s2 = ee.ImageCollection('COPERNICUS/S2')
geometry = ee.Geometry.Polygon([[
  [82.60642647743225, 27.16350437805251],
  [82.60984897613525, 27.1618529901377],
  [82.61088967323303, 27.163695288375266],
  [82.60757446289062, 27.16517483230927]
]])
```

#### Line Continuation

Python doesn't use a semi-colon for line ending. To indicate line-continuation you need to use the \\ character

javascript code:
```
var s2 = ee.ImageCollection('COPERNICUS/S2');
var filtered = s2.filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30))
  .filter(ee.Filter.date('2019-02-01', '2019-03-01'))
  .filter(ee.Filter.bounds(geometry));
```


```python
filtered = s2 \
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30)) \
    .filter(ee.Filter.date('2019-02-01', '2019-03-01')) \
    .filter(ee.Filter.bounds(geometry))
```

#### Functions

Instead of the `function` keyword, Python uses the `def` keyword. Also the in-line functions are defined using `lambda` anonymous functions.

In the example below, also now the `and` operator - which is capitalized as `And` in Python version to avoid conflict with the built-in `and` operator. The same applies to `Or` and `Not` operators. `true`, `false`, `null` in Python are also spelled as `True`, `False` and `None`.

javascript code:
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

function addNDVI(image) {
  var ndvi = image.normalizedDifference(['B8', 'B4']).rename('ndvi');
  return image.addBands(ndvi);
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

def addNDVI(image):
  ndvi = image.normalizedDifference(['B8', 'B4']).rename('ndvi')
  return image.addBands(ndvi)

withNdvi = filtered \
    .map(maskS2clouds) \
    .map(addNDVI)
```

#### Function Arguments

Named arguments to Earth Engine functions need to be in quotes. Also when passing the named arguments as a dictionary, it needs to be passed using the `**` keyword.

javascript code:
```
var composite = withNdvi.median();
var ndvi = composite.select('ndvi');

var stats = ndvi.reduceRegion({
    reducer: ee.Reducer.mean(),
    geometry: geometry,
    scale: 10,
    maxPixels: 1e10
})    
```


```python
composite = withNdvi.median()
ndvi = composite.select('ndvi')

stats = ndvi.reduceRegion(**{
  'reducer': ee.Reducer.mean(),
  'geometry': geometry,
  'scale': 10,
  'maxPixels': 1e10
  })
```

#### Printing Values

The `print()` function syntax is the same. But you must remember that in the Code Editor when you cann `print`, the value of the server object is fetched and then printed. You must do that explicitely by calling `getInfo()` on any server-side object.

javascript code:
```
print(stats.get('ndvi')
```


```python
print(stats.get('ndvi').getInfo())
```

#### In-line functions

The syntax for defining in-line functions is also slightly different. You need to use the `lambda` keyword.

javascript code:
```
var myList = ee.List.sequence(1, 10);
var newList = myList.map(function(number) {
    return ee.Number(number).pow(2);
print(newList);
```


```python
myList = ee.List.sequence(1, 10)
newList = myList.map(lambda number: ee.Number(number).pow(2))
print(newList.getInfo())
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
