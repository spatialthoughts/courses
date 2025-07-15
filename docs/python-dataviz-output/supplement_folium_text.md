### Displaying Text on Folium Maps

Folium supports [DivIcon](https://python-visualization.github.io/folium/latest/reference.html#folium.features.DivIcon) markers for creating text-markers. Using this, we can render text on a folium map easily. The example below an example of rendering markers with airport codes.

<img src='https://courses.spatialthoughts.com/images/python_dataviz/folium_text.png' width=600/>


```python
import os
import folium
from folium import Figure
from folium.features import DivIcon
import json
```


```python
sfo = (37.616, -122.386)
jfk = (40.645, -73.782)
```


```python
fig = Figure(width=800, height=400)
m = folium.Map(location=[39.83, -98.58], zoom_start=4)

folium.Marker(
    sfo,
    popup='San Francisco International Airport',
    icon=DivIcon(
        icon_size=(150,36),
        icon_anchor=(0,0),
        html='<div style="font-size: 24pt">SFO</div>',
    )).add_to(m)

folium.Marker(
    jfk,
    popup='John F. Kennedy International Airport',
    icon=DivIcon(
        icon_size=(150,36),
        icon_anchor=(0,0),
        html='<div style="font-size: 24pt">JFK</div>',
    )).add_to(m)


fig.add_child(m)

```

----
