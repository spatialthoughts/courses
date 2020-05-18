# Functions

```
def my_function():
    ....
    ....
    return something
```


```python
def greet(name):
    return 'Hello ' + name

print(greet('World'))
```

    Hello World


## Exercise

Functions can take multiple arguments. Let's write a function to convert coordinates from degrees, minutes, seconds to decimal degrees. This conversion is needed quite often when working with data collected from GPS devices.

- 1 degree is equal to 60 minutes
- 1 minute is equal to 60 seconds (3600 seconds)

To calculate decimal degrees, we can use the formula below:
Decimal Degrees = degrees + (minutes/60) + (seconds/3600)

Delete the `pass` statement and replace it with the code for the formula. If the code is correct, you should see the result 37.773972 -121.568703


```python
latitude = (37, 46, 26.2992)
longitude = (-122, 25, 52.6692)

def dms_to_decimal(degrees, minutes, seconds):
    pass

lat_decimal = dms_to_decimal(latitude[0], latitude[1], latitude[2])
lon_decimal = dms_to_decimal(longitude[0], longitude[1], longitude[2])
print(lat_decimal, lon_decimal)
```

    None None



```python

```
