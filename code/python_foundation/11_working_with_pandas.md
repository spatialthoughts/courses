# Working with pandas

![](https://upload.wikimedia.org/wikipedia/commons/thumb/e/ed/Pandas_logo.svg/320px-Pandas_logo.svg.png)

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
print(df.head())
```

              city   city_ascii      lat       lng        country iso2 iso3  \
    0        Tokyo        Tokyo  35.6850  139.7514          Japan   JP  JPN   
    1     New York     New York  40.6943  -73.9249  United States   US  USA   
    2  Mexico City  Mexico City  19.4424  -99.1310         Mexico   MX  MEX   
    3       Mumbai       Mumbai  19.0170   72.8570          India   IN  IND   
    4    São Paulo    Sao Paulo -23.5587  -46.6250         Brazil   BR  BRA   
    
             admin_name  capital  population          id  
    0             Tōkyō  primary  35676000.0  1392685764  
    1          New York      NaN  19354922.0  1840034016  
    2  Ciudad de México  primary  19028000.0  1484247881  
    3       Mahārāshtra    admin  18978000.0  1356226629  
    4         São Paulo    admin  18845000.0  1076532519  


There is also a `info()` method that shows basic information about the dataframe, such as number of rows/columns and data types of each column.


```python
print(df.info())
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
    None


Pandas have many ways of selecting and filtered data from a dataframe. We will now see how to use the [Boolean Filtering](https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#boolean-indexing) to filter the dataframe to rows that match a condition.


```python
home_country = 'India'
filtered = df[df['country'] == home_country]
print(filtered)
```

               city city_ascii      lat      lng country iso2 iso3  \
    3        Mumbai     Mumbai  19.0170  72.8570   India   IN  IND   
    5         Delhi      Delhi  28.6700  77.2300   India   IN  IND   
    7       Kolkata    Kolkata  22.4950  88.3247   India   IN  IND   
    34      Chennai    Chennai  13.0900  80.2800   India   IN  IND   
    36    Bengalūru  Bengaluru  12.9700  77.5600   India   IN  IND   
    ...         ...        ...      ...      ...     ...  ...  ...   
    7305      Karūr      Karur  10.9504  78.0833   India   IN  IND   
    7441     Jorhāt     Jorhat  26.7500  94.2167   India   IN  IND   
    7583      Sopur      Sopur  34.3000  74.4667   India   IN  IND   
    7681     Tezpur     Tezpur  26.6338  92.8000   India   IN  IND   
    9384        Diu        Diu  20.7197  70.9904   India   IN  IND   
    
                 admin_name capital  population          id  
    3           Mahārāshtra   admin  18978000.0  1356226629  
    5                 Delhi   admin  15926000.0  1356872604  
    7           West Bengal   admin  14787000.0  1356060520  
    34          Tamil Nādu    admin   7163000.0  1356374944  
    36            Karnātaka   admin   6787000.0  1356410365  
    ...                 ...     ...         ...         ...  
    7305        Tamil Nādu      NaN     76915.0  1356837900  
    7441              Assam     NaN     69033.0  1356638741  
    7583  Jammu and Kashmīr     NaN     63035.0  1356978065  
    7681              Assam     NaN     58851.0  1356299437  
    9384      Damān and Diu     NaN     23779.0  1356923516  
    
    [212 rows x 11 columns]


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
print(home_city_coordinates)
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
print(result)
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
print(country_df)
```

               city city_ascii      lat      lng country iso2 iso3  \
    3        Mumbai     Mumbai  19.0170  72.8570   India   IN  IND   
    5         Delhi      Delhi  28.6700  77.2300   India   IN  IND   
    7       Kolkata    Kolkata  22.4950  88.3247   India   IN  IND   
    34      Chennai    Chennai  13.0900  80.2800   India   IN  IND   
    36    Bengalūru  Bengaluru  12.9700  77.5600   India   IN  IND   
    ...         ...        ...      ...      ...     ...  ...  ...   
    7305      Karūr      Karur  10.9504  78.0833   India   IN  IND   
    7441     Jorhāt     Jorhat  26.7500  94.2167   India   IN  IND   
    7583      Sopur      Sopur  34.3000  74.4667   India   IN  IND   
    7681     Tezpur     Tezpur  26.6338  92.8000   India   IN  IND   
    9384        Diu        Diu  20.7197  70.9904   India   IN  IND   
    
                 admin_name capital  population          id     distance  
    3           Mahārāshtra   admin  18978000.0  1356226629   837.185709  
    5                 Delhi   admin  15926000.0  1356872604  1738.638856  
    7           West Bengal   admin  14787000.0  1356060520  1552.637823  
    34          Tamil Nādu    admin   7163000.0  1356374944   295.340107  
    36            Karnātaka   admin   6787000.0  1356410365     0.000000  
    ...                 ...     ...         ...         ...          ...  
    7305        Tamil Nādu      NaN     76915.0  1356837900   230.567496  
    7441              Assam     NaN     69033.0  1356638741  2312.574457  
    7583  Jammu and Kashmīr     NaN     63035.0  1356978065  2383.154991  
    7681              Assam     NaN     58851.0  1356299437  2195.314732  
    9384      Damān and Diu     NaN     23779.0  1356923516  1106.693243  
    
    [212 rows x 12 columns]


We are done with our analysis and ready to save the results. We can further filter the results to only certain columns.


```python
filtered = country_df[['city_ascii','distance']]
print(filtered)
```

         city_ascii     distance
    3        Mumbai   837.185709
    5         Delhi  1738.638856
    7       Kolkata  1552.637823
    34      Chennai   295.340107
    36    Bengaluru     0.000000
    ...         ...          ...
    7305      Karur   230.567496
    7441     Jorhat  2312.574457
    7583      Sopur  2383.154991
    7681     Tezpur  2195.314732
    9384        Diu  1106.693243
    
    [212 rows x 2 columns]


Let's rename the `city_ascii` column to give it a more readable name.


```python
filtered = filtered.rename(columns = {'city_ascii': 'city'})
print(filtered)
```

               city     distance
    3        Mumbai   837.185709
    5         Delhi  1738.638856
    7       Kolkata  1552.637823
    34      Chennai   295.340107
    36    Bengaluru     0.000000
    ...         ...          ...
    7305      Karur   230.567496
    7441     Jorhat  2312.574457
    7583      Sopur  2383.154991
    7681     Tezpur  2195.314732
    9384        Diu  1106.693243
    
    [212 rows x 2 columns]


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

----
