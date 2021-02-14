# Working with Pandas

![](images/python_foundation/pandas-logo.png)

Pandas is a powerful library for working with data. Pandas provides fast and easy functions for reading data from files, and analyzing it.

Pandas is based on another library called `numpy` - which is widely used in scientific computing. Pandas extends `numpy` and provides new data types such as **Index**, **Series** and **DataFrames**.

Pandas implementation is very fast and efficient - so compared to other methods of data processing - using `pandas` results is simpler code and quick processing. We will now re-implement our code for reading a file and computing distance using Pandas.

By convention, `pandas` is commonly imported as `pd`


```python
import pandas as pd
```

## Reading Files


```python
import os
data_pkg_path = 'data'
filename = 'worldcities.csv'
path = os.path.join(data_pkg_path, filename)
```

A **DataFrame** is the most used Pandas object. You can think of a DataFrame being equivalent to a Spreadsheet or an Attribute Table of a GIS layer. 

Pandas provide easy methods to directly read files into a DataFrame. You can use methods such as `read_csv()`, `read_excel()`, `read_hdf()` and so forth to read a variety of formats. Here we will read the `worldcitites.csv` file using `read_csv()` method.


```python
df = pd.read_csv(path)
```

Once the file is read and a DataFrame object is created, we can inspect it using the `head()` method. 


```python
print(df.head())
```

There is also a `info()` method that shows basic information about the dataframe, such as number of rows/columns and data types of each column.


```python
print(df.info())
```

## Filtering Data

Pandas have many ways of selecting and filtered data from a dataframe. We will now see how to use the [Boolean Filtering](https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#boolean-indexing) to filter the dataframe to rows that match a condition.


```python
home_country = 'India'
filtered = df[df['country'] == home_country]
print(filtered)
```

Filtered dataframe is a just view of the original data and we cannot make changes to it. We can save the filtered view to a new dataframe using the `copy()` method.


```python
country_df = df[df['country'] == home_country].copy()
```

To locate a particular row or column from a dataframe, Pandas providea `loc[]` and `iloc[]` methods - that allows you to *locate* particular slices of data. Learn about [different indexing methods](https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#different-choices-for-indexing) in Pandas. Here we can use `iloc[]` to find the row matching the `home_city` name. Since `iloc[]` uses index, the *0* here refers to the first row.


```python
home_city = 'Bengaluru'
filtered = country_df[country_df['city_ascii'] == home_city]
print(filtered.iloc[0])
```

Now that we have filtered down the data to a single row, we can select individual column values using column names.


```python
home_city_coordinates = (filtered.iloc[0]['lat'], filtered.iloc[0]['lng'])
print(home_city_coordinates)
```

## Performing calculations

Let's learn how to do calculations on a dataframe. We can iterate over each row and perform some calculations. But pandas provide a much more efficient way. You can use the `apply()` method to run a function on each row. This is fast and makes it easy to complex computations on large datasets.

The `apply()` function takes 2 arguments. A function to apply, and the axis along which to apply it. `axis=0` means it will be applied to columns and `axis=1` means it will apply to rows.


```python
from geopy import distance

def calculate_distance(row):
    city_coordinates = (row['lat'], row['lng'])
    return distance.geodesic(city_coordinates, home_city_coordinates).km

result = country_df.apply(calculate_distance, axis=1)
print(result)
```

We can add these results to the dataframe by simply assigning the result to a new column.


```python
country_df['distance'] = result
print(country_df)
```

We are done with our analysis and ready to save the results. We can further filter the results to only certain columns.


```python
filtered = country_df[['city_ascii','distance']]
print(filtered)
```

Let's rename the `city_ascii` column to give it a more readable name.


```python
filtered = filtered.rename(columns = {'city_ascii': 'city'})
print(filtered)
```

Now that we have added filtered the original data and computed the distance for all cities, we can save the resulting dataframe to a file. Similar to read methods, Pandas have several write methods, such as `to_csv()`, `to_excel()` etc.

Here we will use the `to_csv()` method to write a CSV file. Pandas assigns an index column (unique integer values) to a dataframe by default. We specify `index=False` so that this index is not added to our output.


```python
output_filename = 'cities_distance_pandas.csv'
output_dir = 'output'
output_path = os.path.join(output_dir, output_filename)
filtered.to_csv(output_path, index=False)
print('Successfully written output file at {}'.format(output_path))
```

## Exercise

You will notice that the output file contains a row with the `home_city` as well. Modify the `filtered` dataframe to remove this row and write it to a file.

Hint: Use the Boolean filtering method we learnt earlier to select rows that do not match the `home_city`.

----
