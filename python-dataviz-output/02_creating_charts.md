## Overview

Pandas allows you to read structured datasets and visualize them using the `plot()` method. By default, Pandas uses `matplotlib` to create the plots.

In this notebook, we will take work with open dataset of crime in London.

## Setup

The following blocks of code will install the required packages and download the datasets to your Colab environment.


```python
import pandas as pd
import os
import matplotlib.pyplot as plt
```


```python
data_folder = 'data'
output_folder = 'output'

if not os.path.exists(data_folder):
    os.mkdir(data_folder)
if not os.path.exists(output_folder):
    os.mkdir(output_folder)
```


```python
def download(url):
    filename = os.path.join(data_folder, os.path.basename(url))
    if not os.path.exists(filename):
        from urllib.request import urlretrieve
        local, _ = urlretrieve(url, filename)
        print('Downloaded ' + local)
```

We have 12 different CSV files containing crime data for each month of 2020. We download each of them to the data folder.


```python
files = [
  '2020-01-metropolitan-street.csv',
  '2020-02-metropolitan-street.csv',
  '2020-03-metropolitan-street.csv',
  '2020-04-metropolitan-street.csv',
  '2020-05-metropolitan-street.csv',
  '2020-06-metropolitan-street.csv',
  '2020-07-metropolitan-street.csv',
  '2020-08-metropolitan-street.csv',
  '2020-09-metropolitan-street.csv',
  '2020-10-metropolitan-street.csv',
  '2020-11-metropolitan-street.csv',
  '2020-12-metropolitan-street.csv'
]

data_url = 'https://github.com/spatialthoughts/python-dataviz-web/raw/main/data/crime/'

for f in files:
  url = os.path.join(data_url, f)
  download(url)

```

    Downloaded data/2020-01-metropolitan-street.csv
    Downloaded data/2020-02-metropolitan-street.csv
    Downloaded data/2020-03-metropolitan-street.csv
    Downloaded data/2020-04-metropolitan-street.csv
    Downloaded data/2020-05-metropolitan-street.csv
    Downloaded data/2020-06-metropolitan-street.csv
    Downloaded data/2020-07-metropolitan-street.csv
    Downloaded data/2020-08-metropolitan-street.csv
    Downloaded data/2020-09-metropolitan-street.csv
    Downloaded data/2020-10-metropolitan-street.csv
    Downloaded data/2020-11-metropolitan-street.csv
    Downloaded data/2020-12-metropolitan-street.csv


## Data Pre-Processing

It will be helpful to merge all 12 CSV files into a single dataframe. We can use `pd.concat()` to merge a list of dataframes.


```python
dataframe_list = []

for f in files:
    filepath = os.path.join(data_folder, f)
    df = pd.read_csv(filepath)
    dataframe_list.append(df)

merged_df = pd.concat(dataframe_list)
```

The resulting dataframe consists of over 1 million records of various crimes recorded in London in the year 2020.


```python
merged_df
```

## Create a Pie-Chart

Let's create a pie-chart showing the distribution of different types of crime. Pandas `groupby()` function allows us to calculate group statistics.


```python
type_counts = merged_df.groupby('Crime type').size()
type_counts
```




    Crime type
    Anti-social behaviour           415105
    Bicycle theft                    23517
    Burglary                         61044
    Criminal damage and arson        50923
    Drugs                            51629
    Other crime                      10066
    Other theft                      81924
    Possession of weapons             5763
    Public order                     53458
    Robbery                          27269
    Shoplifting                      34588
    Theft from the person            31084
    Vehicle crime                   108344
    Violence and sexual offences    227208
    dtype: int64



We now uses the `plot()` method to create the chart. This method is a wrapper around `matplotlib` and can accept supported arguments from it. 

Reference: [`pandas.DataFrame.plot`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.html)


```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(15,10)
type_counts.plot(kind='pie', ax=ax)
plt.show()
```


    
![](python-dataviz-output/02_creating_charts_files/02_creating_charts_16_0.png)
    


Let's customize the chart. First we use `set_title()` method to add a title to the chart and `set_ylabel()` to remove the empty y-axis label. Lastly, we use the `plt.tight_layout()` to remove the extra whitespace around the plot.


```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(15,10)

type_counts.plot(kind='pie', ax=ax)

ax.set_title('Crime Types', fontsize = 18)
ax.set_ylabel('')

plt.tight_layout()
plt.show()
```


    
![](python-dataviz-output/02_creating_charts_files/02_creating_charts_18_0.png)
    


Matplotlib plots offer unlimited possibilities to customize your charts. Let's see some of the options available to customize the pie-chart. 

* `wedgeprops`: Customize the look of each 'wedge' of the pie.
* `textprops`: Set the text properties of labels.
* `autopct` and `pctdistance`: Format and distance of the percentage label of each slice. 

Reference: [`matplotlib.pyplot.pie`](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.pie.html)


```python
wedgeprops={'linewidth': 1, 'edgecolor': 'white'}
textprops= {'fontsize': 10, 'fontstyle': 'italic'}
autopct= '%.1f%%'
pctdistance = 0.8

fig, ax = plt.subplots(1, 1)
fig.set_size_inches(15,10)

type_counts.plot(kind='pie', ax=ax, 
                 wedgeprops=wedgeprops,
                 textprops=textprops, 
                 autopct=autopct,
                 pctdistance=pctdistance )

ax.set_title('Crime Types', fontsize = 18)
ax.set_ylabel('')

plt.tight_layout()
plt.show()

```


    
![](python-dataviz-output/02_creating_charts_files/02_creating_charts_20_0.png)
    


## Create a Bar Chart

We can also chart the trend of crime over the year. For this, let's group the data by month.


```python
monthly_counts = merged_df.groupby('Month').size()
monthly_counts
```




    Month
    2020-01     90979
    2020-02     86984
    2020-03     87409
    2020-04    109951
    2020-05    114008
    2020-06    100198
    2020-07    103657
    2020-08    104782
    2020-09     99633
    2020-10     99471
    2020-11     96914
    2020-12     87936
    dtype: int64




```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(15,7)
monthly_counts.plot(kind='bar', ax=ax)
plt.show()
```


    
![](python-dataviz-output/02_creating_charts_files/02_creating_charts_23_0.png)
    


As we learnt earlier, we can add multiple plots on the same Axes. We can add a `line` chart along with the `bar` chart to show the trendline as well. Lastly we add the titles and axis labels to finish the chart.


```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(15,7)

monthly_counts.plot(kind='bar', ax=ax)
monthly_counts.plot(kind='line', ax=ax, color='red', marker='o')

ax.set_title('Total Crime by Month')
ax.set_ylabel('Total Incidents')

plt.show()
```


    
![](python-dataviz-output/02_creating_charts_files/02_creating_charts_25_0.png)
    


## Exercise

Plot the trend of Bicycle thefts as a line chart. The cell below filters the `merged_df` dataframe to select incidents of 'Bicycle theft'. Group the results by months and plot the results.


```python
bicycle_thefts = merged_df[merged_df['Crime type'] == 'Bicycle theft']
```
