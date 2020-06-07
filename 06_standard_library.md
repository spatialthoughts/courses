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


## Discover Python Easter Eggs

Programmers love to hide secret jokes in their programs for gun. These are known as *Easter Eggs*. Python has an easter egg that you can see when you try to import the module named `this`. Try writing the command `import this` below.


```python
import this
```

    The Zen of Python, by Tim Peters
    
    Beautiful is better than ugly.
    Explicit is better than implicit.
    Simple is better than complex.
    Complex is better than complicated.
    Flat is better than nested.
    Sparse is better than dense.
    Readability counts.
    Special cases aren't special enough to break the rules.
    Although practicality beats purity.
    Errors should never pass silently.
    Unless explicitly silenced.
    In the face of ambiguity, refuse the temptation to guess.
    There should be one-- and preferably only one --obvious way to do it.
    Although that way may not be obvious at first unless you're Dutch.
    Now is better than never.
    Although never is often better than *right* now.
    If the implementation is hard to explain, it's a bad idea.
    If the implementation is easy to explain, it may be a good idea.
    Namespaces are one honking great idea -- let's do more of those!


Let's try one more. Try importing the `antigravity` module.


```python
import antigravity
```

Here's a complete list of [easter eggs in Python](https://towardsdatascience.com/7-easter-eggs-in-python-7765dc15a203).

## Exercise

Find the coordinates of 2 cities near you and calculate the distance between them


```python
# city1 = (lat1, lng1)
# city2 = (lat2, lng2)
# call the function and print the result
```

----
