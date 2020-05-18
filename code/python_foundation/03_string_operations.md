# String Operations


```python
city = 'San Francisco'
print(len(city))
```


```python
print(city.split())
```


```python
print(city.upper())
```


```python
city[0]
```


```python
city[-1]
```


```python
city[0:3]
```


```python
city[4:]
```

## Exercise

Use the string slicing to print the last 5 characters of a string. 

## Escaping characters

Certain characters are special since they are by Python language itself. For example, the quote character **'** is used to define a string. What do you do if your string contains a quote character?

In Python strings, the backslash **\\** is a special character, also called the **escape** character. Prefixing any character with a backslash makes it an ordinary character. (Hint: Prefixing a backslash with a backshalsh makes it ordinary too!)

It is also used for representing certain whitespace characters, \n is a newline, \t is a tab etc.

Remove the # from the cell below and run it.


```python
# my_string = 'It's a beautiful day!'
```

We can fix the error by espacing the single quote within the string.


```python
my_string = 'It\'s a beautiful day!'
```

Alternatively, you can also use double-quotes if your string contains a single-quote.


```python
my_string = "It's a beautiful day!"
```

What if our string contains both single and double quotes?

We can use triple-quotes! Enclosing the string in triple quotes ensures both single and double quotes are treated correctly. 


```python
latitude = '''37° 46' 26.2992 N'''
longitude = '''122° 25' 52.6692" W'''
print(latitude, longitude)
```

Backslashes pose another problem when dealing with Windows paths



```python
#path = 'C:\Users\ujaval'
#print(path)
```

Prefixing a string with **r** makes is a *Raw string*. Which doesn't interpret backslash as a special character


```python
path = r'C:\Users\ujaval'
print(path)
```

## Printing Strings

Modern way of creating strings from variables is using the `format()` method


```python
city = 'San Fransico'
population = 881549
output = 'Population of {} is {}.'.format(city, population)
print(output)
```

You can also use the format method to control the precision of the numbers


```python
latitude = 37.7749
longitude = -122.4194

coordinates = '{:.2f},{:.2f}'.format(latitude, longitude)
print(coordinates)
```


```python

```
