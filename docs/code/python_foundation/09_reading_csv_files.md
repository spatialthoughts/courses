# Reading CSV Files

Comma-separated Values (CSV) are the most common text-based file format for sharing geospatial data. The structure of the file is 1 data record per line, with individual *columns* separated by a comma. 

In general, the separator character is called a delimiter. Other popular delimiters include the tab (\\t), colon (:) and semi-colon (;) characters. 

Reading CSV file properly requires us to know which delimiter is being used, along with quote character to surround the field values that contain space of the delimiter character. Since reading delimited text file is a very common operation, and can be tricky to handle all the corner cases, Python comes with its own library called `csv` for easy reading and writing of CSV files. To use it, you just have to import it.



```python
import csv
```

The preferred way to read CSV files is using the `DictReader()` method. Which directly reads each row and creates a dictionary from it - with column names as *key* and column values as *value*. Let's see how to read a file using the `csv.DictReader()` method.


```python
import os
home_dir = os.path.expanduser('~')
data_pkg_path = 'Downloads/python_foundation/'
filename = 'worldcities.csv'
path = os.path.join(home_dir, data_pkg_path, filename)
```


```python
f = open(path, 'r')
csv_reader = csv.DictReader(f, delimiter=',', quotechar='"')
print(csv_reader)
f.close()
```

## Using `enumerate()` function

When iterating over an object, many times we need a counter. We saw in the previous example, how to use a variable like `count` and increase it with every iteration. There is an easy way to do this using the built-in `enumerate()` function.


```python
cities = ['San Francisco', 'Los Angeles', 'New York', 'Atlanta']
for x in enumerate(cities):
    print(x)
```

We can use enumerate() on any iterable object and get a tuple with an index and the iterable value with each iteration. Let's use it to print the first 5 lines from the DictReader object.


```python
f = open(path, 'r')
csv_reader = csv.DictReader(f, delimiter=',', quotechar='"')
for index, row in enumerate(csv_reader):
    print(row)
    if index == 4:
        break
f.close()
```

## Using `with` statement


The code for file handling requires we open a file, do something with the file object and then close the file. That is tedious and it is possible that you may forget to call `close()` on the file. If the code for processing encounters an error the file is not closed property, it may result in bugs - especially when writing files.

The preferred way to work with file objects is using the `with` statement. It results in simpler and cleaer code - which also ensures file objects are closed properly in case of errors.

As you see below, we open the file and use the file object `f` in a `with` statement. Python takes care of closing the file when the execution of code within the statement is complete.


```python
with open(path, 'r') as f:
    csv_reader = csv.DictReader(f)
```

## Filtering rows

We can use conditional statement while iterating over the rows, to select and process rows that meet certain criterial. Let's count how many cities from a particular country are present in the file.

Replace the `home_country` variable with your home country below.


```python
home_country = 'India'
num_cities = 0

with open(path, 'r') as f:
    csv_reader = csv.DictReader(f)

    for row in csv_reader:
        if row['country'] == home_country:
            num_cities += 1
            
print(num_cities)
```

## Calculating distance

Let's apply the skills we have learnt so far to solve a complete problem. We want to read the `worldcities.csv` file, find all cities within a home country, calculate the distance to each cities from a home city and write the results to a new CSV file.

First we find the coordinates of the out selected `home_city` from the file. Replace the `home_city` below with your hometown or a large city within your country. Note that we are using the `city_ascii` field for city name comparison, so make sure the `home_city` variable contains the ASCII version of the city name.


```python
home_city = 'Bengaluru'

home_city_coordinates = ()

with open(path, 'r') as f:
    csv_reader = csv.DictReader(f)
    for row in csv_reader:
        if row['city_ascii'] == home_city:
            lat = row['lat']
            lng = row['lng']
            home_city_coordinates = (lat, lng)
            break
        
print(home_city_coordinates)
```

Now we can loop through the file, find a city in the chosen home country and call the `geopy.distance.geodesic()` function to calculate the distance. In the code below, we are just computing first 5 matches.


```python
from geopy import distance

counter = 0
with open(path, 'r') as f:
    csv_reader = csv.DictReader(f)
    for row in csv_reader:
        if (row['country'] == home_country and
            row['city_ascii'] != home_city):
            city_coordinates = (row['lat'], row['lng'])
            city_distance = distance.geodesic(
                city_coordinates, home_city_coordinates).km
            print(row['city_ascii'], city_distance)
            counter += 1
            
        if counter == 5:
            break
            
```

## Writing files

Instead of printing the results, let's write the results to a new file. Similar to csv.DictReader(), there is a companion `csv.DictWriter()` method to write files. We create a `csv_writer` object and then write rows to it using the `writerow()` method.


```python
output_filename = 'cities_distance.csv'
output_dir = 'Downloads'

output_path = os.path.join(home_dir, output_dir, output_filename)

with open(output_path, mode='w') as output_file:
    fieldnames = ['city', 'distance_from_home']
    csv_writer = csv.DictWriter(output_file, fieldnames=fieldnames)
    csv_writer.writeheader()
    
    # Now we read the input file, calculate distance and
    # write a row to the output 
    with open(path, 'r') as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            if (row['country'] == home_country and
                row['city_ascii'] != home_city):
                city_coordinates = (row['lat'], row['lng'])
                city_distance = distance.geodesic(
                    city_coordinates, home_city_coordinates).km
                csv_writer.writerow(
                    {'city': row['city_ascii'],
                     'distance_from_home': city_distance}
                )
```

Below is the complete code for our task of reading a file, filtering it, calculating distance and writing the results to a file.


```python
import csv
import os
from geopy import distance

home_dir = os.path.expanduser('~')

input_filename = 'worldcities.csv'
input_dir = 'Downloads/python_foundation/'
data_pkg_path = 'Downloads/python_foundation/'
input_path = os.path.join(home_dir, data_pkg_path, input_filename)
output_filename = 'cities_distance.csv'
output_dir = 'Downloads'
output_path = os.path.join(home_dir, output_dir, output_filename)

home_city = 'Bengaluru'
home_country = 'India'

with open(input_path, 'r') as input_file:
    csv_reader = csv.DictReader(input_file)
    for row in csv_reader:
        if row['city_ascii'] == home_city:
            home_city_coordinates = (row['lat'], row['lng'])
            break

with open(output_path, mode='w') as output_file:
    fieldnames = ['city', 'distance_from_home']
    csv_writer = csv.DictWriter(output_file, fieldnames=fieldnames)
    csv_writer.writeheader()

    with open(input_path, 'r') as input_file:
        csv_reader = csv.DictReader(input_file)
        for row in csv_reader:
            if (row['country'] == home_country and
                row['city_ascii'] != home_city):
                city_coordinates = (row['lat'], row['lng'])
                city_distance = distance.geodesic(
                    city_coordinates, home_city_coordinates).km
                csv_writer.writerow(
                    {'city': row['city_ascii'],
                     'distance_from_home': city_distance}
                )

print('Successfully written output file at {}'.format(output_path))
```

## Exercise

Let's say we want to repeat the same process for another city. Or maybe all the cities in a country. The code above would require us to change the `home_city`, `home_country` and `output_filename` variables for the new city and run the code again manually.

Instead, we can create a *function* that does the operation based on given city name.

```
def write_distance_file(home_city, home_country, output_filename):
    ....
    ....
    print('Successfully written output file at {}'.format(output_path))
```

Then we can call the function like below

```
write_distance_file('Frankfurt', 'Germany', 'frankfurt_distance.csv')
write_distance_file('New York', 'United States', 'nyc_distance.csv')
```

Insert a new code cell below and create the `write_distance_file` function below. Then call it to create the output file as show.

----
