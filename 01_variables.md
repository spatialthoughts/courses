# Variables

## Strings

A string is a sequence of letters, numbers, and punctuation marks - or commonly known as **text**

In Python you can create a string by typing letters between single or double quotation marks.


```python
city = 'San Fransico'
state = 'California'
print(city, state)
```


```python
print(city + state)
```


```python
print(city + ',' + state)
```

## Numbers

Python can handle several types of numbers, but the two most common are:

- **int**, which represents integer values like 100, and
- **float**, which represents numbers that have a fraction part, like 0.5



```python
population = 881549
latitude = 37.7739
longitude = -121.5687
```


```python
print(type(population))
```


```python
print(type(latitude))
```


```python
elevation_feet = 934
elevation_meters = elevation_feet * 0.3048
print(elevation_meters)
```


```python
area_sqmi = 46.89
density = population / area_sqmi
print(density)
```

## Exercise

We calculated the population density in number of people per square mile. Calculate and print the density in number of people per square kilometers.

- Hint1: 1 mile = 1.60934 kilometers
- Hint2: To calculate exponential of a number in Python, you use the ** notation. x² is written as x**2

Add the code in the cell below and run it. The output should be 7258.8966


```python
population = 881549
area_sqmi = 46.89

# Remove this line and add code here
```

----
