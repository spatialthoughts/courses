## Overview

[Folium](https://python-visualization.github.io/folium/) is a Python library that allows you to create interactive maps based on the popular [Leaflet](https://leafletjs.com/) javascript library.

In this section, we will learn how to create an interactive map showing driving directions between two locations.

## Setup



```python
import os
import folium
import json
```


```python
data_folder = 'data'
output_folder = 'output'

if not os.path.exists(data_folder):
    os.mkdir(data_folder)
if not os.path.exists(output_folder):
    os.mkdir(output_folder)
```

## Folium Basics

We will learn the basics of folium by creating an interactive map showing the driving directions between two chosen locations. Let's start by defining the coordinates of two cities.


```python
san_francisco = (37.7749, -122.4194)
new_york = (40.661, -73.944)
```

To create a map, we initialize the `folium.Map()` class which creates a map object with the default basemap. To display the map a Jupyter notebook, we can simply enter the name of the map object.


```python
m = folium.Map()
m
```

The default map spans the full width of the Jupyter notebook - making it difficult to navigate. The `Map()` constructor supports `width` and `height` parameters that control the size of the leaflet map, but you still end up with a lot of extra empty space below the map. The preferred way to get a map of exact size is to create a *Figure* first and add the map object to it.


```python
from folium import Figure
fig = Figure(width=800, height=400)
m = folium.Map(location=[39.83, -98.58], zoom_start=4, width=800, height=400)
fig.add_child(m)
```

The map object `m` can be manipulated by adding different elements to it. Contrary to how Matplotlib objects work, the map object does not get emptied when displayed. So you are able to visualize and incrementally add elements to it. Let's add some markers to the map using [`folium.map.Marker`](https://python-visualization.github.io/folium/modules.html#folium.map.Marker) class.


```python
folium.Marker(san_francisco, popup='San Francisco').add_to(m)
folium.Marker(new_york, popup='New York').add_to(m)

m
```

The markers can be customized to have a different color or icons. You can check the [`folium.map.Icon`](https://python-visualization.github.io/folium/modules.html#folium.map.Icon) class for options for creating icons. This class supports a vast range of icons from the [fontawesome icons](https://fontawesome.com/search?m=free&c=maps) and [bootstrap icons](https://getbootstrap.com/docs/3.3/components/) libraries. You can choose the name of the icon from there to use it in your Folium map. The `prefix` parameter can be *fa* for FontAwesome icons or *glyphicon* for Bootstrap3.


```python
from folium import Figure
fig = Figure(width=800, height=400)
m = folium.Map(location=[39.83, -98.58], zoom_start=4)

folium.Marker(
    san_francisco,
    popup='San Francisco',
    icon=folium.Icon(
        color='green', icon='crosshairs', prefix='fa')
    ).add_to(m)

folium.Marker(
    new_york,
    popup='New York',
    icon=folium.Icon(
        color='red', icon='crosshairs', prefix='fa')
    ).add_to(m)

fig.add_child(m)

```

We will be using [OpenRouteService API](https://openrouteservice.org/) to calculate the directions. Visit [HeiGIT Sign Up](https://account.heigit.org/signup) page and create an account. Once your account is activated, visit your [Dashboard](https://account.heigit.org/manage/key). Copy the long string for **Basic Key** key and enter it below.


```python
ORS_API_KEY = ''
```


```python
import requests

san_francisco = (37.7749, -122.4194)
new_york = (40.661, -73.944)

parameters = {
    'api_key': ORS_API_KEY,
    'start' : '{},{}'.format(san_francisco[1], san_francisco[0]),
    'end' : '{},{}'.format(new_york[1], new_york[0])
}

response = requests.get(
    'https://api.openrouteservice.org/v2/directions/driving-car', params=parameters)

if response.status_code == 200:
    print('Request successful.')
    data = response.text
else:
    print('Request failed.')

```

The API response is formatted as a GeoJSON string.


```python
data
```

We can parse the GeoJSON as a dictionary and extract the route summary returned by the API which contains the total driving distance in meters.


```python
parsed_data = json.loads(data)
summary = parsed_data['features'][0]['properties']['summary']
distance = round(summary['distance']/1000)
tooltip = 'Driving Distance: {} km'.format(distance)
tooltip
```

We can use the [`folium.features.GeoJson`](https://python-visualization.github.io/folium/latest/user_guide/geojson/geojson.html) class to load any data in the GeoJSON format directly. We can specify a `smooth_factor` parameter which can be used to simplify the line displayed when zoomed-out. Setting a higher number results in better performance.


```python
folium.GeoJson(
    data,
    tooltip=tooltip,
    smooth_factor=1
    ).add_to(m)
m
```

Folium maps can be saved to a HTML file by calling `save()` on the map object.


```python
output_folder = 'output'
if not os.path.exists(output_folder):
    os.mkdir(output_folder)
output_path = os.path.join(output_folder, 'directions.html')
m.save(output_path)
```

## Exercise

1. Create an interactive map of driving directions between two of your chosen cities.
2. Cutomize the marker icons to a *car* icon. Reference [`folium.map.Icon`](https://python-visualization.github.io/folium/modules.html#folium.map.Icon).
3. Change the route line to *red* color with a line width of 1 pixels. Reference [`folium.features.GeoJSON` Styling](https://python-visualization.github.io/folium/latest/user_guide/geojson/geojson.html#Styling)


<img src='https://courses.spatialthoughts.com/images/python_dataviz/folium_route.png' width=600/>


Use the code block below as the starting point and replace the variables below with those of your chosen locations and insert your own API key.


```python
import folium
from folium import Figure
import json
import requests

###############################
###  Replace Variables Below
###############################
origin = (37.7749, -122.4194)
origin_name = 'San Francisco'
destination = (40.661, -73.944)
destination_name = 'New York'
map_center = (39.83, -98.58)
ORS_API_KEY = ''
###############################
parameters = {
    'api_key': ORS_API_KEY,
    'start' : '{},{}'.format(origin[1], origin[0]),
    'end' : '{},{}'.format(destination[1], destination[0])
}

response = requests.get(
    'https://api.openrouteservice.org/v2/directions/driving-car', params=parameters)

if response.status_code == 200:
    print('Request successful.')
    data = response.text
else:
    print('Request failed.')

parsed_data = json.loads(data)
summary = parsed_data['features'][0]['properties']['summary']
distance = round(summary['distance']/1000)
tooltip = 'Driving Distance: {} km'.format(distance)

fig = Figure(width=800, height=400)

m = folium.Map(location=map_center, zoom_start=4)

folium.Marker(
    origin, 
    popup=origin_name,
    icon=folium.Icon(
        color='green', icon='car', prefix='fa')
    ).add_to(m)

folium.Marker(
    destination, 
    popup=destination_name,
    icon=folium.Icon(
        color='red', icon='car', prefix='fa')
    ).add_to(m)

folium.GeoJson(
    data,
    tooltip=tooltip,
    smooth_factor=1,
   ).add_to(m)


fig.add_child(m)
```

----
