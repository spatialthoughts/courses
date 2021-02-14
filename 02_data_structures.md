# Data Structures

## Tuples

A *tuple* is a sequence of objects. It can have any number of objects inside. In Python tuples are written with round brackets **()**. 


```python
latitude = 37.7739
longitude = -121.5687
coordinates = (latitude, longitude)
print(coordinates)
```

You can access each item by its position, i.e. *index*. In programming, the counting starts from 0. So the first item has an index of 0, the second item an index of 1 and so now. The index has to be put inside square brackets **[]**.


```python
y = coordinates[0]
x = coordinates[1]
print(x, y)
```

## Lists

A **list** is similar to a tuple - but with a key difference. With tuples, once created, they cannot be changed, i.e. they are immutable. But lists are mutable. You can add, delete or change elements within a list.  In Python, lists are written with square brackets **[]**


```python
cities = ['San Francisco', 'Los Angeles', 'New York', 'Atlanta']
print(cities)
```

You can access the elements from a list using index the same way as tuples.


```python
print(cities[0])
```

You can call `len()` function with any Python object and it will calculates the size of the object.


```python
print(len(cities))
```

We can add items to the list using the `append()` method


```python
cities.append('Boston')
print(cities)
```

As lists are *mutable*, you will see that the size of the list has now changed


```python
print(len(cities))
```

Another useful method for lists is `sort()` - which can sort the elements in a list.


```python
cities.sort()
print(cities)
```

The default sorting is in *ascending* order. If we wanted to sort the list in a *decending* order, we can call the function with `reverse=True`


```python
cities.sort(reverse=True)
print(cities)
```

## Sets

Sets are like lists, but with some interesting properties. Mainly that they contain only unique values. It also allows for *set operations* - such as *intersection*, *union* and *difference*. In practice, the sets are typically created from lists.


```python
capitals = ['Sacramento', 'Boston', 'Austin', 'Atlanta']
capitals_set = set(capitals)
cities_set = set(cities)

capital_cities = capitals_set.intersection(cities_set)
print(capital_cities)
```

Sets are also useful in finding unique elements in a list. Let's merge the two lists using the `extend()` method. The resulting list will have duplicate elements. Creating a set from the list removes the duplicate elements.


```python
cities.extend(capitals)
print(cities)
print(set(cities))
```

## Dictionaries

In Python dictionaries are written with curly brackets **{}**. Dictionaries have *keys* and *values*. With lists, we can access each element by its index. But a dictionary makes it easy to access the element by name. Keys and values are separated by a colon **:**. 


```python
data = {'city': 'San Francisco', 'population': 881549, 'coordinates': (-122.4194, 37.7749) }
print(data)
```

You can access an item of a dictionary by referring to its key name, inside square brackets.


```python
print(data['city'])
```

## Exercise

From the dictionary below, how do you access the latitude and longitude values? print the latitude and longitude of new york city by extracting it from the dictionary below.


```python
nyc_data = {'city': 'New York', 'population': 8175133, 'coordinates': (40.661, -73.944) }
```

----
