# Creating Interactive Maps with Folium

[Folium](https://python-visualization.github.io/folium/) is a Python library that allows you to create interactive maps based on the popular [Leaflet](https://leafletjs.com/) javascript library.

In this section, we will learn how to create an interactive map showing driving directions between two locations.


```python
import os
import folium
```


```python
san_francisco = (37.7749, -122.4194)
new_york = (40.661, -73.944)
```


```python
m = folium.Map()
m
```


```python
m = folium.Map(location=[39.83, -98.58], zoom_start=4)
m
```


```python
folium.Marker(san_francisco, popup='San Francisco').add_to(m)
folium.Marker(new_york, popup='New York').add_to(m)

m
```

* [folium.map.Marker](https://python-visualization.github.io/folium/modules.html#folium.map.Marker)
* [folium.map.Icon](https://python-visualization.github.io/folium/modules.html#folium.map.Icon)
* [fontawesome icons](https://fontawesome.com/search?m=free&c=maps)
* [bootstrap icons](https://getbootstrap.com/docs/3.3/components/)


```python
m = folium.Map(location=[39.83, -98.58], zoom_start=4)
folium.Marker(san_francisco, popup='San Francisco',
              icon=folium.Icon(
                  color='green', icon='crosshairs', prefix='fa')
             ).add_to(m)
folium.Marker(new_york, popup='New York', 
              icon=folium.Icon(color='red', icon='crosshairs', prefix='fa')
             ).add_to(m)
m
```

Enter your API key in the followig variable. The API key is obtained from the [OpenRouteService Dashboard](https://openrouteservice.org/dev/#/home)


```python
ORS_API_KEY = ''
```

While running this notebook in production, we load the `ORS_API_KEY` from a `.env` file in the local environment. 
> Users of this notebook can skip running this cell.


```python
if not ORS_API_KEY:
    from dotenv import dotenv_values
    config = dotenv_values('.env')
    ORS_API_KEY = config['ORS_API_KEY']
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


```python
summary = data['features'][0]['properties']['summary']
distance = round(summary['distance']/1000)
tooltip = 'Driving Distance: {}km'.format(distance)
```


```python
m = folium.Map(location=[39.83, -98.58], zoom_start=4)
folium.Marker(san_francisco, popup='San Francisco',
              icon=folium.Icon(
                  color='green', icon='crosshairs', prefix='fa')
             ).add_to(m)
folium.Marker(new_york, popup='New York', 
              icon=folium.Icon(color='red', icon='crosshairs', prefix='fa')
             ).add_to(m)
folium.PolyLine(route_xy, tooltip=tooltip).add_to(m)
m
```


```python
output_folder = 'output'

if not os.path.exists(output_folder):
    os.mkdir(output_folder)
output_path = os.path.join(output_folder, 'directions.html')
m.save(output_path)
```

## Exercise

Below is the complete code to create an interactive map with the driving directions between two cities. Replace the origin and destination with your chosen cities and create an interactive map.


```python
import folium
import requests

origin = (37.7749, -122.4194)
origin_name = 'San Francisco'
destination = (40.661, -73.944)
destination_name = 'New York'

ORS_API_KEY = '5b3ce3597851110001cf6248ed43ece522584866b5deb4ac3732a19f'

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
m = folium.Map(location=[39.83, -98.58], zoom_start=4)
folium.Marker(origin, popup=origin_name,
              icon=folium.Icon(
                  color='green', icon='crosshairs', prefix='fa')
             ).add_to(m)
folium.Marker(destination, popup=destination_name, 
              icon=folium.Icon(color='red', icon='crosshairs', prefix='fa')
             ).add_to(m)
folium.PolyLine(route_xy, tooltip=tooltip).add_to(m)
m
```

----
