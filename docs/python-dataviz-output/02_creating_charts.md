# Creating Charts

Pandas allows you to read structured datasets and visualize them using the `plot()` method. By default, Pandas uses `matplotlib` to create the plots.

In this notebook, we will take work with open dataset of crime in London.


```python
import pandas as pd
import os
import glob

%matplotlib inline
import matplotlib.pyplot as plt
```

We have 12 different CSV files containing crime data for each month of 2020. We can use the `glob` module to find all files matching a pattern.


```python
data_pkg_path = 'data'
folder = 'crime'
file_pattern = '2020-*.csv'
file_path_pattern = os.path.join(data_pkg_path, folder, file_pattern)

file_list = []
for file in glob.glob(file_path_pattern):
    file_list.append(file)
file_list
```

It will be helpful to merge all these files into a single dataframe. We can use `pd.concat()` to merge a list of dataframes.


```python
dataframe_list = []

for file in file_list:
    df = pd.read_csv(file)
    dataframe_list.append(df)

merged_df = pd.concat(dataframe_list)
```

Let's create a pie-chart showing the distribution of different types of crime. Pandas `groupby()` function allows us to calculate group statistics.


```python
type_counts = merged_df.groupby('Crime type').size()
type_counts
```

We now uses the `plot()` method to create the chart. This method is a wrapper around `matplotlib` and can accept supported arguments from it. 

Reference: [pandas.DataFrame.plot](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.html)


```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(15,7)
type_counts.plot(kind='pie', ax=ax)
plt.show()
```


```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(15,7)
type_counts.plot(kind='pie', ax=ax, wedgeprops={'linewidth': 1.0, 'edgecolor': 'white'}, label='')
plt.tight_layout()
plt.title('Crime Types', fontsize = 18)

plt.show()
```

We can also chart the trend of crime over the year. For this, let's group the data by month.


```python
monthly_counts = merged_df.groupby('Month').size()
monthly_counts
```


```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(15,7)
monthly_counts.plot(kind='bar', ax=ax)
plt.show()
```


```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(15,7)
monthly_counts.plot(kind='bar', ax=ax)
monthly_counts.plot(kind='line', ax=ax, color='red', marker='o')
plt.show()
```

## Exercise

Plot the trend of Bicycle thefts as a line chart. The cell below filters the `merged_df` dataframe to select incidents of 'Bicycle theft'. Group the results by months and plot the results.


```python
bicycle_thefts = merged_df[merged_df['Crime type'] == 'Bicycle theft']
```
