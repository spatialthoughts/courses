# Third-party Modules

Python has a thriving ecosystem of third-party modules (i.e. libraries or packages) available for you to install. There are hundreds of thousands of such modules available for you to install and use.

## Installing third-party libraries

Python comes with a package manager called `pip`. It can install all the packages listed at [PyPI (Python Package Index)](https://pypi.org/). To install a package using pip, you need to run a command like following in a Terminal or CMD prompt.

`pip install <package name>`

For this course, we are using Anancoda platform - which comes with its own package manager called `conda`. You can run the command like following in a Terminal or CMD Prompt.

`conda install <package name>`

### Alternative package managers

Python ecosystem has many other package managers that you can use. Once you learn the basics of creating environments and installing packages using conda, you may consider switching to any of the following alternatives.

* [Mamba](https://mamba.readthedocs.io/en/latest/index.html) is an alternate open-source package manager that is fully compatible with conda and does not have the commercial licensing requirements of conda.
* [Pixi](https://pixi.prefix.dev/latest/) is a fast and modern alternative to conda.
* [uv](https://docs.astral.sh/uv/) is a popular and fast alternative to pip.

You can read more about [Python package managers](https://jacobtomlinson.dev/posts/2025/python-package-managers-uv-vs-pixi/) which details all the options and their tradeoffs.


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

print(straight_line_distance, ellipsoid_distance)
```

## Exercise

Repeat the distance calculation exercise from the previous module but perform the calculation using the geopy library.


```python
from geopy import distance

# city1 = (lat1, lng1)
# city2 = (lat2, lng2)
# call the geopy distance function and print the great circle and ellipsoid distance
```

----
