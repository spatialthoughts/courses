# The Python Standard Library

Python comes with many built-in modules that offer ready-to-use solutions to common programming problems. To use these modules, you must use the `import` keyword. Once imported in your Python script, you can use the functions provided by the module in your script.

We will use the built-in `math` module that allows us to use advanced mathematical functions.


```python
import math
```

You can also import specific functions or constants from the module like below


```python
from math import pi
print(pi)
```

    3.141592653589793


## Calculating Distance

Given 2 points with their Latitude and Longitude coordinates, the Haversine Formula calculates the straight-line distance in meters, assuming that Earth is a sphere.

The formula is simple enough to be implemented in a spreadsheet too. If you are curious, see [my post](https://spatialthoughts.com/2013/07/06/calculate-distance-spreadsheet/) about using this formula for calculating distances in a spreadsheet.

We can write a function that accepts a pair of origin and destination coordinates and computes the distance.


```python
san_francisco = (37.7749, -122.4194)
new_york = (40.661, -73.944)
```


```python
def haversine_distance(origin, destination):
  lat1, lon1 = origin
  lat2, lon2 = destination
  radius = 6371000
  dlat = math.radians(lat2-lat1)
  dlon = math.radians(lon2-lon1)
  a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
    * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
  c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
  distance = radius * c
  return distance
```


```python
distance = haversine_distance(san_francisco, new_york)
print(distance/1000, 'km')
```

    4135.374617164737 km


## Exercise

Find the coordinates of 2 cities near you and calculate the distance between them


```python
# city1 = (lat1, lng1)
# city2 = (lat2, lng2)
# call the function and print the result
```
