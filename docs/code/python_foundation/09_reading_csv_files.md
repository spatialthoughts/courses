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
data_pkg_path = 'data'
filename = 'worldcities.csv'
path = os.path.join(data_pkg_path, filename)
```


```python
f = open(path, 'r')
csv_reader = csv.DictReader(f, delimiter=',', quotechar='"')
print(csv_reader)
f.close()
```

    <csv.DictReader object at 0x0000000005528548>


## Using `enumerate()` function

When iterating over an object, many times we need a counter. We saw in the previous example, how to use a variable like `count` and increase it with every iteration. There is an easy way to do this using the built-in `enumerate()` function.


```python
cities = ['San Francisco', 'Los Angeles', 'New York', 'Atlanta']
for x in enumerate(cities):
    print(x)
```

    (0, 'San Francisco')
    (1, 'Los Angeles')
    (2, 'New York')
    (3, 'Atlanta')


We can use enumerate() on any iterable object and get a tuple with an index and the iterable value with each iteration. Let's use it to print the first 5 lines from the DictReader object.


```python
f = open(path, 'r', encoding='utf-8')
csv_reader = csv.DictReader(f, delimiter=',', quotechar='"')
for index, row in enumerate(csv_reader):
    print(row)
    if index == 4:
        break
f.close()
```

    OrderedDict([('city', 'Tokyo'), ('city_ascii', 'Tokyo'), ('lat', '35.6850'), ('lng', '139.7514'), ('country', 'Japan'), ('iso2', 'JP'), ('iso3', 'JPN'), ('admin_name', 'Tōkyō'), ('capital', 'primary'), ('population', '35676000'), ('id', '1392685764')])
    OrderedDict([('city', 'New York'), ('city_ascii', 'New York'), ('lat', '40.6943'), ('lng', '-73.9249'), ('country', 'United States'), ('iso2', 'US'), ('iso3', 'USA'), ('admin_name', 'New York'), ('capital', ''), ('population', '19354922.0'), ('id', '1840034016')])
    OrderedDict([('city', 'Mexico City'), ('city_ascii', 'Mexico City'), ('lat', '19.4424'), ('lng', '-99.1310'), ('country', 'Mexico'), ('iso2', 'MX'), ('iso3', 'MEX'), ('admin_name', 'Ciudad de México'), ('capital', 'primary'), ('population', '19028000'), ('id', '1484247881')])
    OrderedDict([('city', 'Mumbai'), ('city_ascii', 'Mumbai'), ('lat', '19.0170'), ('lng', '72.8570'), ('country', 'India'), ('iso2', 'IN'), ('iso3', 'IND'), ('admin_name', 'Mahārāshtra'), ('capital', 'admin'), ('population', '18978000'), ('id', '1356226629')])
    OrderedDict([('city', 'São Paulo'), ('city_ascii', 'Sao Paulo'), ('lat', '-23.5587'), ('lng', '-46.6250'), ('country', 'Brazil'), ('iso2', 'BR'), ('iso3', 'BRA'), ('admin_name', 'São Paulo'), ('capital', 'admin'), ('population', '18845000'), ('id', '1076532519')])


## Using `with` statement


The code for file handling requires we open a file, do something with the file object and then close the file. That is tedious and it is possible that you may forget to call `close()` on the file. If the code for processing encounters an error the file is not closed property, it may result in bugs - especially when writing files.

The preferred way to work with file objects is using the `with` statement. It results in simpler and cleaer code - which also ensures file objects are closed properly in case of errors.

As you see below, we open the file and use the file object `f` in a `with` statement. Python takes care of closing the file when the execution of code within the statement is complete.


```python
with open(path, 'r', encoding='utf-8') as f:
    csv_reader = csv.DictReader(f)
```

## Filtering rows

We can use conditional statement while iterating over the rows, to select and process rows that meet certain criterial. Let's count how many cities from a particular country are present in the file.

Replace the `home_country` variable with your home country below.


```python
home_country = 'India'
num_cities = 0

with open(path, 'r', encoding='utf-8') as f:
    csv_reader = csv.DictReader(f)

    for row in csv_reader:
        if row['country'] == home_country:
            num_cities += 1
            
print(num_cities)
```

    212


## Calculating distance

Let's apply the skills we have learnt so far to solve a complete problem. We want to read the `worldcities.csv` file, find all cities within a home country, calculate the distance to each cities from a home city and write the results to a new CSV file.

First we find the coordinates of the out selected `home_city` from the file. Replace the `home_city` below with your hometown or a large city within your country. Note that we are using the `city_ascii` field for city name comparison, so make sure the `home_city` variable contains the ASCII version of the city name.


```python
home_city = 'Bengaluru'

home_city_coordinates = ()

with open(path, 'r', encoding='utf-8') as f:
    csv_reader = csv.DictReader(f)
    for row in csv_reader:
        if row['city_ascii'] == home_city:
            lat = row['lat']
            lng = row['lng']
            home_city_coordinates = (lat, lng)
            break
        
print(home_city_coordinates)
```

    ('12.9700', '77.5600')


Now we can loop through the file, find a city in the chosen home country and call the `geopy.distance.geodesic()` function to calculate the distance. In the code below, we are just computing first 5 matches.


```python
from geopy import distance

counter = 0
with open(path, 'r', encoding='utf-8') as f:
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

    Mumbai 837.1857087990928
    Delhi 1738.638855782645
    Kolkata 1552.6378233436674
    Chennai 295.3401073046679
    Hyderabad 500.0477286304823


## Writing files

Instead of printing the results, let's write the results to a new file. Similar to csv.DictReader(), there is a companion `csv.DictWriter()` method to write files. We create a `csv_writer` object and then write rows to it using the `writerow()` method.

First we create an `output` folder to save the results. We can first check if the folder exists and if it doesn't exist, we can create it.


```python
output_dir = 'output'
if not os.path.exists(output_dir):
    os.mkdir(output_dir)
```


```python
output_filename = 'cities_distance.csv'
output_path = os.path.join(output_dir, output_filename)

with open(output_path, mode='w', encoding='utf-8') as output_file:
    fieldnames = ['city', 'distance_from_home']
    csv_writer = csv.DictWriter(output_file, fieldnames=fieldnames)
    csv_writer.writeheader()
    
    # Now we read the input file, calculate distance and
    # write a row to the output 
    with open(path, 'r', encoding='utf-8') as f:
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

data_pkg_path = 'data'
input_filename = 'worldcities.csv'
input_path = os.path.join(data_pkg_path, filename)
output_filename = 'cities_distance.csv'
output_dir = 'output'
output_path = os.path.join(output_dir, output_filename)

home_city = 'Bengaluru'
home_country = 'India'

with open(input_path, 'r', encoding='utf-8') as input_file:
    csv_reader = csv.DictReader(input_file)
    for row in csv_reader:
        if row['city_ascii'] == home_city:
            home_city_coordinates = (row['lat'], row['lng'])
            break

with open(output_path, mode='w') as output_file:
    fieldnames = ['city', 'distance_from_home']
    csv_writer = csv.DictWriter(output_file, fieldnames=fieldnames)
    csv_writer.writeheader()

    with open(input_path, 'r', encoding='utf-8') as input_file:
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

    Successfully written output file at output\cities_distance.csv


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
