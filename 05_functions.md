# Functions

A function is a block of code that takes one or more *inputs*, does some processing on them and returns one or more *outputs*. The code within the function runs only when it is called.

A funtion is defined using the `def` keyword

```
def my_function():
    ....
    ....
    return something
```

Functions are useful because they allow us to capture the logic of our code and we can run it with differnt inputs without having to write the same code again and again.


```python
def greet(name):
    return 'Hello ' + name

print(greet('World'))
```

Functions can also take arguments with a default value. This helps make calling the functions simpler for the default behavior while giving an option to pass on extra arguments.


```python
lat = 37.7739
lng = -121.5687

def format_coordinates(latitude, longitude, separator=','):
        return '{}{}{}'.format(latitude, separator, longitude)

print(format_coordinates(lat, lng))
print(format_coordinates(lat, lng, '|'))
```

The default behavior of Python functions is to take *positional arguments*. You pass the arguments in the *order* that is defined by the function. Python allows functions to be called using *keyword arguments*. When we call functions in this way, the order (position) of the arguments can be changed. The main advantage of using keyword arguments is to make the code more readable and explicit.


```python
print(format_coordinates(latitude=lat, longitude=lng, separator=';'))
```

## Exercise

Functions can take multiple arguments. Let's write a function to convert coordinates from degrees, minutes, seconds to decimal degrees. This conversion is needed quite often when working with data collected from GPS devices.

- 1 degree is equal to 60 minutes
- 1 minute is equal to 60 seconds (3600 seconds)

To calculate decimal degrees, we can use the formula below:

If degrees are positive:

`Decimal Degrees = degrees + (minutes/60) + (seconds/3600)`

If degrees are negative

`Decimal Degrees = degrees - (minutes/60) - (seconds/3600)`

Delete the `pass` statement and replace it with the code for the formula. If the code is correct, you should see the result 37.773972 -121.56869


```python
latitude = (37, 46, 26.2992)
longitude = (-121, 34, 7.32)

def dms_to_decimal(degrees, minutes, seconds):
    pass

# Extract the degree, minute and seconds values from the tuple
lat_deg, lat_min, lat_sec = latitude
lon_deg, lon_min, lon_sec = longitude

lat_decimal = dms_to_decimal(lat_deg, lat_min, lat_sec)
lon_decimal = dms_to_decimal(lon_deg, lon_min, lon_sec)
print(lat_decimal, lon_decimal)
```

----
