# Working with pandas

Pandas is a powerful library for working with data. Pandas provides fast and easy functions for reading data from files, and analyzing it.

Pandas is based on another library called `numpy` - which is widely used in scientific computing. Pandas extends `numpy` and provides new data types such as **Index**, **Series** and **DataFrames**.

Pandas implementation is very fast and efficient - so compared to other methods of data processing - using `pandas` results is simpler code and quick processing. We will now re-implement our code for reading a file and computing distance using Pandas.

By convention, `pandas` is commonly imported as `pd`


```python
import pandas as pd
```


```python
import os
home_dir = os.path.expanduser('~')
data_pkg_path = 'Downloads/python_foundation/'
filename = 'worldcities.csv'
path = os.path.join(home_dir, data_pkg_path, filename)
```

A **DataFrame** is the most used Pandas object. You can think of a DataFrame being equivalent to a Spreadsheet or an Attribute Table of a GIS layer. 

Pandas provide easy methods to directly read files into a DataFrame. You can use methods such as `read_csv()`, `read_excel()`, `read_hdf()` and so forth to read a variety of formats. Here we will read the `worldcitites.csv` file using `read_csv()` method.


```python
df = pd.read_csv(path)
```

Once the file is read and a DataFrame object is created, we can inspect it using the `head()` method. You can see that we are not using `print()` here. Jupyter notebooks call the `display()` method on objects implicitely and gives us a nicely formatted output. This is very useful when dealing with DataFrames.


```python
df.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>city</th>
      <th>city_ascii</th>
      <th>lat</th>
      <th>lng</th>
      <th>country</th>
      <th>iso2</th>
      <th>iso3</th>
      <th>admin_name</th>
      <th>capital</th>
      <th>population</th>
      <th>id</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Tokyo</td>
      <td>Tokyo</td>
      <td>35.6850</td>
      <td>139.7514</td>
      <td>Japan</td>
      <td>JP</td>
      <td>JPN</td>
      <td>Tōkyō</td>
      <td>primary</td>
      <td>35676000.0</td>
      <td>1392685764</td>
    </tr>
    <tr>
      <th>1</th>
      <td>New York</td>
      <td>New York</td>
      <td>40.6943</td>
      <td>-73.9249</td>
      <td>United States</td>
      <td>US</td>
      <td>USA</td>
      <td>New York</td>
      <td>NaN</td>
      <td>19354922.0</td>
      <td>1840034016</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Mexico City</td>
      <td>Mexico City</td>
      <td>19.4424</td>
      <td>-99.1310</td>
      <td>Mexico</td>
      <td>MX</td>
      <td>MEX</td>
      <td>Ciudad de México</td>
      <td>primary</td>
      <td>19028000.0</td>
      <td>1484247881</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Mumbai</td>
      <td>Mumbai</td>
      <td>19.0170</td>
      <td>72.8570</td>
      <td>India</td>
      <td>IN</td>
      <td>IND</td>
      <td>Mahārāshtra</td>
      <td>admin</td>
      <td>18978000.0</td>
      <td>1356226629</td>
    </tr>
    <tr>
      <th>4</th>
      <td>São Paulo</td>
      <td>Sao Paulo</td>
      <td>-23.5587</td>
      <td>-46.6250</td>
      <td>Brazil</td>
      <td>BR</td>
      <td>BRA</td>
      <td>São Paulo</td>
      <td>admin</td>
      <td>18845000.0</td>
      <td>1076532519</td>
    </tr>
  </tbody>
</table>
</div>



There is also a `info()` method that shows basic information about the dataframe, such as number of rows/columns and data types of each column.


```python
df.info()
```

    <class 'pandas.core.frame.DataFrame'>
    RangeIndex: 15493 entries, 0 to 15492
    Data columns (total 11 columns):
     #   Column      Non-Null Count  Dtype  
    ---  ------      --------------  -----  
     0   city        15493 non-null  object 
     1   city_ascii  15493 non-null  object 
     2   lat         15493 non-null  float64
     3   lng         15493 non-null  float64
     4   country     15493 non-null  object 
     5   iso2        15462 non-null  object 
     6   iso3        15493 non-null  object 
     7   admin_name  15302 non-null  object 
     8   capital     5246 non-null   object 
     9   population  13808 non-null  float64
     10  id          15493 non-null  int64  
    dtypes: float64(3), int64(1), object(7)
    memory usage: 1.3+ MB


Pandas have many ways of selecting and filtered data from a dataframe. We will now see how to use the [Boolean Filtering](https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#boolean-indexing) to filter the dataframe to rows that match a condition.


```python
home_country = 'India'
df[df['country'] == home_country]
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>city</th>
      <th>city_ascii</th>
      <th>lat</th>
      <th>lng</th>
      <th>country</th>
      <th>iso2</th>
      <th>iso3</th>
      <th>admin_name</th>
      <th>capital</th>
      <th>population</th>
      <th>id</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>3</th>
      <td>Mumbai</td>
      <td>Mumbai</td>
      <td>19.0170</td>
      <td>72.8570</td>
      <td>India</td>
      <td>IN</td>
      <td>IND</td>
      <td>Mahārāshtra</td>
      <td>admin</td>
      <td>18978000.0</td>
      <td>1356226629</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Delhi</td>
      <td>Delhi</td>
      <td>28.6700</td>
      <td>77.2300</td>
      <td>India</td>
      <td>IN</td>
      <td>IND</td>
      <td>Delhi</td>
      <td>admin</td>
      <td>15926000.0</td>
      <td>1356872604</td>
    </tr>
    <tr>
      <th>7</th>
      <td>Kolkata</td>
      <td>Kolkata</td>
      <td>22.4950</td>
      <td>88.3247</td>
      <td>India</td>
      <td>IN</td>
      <td>IND</td>
      <td>West Bengal</td>
      <td>admin</td>
      <td>14787000.0</td>
      <td>1356060520</td>
    </tr>
    <tr>
      <th>34</th>
      <td>Chennai</td>
      <td>Chennai</td>
      <td>13.0900</td>
      <td>80.2800</td>
      <td>India</td>
      <td>IN</td>
      <td>IND</td>
      <td>Tamil Nādu</td>
      <td>admin</td>
      <td>7163000.0</td>
      <td>1356374944</td>
    </tr>
    <tr>
      <th>36</th>
      <td>Bengalūru</td>
      <td>Bengaluru</td>
      <td>12.9700</td>
      <td>77.5600</td>
      <td>India</td>
      <td>IN</td>
      <td>IND</td>
      <td>Karnātaka</td>
      <td>admin</td>
      <td>6787000.0</td>
      <td>1356410365</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>7305</th>
      <td>Karūr</td>
      <td>Karur</td>
      <td>10.9504</td>
      <td>78.0833</td>
      <td>India</td>
      <td>IN</td>
      <td>IND</td>
      <td>Tamil Nādu</td>
      <td>NaN</td>
      <td>76915.0</td>
      <td>1356837900</td>
    </tr>
    <tr>
      <th>7441</th>
      <td>Jorhāt</td>
      <td>Jorhat</td>
      <td>26.7500</td>
      <td>94.2167</td>
      <td>India</td>
      <td>IN</td>
      <td>IND</td>
      <td>Assam</td>
      <td>NaN</td>
      <td>69033.0</td>
      <td>1356638741</td>
    </tr>
    <tr>
      <th>7583</th>
      <td>Sopur</td>
      <td>Sopur</td>
      <td>34.3000</td>
      <td>74.4667</td>
      <td>India</td>
      <td>IN</td>
      <td>IND</td>
      <td>Jammu and Kashmīr</td>
      <td>NaN</td>
      <td>63035.0</td>
      <td>1356978065</td>
    </tr>
    <tr>
      <th>7681</th>
      <td>Tezpur</td>
      <td>Tezpur</td>
      <td>26.6338</td>
      <td>92.8000</td>
      <td>India</td>
      <td>IN</td>
      <td>IND</td>
      <td>Assam</td>
      <td>NaN</td>
      <td>58851.0</td>
      <td>1356299437</td>
    </tr>
    <tr>
      <th>9384</th>
      <td>Diu</td>
      <td>Diu</td>
      <td>20.7197</td>
      <td>70.9904</td>
      <td>India</td>
      <td>IN</td>
      <td>IND</td>
      <td>Damān and Diu</td>
      <td>NaN</td>
      <td>23779.0</td>
      <td>1356923516</td>
    </tr>
  </tbody>
</table>
<p>212 rows × 11 columns</p>
</div>



Filtered dataframe is a just view of the original data and we cannot make changes to it. We can save the filtered view to a new dataframe using the `copy()` method.


```python
country_df = df[df['country'] == home_country].copy()
```

To locate a particular row or column from a dataframe, Pandas providea `loc[]` and `iloc[]` methods - that allows you to *locate* particular slices of data. Learn about [different indexing methods](https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#different-choices-for-indexing) in Pandas. Here we can use `iloc[]` to find the row matching the `home_city` name. Since `iloc[]` uses index, the *0* here refers to the first row.


```python
home_city = 'Bengaluru'
filtered = country_df[country_df['city_ascii'] == home_city]
filtered.iloc[0]
```




    city           Bengalūru
    city_ascii     Bengaluru
    lat                12.97
    lng                77.56
    country            India
    iso2                  IN
    iso3                 IND
    admin_name     Karnātaka
    capital            admin
    population     6.787e+06
    id            1356410365
    Name: 36, dtype: object



Now that we have filtered down the data to a single row, we can select individual column values using column names.


```python
home_city_coordinates = (filtered.iloc[0]['lat'], filtered.iloc[0]['lng'])
home_city_coordinates
```




    (12.97, 77.56)



Let's learn how to do calculations on a dataframe. We can iterate over each row and perform some calculations. But pandas provide a much more efficient way. You can use the `apply()` method to run a function on each row. This is fast and makes it easy to complex computations on large datasets.

The `apply()` function takes 2 arguments. A function to apply, and the axis along which to apply it. `axis=0` means it will be applied to columns and `axis=1` means it will apply to rows.


```python
from geopy import distance

def calculate_distance(row):
    city_coordinates = (row['lat'], row['lng'])
    return distance.geodesic(city_coordinates, home_city_coordinates).km

result = country_df.apply(calculate_distance, axis=1)
result
```




    3        837.185709
    5       1738.638856
    7       1552.637823
    34       295.340107
    36         0.000000
               ...     
    7305     230.567496
    7441    2312.574457
    7583    2383.154991
    7681    2195.314732
    9384    1106.693243
    Length: 212, dtype: float64



We can add these results to the dataframe by simply assigning the result to a new column.


```python
country_df['distance'] = result
country_df
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>city</th>
      <th>city_ascii</th>
      <th>lat</th>
      <th>lng</th>
      <th>country</th>
      <th>iso2</th>
      <th>iso3</th>
      <th>admin_name</th>
      <th>capital</th>
      <th>population</th>
      <th>id</th>
      <th>distance</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>3</th>
      <td>Mumbai</td>
      <td>Mumbai</td>
      <td>19.0170</td>
      <td>72.8570</td>
      <td>India</td>
      <td>IN</td>
      <td>IND</td>
      <td>Mahārāshtra</td>
      <td>admin</td>
      <td>18978000.0</td>
      <td>1356226629</td>
      <td>837.185709</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Delhi</td>
      <td>Delhi</td>
      <td>28.6700</td>
      <td>77.2300</td>
      <td>India</td>
      <td>IN</td>
      <td>IND</td>
      <td>Delhi</td>
      <td>admin</td>
      <td>15926000.0</td>
      <td>1356872604</td>
      <td>1738.638856</td>
    </tr>
    <tr>
      <th>7</th>
      <td>Kolkata</td>
      <td>Kolkata</td>
      <td>22.4950</td>
      <td>88.3247</td>
      <td>India</td>
      <td>IN</td>
      <td>IND</td>
      <td>West Bengal</td>
      <td>admin</td>
      <td>14787000.0</td>
      <td>1356060520</td>
      <td>1552.637823</td>
    </tr>
    <tr>
      <th>34</th>
      <td>Chennai</td>
      <td>Chennai</td>
      <td>13.0900</td>
      <td>80.2800</td>
      <td>India</td>
      <td>IN</td>
      <td>IND</td>
      <td>Tamil Nādu</td>
      <td>admin</td>
      <td>7163000.0</td>
      <td>1356374944</td>
      <td>295.340107</td>
    </tr>
    <tr>
      <th>36</th>
      <td>Bengalūru</td>
      <td>Bengaluru</td>
      <td>12.9700</td>
      <td>77.5600</td>
      <td>India</td>
      <td>IN</td>
      <td>IND</td>
      <td>Karnātaka</td>
      <td>admin</td>
      <td>6787000.0</td>
      <td>1356410365</td>
      <td>0.000000</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>7305</th>
      <td>Karūr</td>
      <td>Karur</td>
      <td>10.9504</td>
      <td>78.0833</td>
      <td>India</td>
      <td>IN</td>
      <td>IND</td>
      <td>Tamil Nādu</td>
      <td>NaN</td>
      <td>76915.0</td>
      <td>1356837900</td>
      <td>230.567496</td>
    </tr>
    <tr>
      <th>7441</th>
      <td>Jorhāt</td>
      <td>Jorhat</td>
      <td>26.7500</td>
      <td>94.2167</td>
      <td>India</td>
      <td>IN</td>
      <td>IND</td>
      <td>Assam</td>
      <td>NaN</td>
      <td>69033.0</td>
      <td>1356638741</td>
      <td>2312.574457</td>
    </tr>
    <tr>
      <th>7583</th>
      <td>Sopur</td>
      <td>Sopur</td>
      <td>34.3000</td>
      <td>74.4667</td>
      <td>India</td>
      <td>IN</td>
      <td>IND</td>
      <td>Jammu and Kashmīr</td>
      <td>NaN</td>
      <td>63035.0</td>
      <td>1356978065</td>
      <td>2383.154991</td>
    </tr>
    <tr>
      <th>7681</th>
      <td>Tezpur</td>
      <td>Tezpur</td>
      <td>26.6338</td>
      <td>92.8000</td>
      <td>India</td>
      <td>IN</td>
      <td>IND</td>
      <td>Assam</td>
      <td>NaN</td>
      <td>58851.0</td>
      <td>1356299437</td>
      <td>2195.314732</td>
    </tr>
    <tr>
      <th>9384</th>
      <td>Diu</td>
      <td>Diu</td>
      <td>20.7197</td>
      <td>70.9904</td>
      <td>India</td>
      <td>IN</td>
      <td>IND</td>
      <td>Damān and Diu</td>
      <td>NaN</td>
      <td>23779.0</td>
      <td>1356923516</td>
      <td>1106.693243</td>
    </tr>
  </tbody>
</table>
<p>212 rows × 12 columns</p>
</div>



We are done with our analysis and ready to save the results. We can further filter the results to only certain columns.


```python
filtered = country_df[['city_ascii','distance']]
filtered
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>city_ascii</th>
      <th>distance</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>3</th>
      <td>Mumbai</td>
      <td>837.185709</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Delhi</td>
      <td>1738.638856</td>
    </tr>
    <tr>
      <th>7</th>
      <td>Kolkata</td>
      <td>1552.637823</td>
    </tr>
    <tr>
      <th>34</th>
      <td>Chennai</td>
      <td>295.340107</td>
    </tr>
    <tr>
      <th>36</th>
      <td>Bengaluru</td>
      <td>0.000000</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>7305</th>
      <td>Karur</td>
      <td>230.567496</td>
    </tr>
    <tr>
      <th>7441</th>
      <td>Jorhat</td>
      <td>2312.574457</td>
    </tr>
    <tr>
      <th>7583</th>
      <td>Sopur</td>
      <td>2383.154991</td>
    </tr>
    <tr>
      <th>7681</th>
      <td>Tezpur</td>
      <td>2195.314732</td>
    </tr>
    <tr>
      <th>9384</th>
      <td>Diu</td>
      <td>1106.693243</td>
    </tr>
  </tbody>
</table>
<p>212 rows × 2 columns</p>
</div>



Let's rename the `city_ascii` column to give it a more readable name.


```python
filtered = filtered.rename(columns = {'city_ascii': 'city'})
filtered
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>city</th>
      <th>distance</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>3</th>
      <td>Mumbai</td>
      <td>837.185709</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Delhi</td>
      <td>1738.638856</td>
    </tr>
    <tr>
      <th>7</th>
      <td>Kolkata</td>
      <td>1552.637823</td>
    </tr>
    <tr>
      <th>34</th>
      <td>Chennai</td>
      <td>295.340107</td>
    </tr>
    <tr>
      <th>36</th>
      <td>Bengaluru</td>
      <td>0.000000</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>7305</th>
      <td>Karur</td>
      <td>230.567496</td>
    </tr>
    <tr>
      <th>7441</th>
      <td>Jorhat</td>
      <td>2312.574457</td>
    </tr>
    <tr>
      <th>7583</th>
      <td>Sopur</td>
      <td>2383.154991</td>
    </tr>
    <tr>
      <th>7681</th>
      <td>Tezpur</td>
      <td>2195.314732</td>
    </tr>
    <tr>
      <th>9384</th>
      <td>Diu</td>
      <td>1106.693243</td>
    </tr>
  </tbody>
</table>
<p>212 rows × 2 columns</p>
</div>



Now that we have added filtered the original data and computed the distance for all cities, we can save the resulting dataframe to a file. Similar to read methods, Pandas have several write methods, such as `to_csv()`, `to_excel()` etc.

Here we will use the `to_csv()` method to write a CSV file. Pandas assigns an index column (unique integer values) to a dataframe by default. We specify `index=False` so that this index is not added to our output.


```python
output_filename = 'cities_distance_pandas.csv'
output_dir = 'Downloads'
output_path = os.path.join(home_dir, output_dir, output_filename)
filtered.to_csv(output_path, index=False)
```

## Exercise

You will notice that the output file contains a row with the `home_city` as well. Modify the `filtered` dataframe to remove this row and write it to a file.

Hint: Use the Boolean filtering method we learnt earlier to select rows that do not match the `home_city`.
