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

Functions can take multiple arguments. Let's write a function to convert coordinates from degrees, minutes, seconds to decimal degrees. This conversion is needed quite often when working with data collected from GPS devices.

- 1 degree is equal to 60 minutes
- 1 minute is equal to 60 seconds (3600 seconds)

To calculate decimal degrees, we can use the formula below:

If degrees are positive:

`Decimal Degrees = degrees + (minutes/60) + (seconds/3600)`

If degrees are negative

`Decimal Degrees = degrees - (minutes/60) - (seconds/3600)`


```python
def dms_to_decimal(degrees, minutes, seconds):
    if degrees < 0:
        result = degrees - minutes/60 - seconds/3600
    else:
        result = degrees + minutes/60 + seconds/3600
    return result
```


```python
output = dms_to_decimal(10, 10, 10)
print(output)
```

## Exercise

Given a coordinate string with value in degree, minutes and seconds, convert it to decimal degrees by calling the `dms_to_decimal` function.


```python
def dms_to_decimal(degrees, minutes, seconds):
    if degrees < 0:
        result = degrees - minutes/60 - seconds/3600
    else:
        result = degrees + minutes/60 + seconds/3600
    return result

coordinate = '''37° 46' 26.2992"'''

# Add the code below to extract the parts from the coordinate string,
# call the function to convert to decimal degrees and print the result
```


```python
# Hint: Converting strings to numbers
# When you extract the parts from the coordinate string, they are strings
# You will need to use the built-in int() / float() functions to
# convert them to numbers
x = '25'
print(x, type(x))
y = int(x)
print(y, type(y))
```

----
