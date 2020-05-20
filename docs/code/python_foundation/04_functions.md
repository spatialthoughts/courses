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

    Hello World


Functions can also take arguments with a default value. This helps make calling the functions simpler for the default behavior while giving an option to pass on extra arguments.


```python
lat = 37.7739
lng = -121.5687

def format_coordinates(latitude, longitude, separator=','):
        return '{}{}{}'.format(latitude, separator, longitude)

print(format_coordinates(lat, lng))
print(format_coordinates(lat, lng, '|'))
```

    37.7739,-121.5687
    37.7739|-121.5687


The default behavior of Python functions is to take *positional arguments*. You pass the arguments in the *order* that is defined by the function. Python allows functions to be called using *keyword arguments*. When we call functions in this way, the order (position) of the arguments can be changed. The main advantage of using keyword arguments is to make the code more readable and explicit.


```python
print(format_coordinates(latitude=lat, longitude=lng, separator=';'))
```

    37.7739;-121.5687


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


----
