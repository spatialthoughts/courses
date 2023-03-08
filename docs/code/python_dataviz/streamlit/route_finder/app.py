import folium
import streamlit as st
from streamlit_folium import st_folium
from streamlit_folium import folium_static
import requests

st.set_page_config(page_title='Route Finder')
st.title('Route Finder')

st.markdown('This app uses the [OpenRouteService API](https://openrouteservice.org/) to geocode and get directions between the specified origin and destination. [[view source code](https://github.com/spatialthoughts/streamlit/tree/main/route_finder)]')
st.text('Enter any city name or address below.')
origin = st.text_input('Origin (Example: San Francisco, CA)')
destination = st.text_input('Destination (Example: San Jose, CA)')
mode = st.selectbox('Travel Mode', ['Car', 'Walk', 'Bike'])
button = st.button('Get Directions')

# Define a placeholder to display the distance and download button once computed.    
placeholder = st.empty()


ORS_API_KEY = st.secrets['ORS_API_KEY']

@st.cache_data
def geocode(query):
    parameters = {
        'api_key': ORS_API_KEY,
        'text' : query
    }

    response = requests.get(
         'https://api.openrouteservice.org/geocode/search',
         params=parameters)
    if response.status_code == 200:
     data = response.json()
    else:
     st.error('Request failed.')
    x, y = data['features'][0]['geometry']['coordinates']
    return (y, x)

def get_directions(origin_name, destination_name):    
    origin_coords = geocode(origin_name)
    destination_coords = geocode(destination_name)
    parameters = {
        'api_key': ORS_API_KEY,
        'start' : '{},{}'.format(origin_coords[1], origin_coords[0]),
        'end' : '{},{}'.format(destination_coords[1], destination_coords[0])
    }
    mode_dict = {
        'Car': 'driving-car',
        'Walk': 'foot-walking',
        'Bike': 'cycling-regular'
    }
    service_url = '{}/{}'.format(
        'https://api.openrouteservice.org/v2/directions',
        mode_dict[mode])
    response = requests.get(service_url, params=parameters)

    if response.status_code == 200:
        data = response.json()
    else:
        st.error('Request failed.')
        
    route= data['features'][0]['geometry']['coordinates']
    route_xy = [(y,x) for x, y in route]
    summary = data['features'][0]['properties']['summary']
    distance = round(summary['distance']/1000)
    tooltip = 'Distance by {}: {}km'.format(mode, distance)
    return route_xy, tooltip
    


m = folium.Map(location=[39.949610, -75.150282], zoom_start=5)
if origin:
    origin_coords = geocode(origin)
    folium.Marker(
        origin_coords,
        popup=origin,
        icon=folium.Icon(color='green', icon='crosshairs', prefix='fa')
        ).add_to(m)
    origin_bb = [
        (origin_coords[0] - 0.05, origin_coords[1] - 0.05),
        (origin_coords[0] + 0.05, origin_coords[1] + 0.05)]
    m.fit_bounds(origin_bb)
    
if destination:
    destination_coords = geocode(destination)
    folium.Marker(
        destination_coords,
        popup=destination,
        icon=folium.Icon(color='red', icon='crosshairs', prefix='fa')
        ).add_to(m)
if origin and destination:
    m.fit_bounds([origin_coords, destination_coords])

if button:
    route_xy, tooltip = get_directions(origin, destination)
    folium.PolyLine(route_xy, tooltip=tooltip).add_to(m)
    placeholder.text(tooltip)
    
    m.save('directions.html')
    with open('directions.html') as file:
        placeholder.download_button('Download Directions', data=file, file_name='directions.html')
    
folium_static(m, width=800)
