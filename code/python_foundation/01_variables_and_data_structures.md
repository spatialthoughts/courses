## Hello World

When learning a new programming language, it is customary to first learn how to print 'Hello World!'. While a bit quirky, it is a useful first step to know how to send input to the program and where to see the output. In Python, you can use the built-in ``print()`` function to print the greeting ``"Hello World!"``


```python
print('Hello World!')
```

    Hello World!


## Variables

### Strings

A **string** is a sequence of letters, numbers, and punctuation marks - or commonly known as **text**

In Python you can create a string by typing letters between single or double quotation marks.


```python
city = 'San Fransico'
state = 'California'
print(city, state)
```

    San Fransico California



```python
print(city + state)
```

    San FransicoCalifornia



```python
print(city + ',', state)
```

    San Fransico, California


### Numbers

Python can handle several types of numbers, but the two most common are:

 - **int**, which represents integer values like 100, and
- **float**, which represents numbers that have a fraction part, like 0.5



```python
population = 881549
latitude = 37.7749
longitude = -122.4194
```


```python
print(type(population))
```

    <class 'int'>



```python
print(type(latitude))
```

    <class 'float'>



```python
elevation_feet = 934
elevation_meters = elevation_feet * 0.3048
print(elevation_meters)
```

    284.6832



```python
area_sqmi = 46.89
density = population / area_sqmi
print(density)
```

    18800.362550650458


### Exercise

We calculated the population density in number of people per square mile. Calculate and print the density in number of people per square kilometers.

Hint1: 1 mile = 1.60934 kilometers
Hint2: To square a number in Python, you use the ** notation

Create a code cell below this one, type in the code and run the cell. The output should be 7258.8966

## Data Structures


```python
coordinates = (latitude, longitude)
print(coordinates)
```

    (37.7749, -122.4194)



```python
y = coordinates[0]
x = coordinates[1]
print(x, y)
```

    -122.4194 37.7749



```python
data = {'city': 'San Francisco', 'population': 122.4194, 'coordinates': (-122.4194, 37.7749) }
print(data)
```

    {'city': 'San Francisco', 'population': 122.4194, 'coordinates': (-122.4194, 37.7749)}



```python
print(data['city'])
```

    San Francisco



```python
cities = ['San Francisco', 'Los Angeles', 'New York']
print(cities)
```

    ['San Francisco', 'Los Angeles', 'New York']



```python

```
