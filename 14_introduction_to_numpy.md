# Introduction to NumPy

![](images/python_foundation/numpy.png)

NumPy (Numerical Python) is an important Python library for scientific computation. Libraries such as Pandas and GeoPandas are built on top of NumPy. 

It provides a fast and efficient ways to work with *Arrays*. In the domain of spatial data analysis, it plays a critical role in working with Raster data - such as satellite imagery, aerial photos, elevation data etc. Since the underlying structure of raster data is a 2D array for each band - learning NumPy is critical in processing raster data using Python.

By convention, `numpy` is commonly imported as `np`


```python
import numpy as np
```

## Arrays

The array object in NumPy is called `ndarray`. It provides a lot of supporting functions that make working with arrays fast and easy. Arrays may seem like Python Lists, but `ndarray` is upto 50x faster in mathematical operations. You can create an array using the `array()` method. As you can see, the rsulting object is of type `numpy.ndarray`


```python
a = np.array([1, 2, 3, 4])
print(type(a))
```

Arrays can have any *dimensions*. We can create a 2D array like below. `ndarray` objects have the property `ndim` that stores the number of array dimensions. You can also check the array size using the `shape` property.


```python
b = np.array([[1, 2, 4], [3, 4, 5]])
print(b)
print(b.ndim)
print(b.shape)
```

You can access elements of arrays like Python lists using `[]` notation.


```python
print(b[0])
```


```python
print(b[0][2])
```

## Array Operations

Mathematical operations on numpy arrays are easy and fast. NumPy as many built-in functions for common operations.


```python
print(np.sum(b))
```

You can also use the functions operations on arrays. 


```python
c = np.array([[2, 2, 2], [2, 2, 2]])
print(np.divide(b, c))
```

If the objects are numpy objects, you can use the Python operators as well


```python
print(b/c)
```

You can also combine array and scalar objects. The scalar operation is applied to each item in the array.


```python
print(b)
print(b*2)
print(b/2)
```

An important concept in NumPy is the *Array Axes*. In a 2D array, Axis 0 is the direction of rows and Axis 1 is the direction of columns. [This article](https://www.sharpsightlabs.com/blog/numpy-axes-explained/) provides a very good explanation of the concept.

Let's see how we can apply a function on a specific axis. Here when we apply `sum` function on axis-0 of a 2D array, it gives us a 1D-array with values summed across rows.


```python
print(b)
row_sum = b.sum(axis=0)
print(row_sum)
```

## Exercise

Sum the array `b` along Axis-1. What do you think will be the result?


```python
import numpy as np

b = np.array([[1, 2, 4], [3, 4, 5]])
print(b)
```

----
