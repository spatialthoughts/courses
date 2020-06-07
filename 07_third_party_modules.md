# Third-party Modules

Python has a thriving ecosystem of third-party modules (i.e. libraries or packages) available for you to install. There are hundreds of thousands of such modules available for you to install and use.

## Installing third-party libraries

Python comes with a package manager called `pip`. It can install all the packages listed at [PyPI (Python Package Index)](https://pypi.org/). To install a package using pip, you need to run a command like following in a Terminal or CMD prompt.

`pip install <package name>`

For this course, we are using Anancoda platform - which comes with its own package manager called `conda`. You can use Anaconda Navigator to search and install packages. Or run the command like following in a Terminal or CMD Prompt.

`conda install <package name>`

See this [comparison of pip and conda](https://www.anaconda.com/blog/understanding-conda-and-pip) to understand the differences.

## Calculating Distance

We have already installed the `geopy` package in our environment. `geopy` comes with functions that have already implemented many distance calculation formulae.

- `distance.great_circle()`: Calculates the distance on a great circle using haversine formula
- `distance.geodesic()`: Calculates the distance using a chosen ellipsoid using vincenty's formula


```python
from geopy import distance

san_francisco = (37.7749, -122.4194)
new_york = (40.661, -73.944)

straight_line_distance = distance.great_circle(san_francisco, new_york)
ellipsoid_distance = distance.geodesic(san_francisco, new_york, ellipsoid='WGS-84')

print(round(straight_line_distance.mi))
print(straight_line_distance, ellipsoid_distance)
```

    2570
    4135.3804590061345 km 4145.446977549562 km


## Exercise

Repeat the distance calculation exercise from the previous module but perform the calculation using the geopy library.


```python
# city1 = (lat1, lng1)
# city2 = (lat2, lng2)
# call the geopy distance function and print the great circle and ellipsoid distance
```

----
