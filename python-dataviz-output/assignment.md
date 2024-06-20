## Overview

Your assignment is to create a colorized river basin map for your country using the [HydroRIVERS](https://www.hydrosheds.org/products/hydrorivers) data.

This notebook contains code to download and pre-process the data. Your task is to plot the rivers using Matplotlib and achieve a unique style shown below.

<img src='https://courses.spatialthoughts.com/images/python_dataviz/assignment.png' width=800/>

## Setup and Data Download


```python
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import requests
import zipfile
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
      with requests.get(url, stream=True, allow_redirects=True) as r:
          with open(filename, 'wb') as f:
              for chunk in r.iter_content(chunk_size=8192):
                  f.write(chunk)
      print('Downloaded', filename)


data_url = 'https://github.com/spatialthoughts/python-dataviz-web/releases/download/'

# This is a subset of the main HydroRivers dataset of all
# rivers having `UPLAND_SKM` value  greater than 100 sq. km.
hydrorivers_file = 'hydrorivers_100.gpkg'
hydrorivers_url = data_url + 'hydrosheds/'

countries_file = 'ne_10m_admin_0_countries_ind.zip'
countries_url = data_url + 'naturalearth/'


download(hydrorivers_url + hydrorivers_file)
download(countries_url + countries_file)

```

## Data Pre-Processing

Read the countries shapefile.


```python
countries_filepath = os.path.join(data_folder, countries_file)
```

For the assignment, you need to pick the country for which you want to create the map. We can print a list of values from the `SOVEREIGNT` column of `country_gdf` GeoDataFrame using `country_gdf.SOVEREIGNT.values` to know the names of all countries.


```python
country_gdf = gpd.read_file(countries_filepath)
print(sorted(country_gdf.SOVEREIGNT.unique()))
```

Select a country name. Replace the value below with your chosen country.


```python
country = 'India'
```

Apply filters to select the country feature. We use an additional filter `TYPE != 'Dependency'` to exclude overseas territories. You may have to adjust the filter to get the correct country polygon.


```python
selected_country = country_gdf[(country_gdf['SOVEREIGNT'] == country) & (country_gdf['TYPE'] != 'Dependency')]
selected_country
```

We read the river network data from HydroRivers. We specify the `mask` parameter which clips the layer to the country boundary while reading the data.

*This step can take a few minutes depending on the size of the country.*


```python
hydrorivers_filepath = os.path.join(data_folder, hydrorivers_file)
river_gdf = gpd.read_file(hydrorivers_filepath, mask=selected_country)
river_gdf
```

Visualize the river network.


```python
fig, ax = plt.subplots(figsize=(10, 10))
title = f'Rivers of {country}'
river_gdf.plot(ax=ax)
ax.set_title(title)
ax.set_axis_off()
plt.show()
```

We want to style the rivers so that the width of the line is proportional to the value in the `UPLAND_SKM` attribute. We add a new column `width` to the GeoDataFrame by scaling the input values to a range of target widths.

*Tip: These values will play an important role in your final visualization. Adjust these to suit the range of values for your country.*


```python
original_min = 300
original_max = 10000
target_min = 0.2
target_max = 0.9
scaled = (river_gdf['UPLAND_SKM'] - original_min) / (original_max - original_min)
river_gdf['width'] = scaled.clip(0, 1) * (target_max - target_min) + target_min
river_gdf_final = river_gdf.sort_values(['UPLAND_SKM', 'width'])[
    ['MAIN_RIV', 'UPLAND_SKM', 'width', 'geometry']]
river_gdf_final
```

Your task is to render the river network by applying the following changes. Refer to the [`geopandas.GeoDataFrame.plot()`](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.plot.html) documentation for parameter values and options.

*   Assign a color to each river segment based on the value of `MAIN_RIV` column. *Hint: set `categorical=True`*.
*  Assign width to each item based on the value in the `width` column.
* Set the map background to black.
* Set the title to white and change the font to be larger.
