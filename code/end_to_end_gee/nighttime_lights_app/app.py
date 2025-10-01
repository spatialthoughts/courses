import streamlit as st
import ee
import geemap.foliumap as geemap
import json
import os

# Page configuration
st.set_page_config(
    page_title='Nighttime Lights Explorer',
    page_icon='🌙',
    layout='wide'
)

# Title and description
st.title('Nighttime Lights Explorer')

# Initialize Earth Engine
json_data = st.secrets['json_data']
service_account = st.secrets['service_account']
credentials = ee.ServiceAccountCredentials(service_account, key_data=json_data)
ee.Initialize(credentials)


# Year dropdown
year = st.sidebar.selectbox(
    'Select Year',
    options=list(range(2014, 2024)),
    index=0,  # Default to 2022 (index 8 in the range)
    help='Select the year for nighttime lights data'
)

# Month dropdown
month = st.sidebar.selectbox(
    'Select Month',
    options=list(range(1, 13)),
    format_func=lambda x: {
        1: 'January', 2: 'February', 3: 'March', 4: 'April',
        5: 'May', 6: 'June', 7: 'July', 8: 'August', 
        9: 'September', 10: 'October', 11: 'November', 12: 'December'
    }[x],
    index=0,  # Default to January
    help='Select the month for nighttime lights data'
)

# Load nighttime lights data
@st.cache_data
def load_nighttime_lights(year, month):
    col = ee.ImageCollection('NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG');
    startDate = ee.Date.fromYMD(year, month, 1)
    endDate = startDate.advance(1, 'month')
    image = col.filterDate(startDate, endDate).select('avg_rad').first()
    return image

with st.spinner('Loading map data...'):
        # Load the data
        image = load_nighttime_lights(year, month)
        
        # Create the map
        Map = geemap.Map(
            center=[12.94, 77.57],
            zoom=9,
            height=600,
            width=800
        )
        
        # Visualization parameters
        vis_params = {
            'min': 0,
            'max': 60,
        }
        
        # Add nighttime lights layer
        Map.addLayer(
            image,
            vis_params,
            f'Nighttime Lights {year}'
        )
        
        # Add layer control
        Map.add_layer_control()
        
        # Display the map
        Map.to_streamlit(height=600, width=800)