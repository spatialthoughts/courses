# import folium
import streamlit as st
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium

# Initialize session state
if "center" not in st.session_state:
    st.session_state["center"] = [37.7749, -122.4194]  # Default to San Francisco
if "zoom" not in st.session_state:
    st.session_state["zoom"] = 13
    
st.title('Bounding Box Tool')
st.markdown('This app allows you to get coordinates and bounding box for any '
  'place in the world - powered by OpenStreetMap.')

address = st.text_input('Enter an address.')

col1, col2 = st.columns([0.3, 0.7])
col1.text('Center Coordinates')
col1.caption('Format is X,Y (Longitude/Latitude)')
coordinate_text = col2.text('')
col3, col4 = st.columns([0.3, 0.7])
col3.text('Bounding Box')
col3.caption('Format is [Xmin,Ymin,XMax,YMax]')
boundingbox_text = col4.text('')

# Function to update the center
def update_map(lat, lon, zoom):
    st.session_state["center"] = [lat, lon]
    st.session_state['zoom'] = zoom
    

@st.cache_data
def geocode(query):
    geolocator = Nominatim(user_agent='streamlit-boundingbox')
    location = geolocator.geocode(address)
    return location
    
if address:
    location = geocode(address)
    if location:
        geocode_lat = location.latitude
        geocode_lng = location.longitude
        zoom = 8
        update_map(geocode_lat, geocode_lng, zoom)
    else:
        st.error('Request failed. No results.')

# Create a folium map
m = folium.Map(location=st.session_state["center"], zoom_start=st.session_state["zoom"])

# Display the map
st_data = st_folium(
    m,
    center=st.session_state["center"],
    zoom=st.session_state["zoom"],
    key="map",
    height=400,
    width=700,
)
        
center = st_data['center']
lat = center['lat']
lng = center['lng']
bounds = st_data['bounds']
lowerleft = bounds['_southWest']
upperright = bounds['_northEast']
ymin = lowerleft['lat']
xmin = lowerleft['lng']
ymax = upperright['lat']
xmax = upperright['lng']

coordinate_text.text(f'{lng:.4f}, {lat:.4f}')
boundingbox_text.text(f'[{xmin:.4f}, {ymin:.4f}, {xmax:.4f}, {ymax:.4f}]')


