### Visualizing Large Vector Datasets with Lonboard

[Lonboard](https://github.com/developmentseed/lonboard) is a deck-gl based Python library that allows you to interactively visualize large vector datasets. You can use Lonboard in Leafmap via the [deckgl module](https://leafmap.org/deckgl/).

Lonboard uses a different terminology for different types of vector layers.

* [ScatterplotLayer](https://developmentseed.org/lonboard/latest/api/layers/scatterplot-layer/): Reders points as circles.
* [PathLayer](https://developmentseed.org/lonboard/latest/api/layers/path-layer/): Renders polylines.
* [SolidPolygonLayer](https://developmentseed.org/lonboard/latest/api/layers/solid-polygon-layer/): Renders filled and/or extruded polygons.

When visualizing vector data via lonboard, please refer to the documentation for appropriate class for the parameter values.

We will visualize and style a very large layer of rivers using Leafmap and Lonboard.

<img src='https://courses.spatialthoughts.com/images/python_dataviz/lonboard_rivers.png' width=800/>

#### Setup and Data Download


```python
%%capture
if 'google.colab' in str(get_ipython()):
  !pip install leafmap lonboard palettable
```


```python
import os
import leafmap.deckgl as leafmap
import geopandas as gpd
import pandas as pd
import requests
import palettable
import lonboard

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
```


```python
countries_file = 'ne_10m_admin_0_countries_ind.zip'

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

#### Data Pre-Processing

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
country = 'United States of America'
```

Apply filters to select the country feature. We use an additional filter `TYPE != 'Dependency'` to exclude overseas territories. You may have to adjust the filter to get the correct country polygon.


```python
selected_country = country_gdf[
    (country_gdf['SOVEREIGNT'] == country) &
    (country_gdf['TYPE'] != 'Dependency')
]
selected_country
```

We read the river network data from HydroRivers. We specify the `mask` parameter which clips the layer to the country boundary while reading the data.

*This step can take a few minutes depending on the size of the country.*


```python
hydrorivers_filepath = os.path.join(data_folder, hydrorivers_file)
river_gdf = gpd.read_file(hydrorivers_filepath, mask=selected_country)
river_gdf
```

#### Visualize GeoDataFrame using Lonboard

Lonboard renders line layers using the [`PathLayer`](https://developmentseed.org/lonboard/latest/api/layers/path-layer/) object. We supply the lonboard parameters as keyword arguents to leafmap.


```python
m = leafmap.Map(height=600)
m.add_gdf(river_gdf,
          zoom_to_layer=True,
          pickable=True,
          get_width=2,
          get_color='blue',
          width_units='pixels'
)
m
```

We want to style the rivers so that the width of the line is proportional to the value in the `UPLAND_SKM` attribute. We add a new column `width` to the GeoDataFrame by scaling the input values to a range of target widths.


```python
original_min = 300
original_max = 10000
target_min = 0.1
target_max = 1
scaled = (river_gdf['UPLAND_SKM'] - original_min) / (original_max - original_min)
river_gdf['width'] = scaled.clip(0, 1) * (target_max - target_min) + target_min
river_gdf_final = river_gdf.sort_values(['UPLAND_SKM', 'width'])[
    ['MAIN_RIV', 'UPLAND_SKM', 'width', 'geometry']]
river_gdf_final
```

We want to assign a color based on the `MAIN_RIV` attribute. We will split the rivers into 10 equal bins.


```python
river_gdf_final['color'] = pd.qcut(
    river_gdf_final.MAIN_RIV, q=10,
    labels=False, duplicates='drop')
river_gdf_final
```

We create a discreate colormap by assigning a color to each bin.


```python
cmap = palettable.colorbrewer.diverging.Spectral_10

colormap = {}
for i, color in enumerate(cmap.colors):
    colormap[i] = color
colormap
```


```python
basemap = lonboard.basemap.CartoBasemap.DarkMatterNoLabels
cmap = palettable.colorbrewer.diverging.Spectral_10
widths = river_gdf_final['width']
colors = lonboard.colormap.apply_categorical_cmap(
    river_gdf_final['color'], colormap)

m = leafmap.Map(height=700, basemap_style=basemap)
m.add_gdf(river_gdf_final,
          zoom_to_layer=True,
          pickable=True,
          get_width=widths,
          get_color=colors,
          width_units='pixels'
)
m
```
