## Overview

[Folium](https://python-visualization.github.io/folium/) is a Python library that allows you to create interactive maps based on the popular [Leaflet](https://leafletjs.com/) javascript library.

In this section, we will learn how to create an interactive map showing driving directions between two locations.

## Setup



```python
import os
import folium
```


```python
data_folder = 'data'
output_folder = 'output'

if not os.path.exists(data_folder):
    os.mkdir(data_folder)
if not os.path.exists(output_folder):
    os.mkdir(output_folder)
```

We will be using [OpenRouteService API](https://openrouteservice.org/) to calculate the directions. Please sign-up for a free account and create an API key. If you already have an account, the API key is obtained from the [OpenRouteService Dashboard](https://openrouteservice.org/dev/#/home). Enter your API key below.


```python
ORS_API_KEY = ''
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
m = folium.Map(location=[39.83, -98.58], zoom_start=4)
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
folium.Marker(san_francisco, popup='San Francisco',
              icon=folium.Icon(
                  color='green', icon='crosshairs', prefix='fa')
             ).add_to(m)
folium.Marker(new_york, popup='New York',
              icon=folium.Icon(color='red', icon='crosshairs', prefix='fa')
             ).add_to(m)
fig.add_child(m)

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
    data = response.json()
else:
    print('Request failed.')

```

Extract the coordinates for the driving directions.


```python
route= data['features'][0]['geometry']['coordinates']
```


```python
route[:5]
```

The coordinates returned by OpenRouteService API is in the order [X,Y] (i.e. [Longitude, Latitude]) whereas Folium requires the coordinates in [Y,X] (i.e. [Latitude, Longitude]) order. We can swap them before plotting.


```python
route_xy = []
for x, y in route:
    route_xy.append((y,x))
route_xy[:5]
```

An easier way to accomplish the same is by using a Python [List Comprehension](https://www.w3schools.com/python/python_lists_comprehension.asp).


```python
route_xy = [(y, x) for x, y in route]
route_xy[:5]
```

We extract the route summary returned by the API which contains the total driving distance in meters.


```python
summary = data['features'][0]['properties']['summary']
distance = round(summary['distance']/1000)
tooltip = 'Driving Distance: {}km'.format(distance)
```

We can use the [`folium.vector_layers.Polyline`](https://python-visualization.github.io/folium/modules.html#folium.vector_layers.PolyLine) class to add a line to the map. The class has a `smooth_factor` parameter which can be used to simplify the line displayed when zoomed-out. Setting a higher number results in better performance.


```python
folium.PolyLine(route_xy, tooltip=tooltip, smooth_factor=1).add_to(m)
m
```

> Folium also provides a [`GeoJson`](https://python-visualization.github.io/folium/latest/user_guide/geojson/geojson.html) method to load any data in the GeoJSON format directly. Instead of extracting the coordinates, and creating a Polyline, we can also directly use the GeoJSON response returned by the OpenRouteService API like this. This is the preferred method as it gives you additional features for styling and layer manipulation.

```
folium.GeoJson(data, tooltip=tooltip, smooth_factor=1)
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
3. Change the route line to *red* color with a line width of 1 pixels. Reference [`folium.vector_layers.Polyline`](https://python-visualization.github.io/folium/modules.html#folium.vector_layers.PolyLine) and [`leaflet.Path`](https://leafletjs.com/reference.html#path)


<img src='https://courses.spatialthoughts.com/images/python_dataviz/folium_route.png' width=600/>


Use the code block below as the starting point and replace the variables below with those of your chosen locations and insert your own API key.


```python
import folium
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
    data = response.json()
else:
    print('Request failed.')

route= data['features'][0]['geometry']['coordinates']
summary = data['features'][0]['properties']['summary']

route_xy = [(y, x) for x, y in route]
distance = round(summary['distance']/1000)
tooltip = 'Driving Distance: {}km'.format(distance)

from folium import Figure
fig = Figure(width=800, height=400)

m = folium.Map(location=map_center, zoom_start=4)
folium.Marker(origin, popup=origin_name,
              icon=folium.Icon(
                  color='green', icon='crosshairs', prefix='fa')
             ).add_to(m)
folium.Marker(destination, popup=destination_name,
              icon=folium.Icon(color='red', icon='crosshairs', prefix='fa')
             ).add_to(m)
folium.PolyLine(route_xy, tooltip=tooltip).add_to(m)
fig.add_child(m)
```

----
