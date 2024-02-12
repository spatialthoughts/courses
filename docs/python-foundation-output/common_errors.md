# Review of Common Python Errors


```python
print(Hello World)
```

<details>
Here, we are getting syntax error because we have missed quotes ('') - which is required to define any string(text).
 </details>


```python
city = 'San Francisco'
print('city')
```

<details>
The code above will not give any error but see what is it printing!
So, quotes should't be there in case of printing a variable.
</details>


```python
elevation_feet = '934'
elevation_meters = elevation_feet * 0.3048
print(elevation_meters)
```

<details>
    If we want to do mathematical operations, it is important to have appropreate data type. In the above code we have stired 'elevation_feet' as a string(having quotes) and we want to multiply it with float(a number with decimal) which is not possible.
</details>


```python
latitude = 37.7739
longitude = -121.5687
coordinates = (latitude, longitude)
long = (coordinates['1'])
```

<details>
    Index of the element in a list or a tupal should be of the type 'integer'. Putting quotes or any floating number will give TypeError.
</details>


```python
data = {place : 'San Francisco', 'population': 881549, 'coordinates': (-122.4194, 37.7749) }
print(data)
```

<details>
    We have not put the quotes around a key(place) in the dictionary. So it is searching for a variable named 'place' which is not defined hence the nameError.
</details>


```python
data = {'place' : 'San Francisco', 'population': 881549, 'coordinates': (-122.4194, 37.7749) }
print(data['Place'])
```

<details>
    In the print statement written above, We have wrongly written the key(place).
We are getting KeyError which means that there is no such key.
</details>


```python
cities = ['San Francisco', 'Los Angeles', 'New York', 'Atlanta']
print(cities[4])
```

<details>
    Here, we are trying to extract 5th element of the list - which doesn't exist. (Remember counting starts from 0!)


```python
cities.sort(reverse=true)
print(cities)
```

<details>
Python Booleans take one of two values: True or False and are case sensitive.
</details>


```python
cities = ['San Francisco', 'Los Angeles', 'New York', 'Atlanta']
capitals = ['Sacramento', 'Boston', 'Austin', 'Atlanta']
capitals_set = set(capitals)
cities_set = set(cities)
capital_cities = capitals_set.Difference(cities_set)
print(capital_cities)
```

<details>
In the above code, variable 'capitals_set' is the object of type set. Now, there there are few attributes of a set which doesn't include 'Intersection'. So we might have spelt it wrong or we are performing some wrong operation here.
</details>


```python
path = 'C:\Users\vigna'
print(path)
```

<details>
The '\\' is a special character and must be escaped.
</details>


```python
city = 'San Fransico'
population = 881549
output = 'Population of {} is {}.'.format(city)
print(output)
```

<details>
This error is arising because there are no enough arguments provided inside the format. So there is nothing to fill for second {} hence the error for index 1.
</details>


```python
cities = ['San Francisco', 'Los Angeles', 'New York', 'Atlanta']

for city in cities:
print(city)
```

<details>
If tabs/spaces are not proper anywhere in the code block, Python raises the IndentationError error.
</details>


```python
cities = ['San Francisco', 'Los Angeles', 'New York', 'Atlanta']
for city in cities:
    if city = 'Atlanta':
        print(city)
```

<details>
If you want to select the city named 'Atlanta' by comparision, using '=' instead of '==' will give you syntax error. Code expects a condition in the If statement but you are assigning a variable.
</details>


```python
cities = ['San Francisco', 'Los Angeles', 'New York', 'Atlanta']

for city in cities:
    if city == 'Los Angeles':
        state == 'California'

print(state)
```

<details>
    Here the == operator is comparing the value of the variable `state` with the text 'California'.  As we want to assign the value to a new variable, the correct syntax is to use the = operator.
</details>


```python
import math
import pi
```

<details>
Importing the module and importing a function from the module are different in python. Here, Pi is a function inside math so it can't be called using 'import'. This error also arises because of spelling error or incorrect letter case while importing a module.
</details>


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

city1 = (22.47, 70.05)
city2 =  (28.45 , 77.02)
haversine_distance(city1)
```

<details>
The function `haversine_distance()` is defined to take 2 arguments, but we called it with only 1 argiment.
</details>
