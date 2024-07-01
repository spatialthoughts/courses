import folium
import requests
import streamlit as st
from streamlit_folium import folium_static

st.title('A Simple Geocoder')
st.markdown('This app uses the [OpenRouteService API](https://openrouteservice.org/) '
    'to geocode the input address and siplay the results on a map.')

address = st.text_input('Enter an address.')

ORS_API_KEY = '<your api key>'

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
        if data['features']:
            x, y = data['features'][0]['geometry']['coordinates']
            return (y, x)
    
if address:
    results = geocode(address)
    if results:
        st.write('Geocoded Coordinates: {}, {}'.format(results[0], results[1]))
        
        m = folium.Map(location=results, zoom_start=8)
        folium.Marker(
                results,
                popup=address,
                icon=folium.Icon(color='green', icon='crosshairs', prefix='fa')
                ).add_to(m)
        folium_static(m, width=800)
        
    else:
        st.error('Request failed. No results.')

