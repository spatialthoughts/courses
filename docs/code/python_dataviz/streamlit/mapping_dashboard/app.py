import streamlit as st
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import leafmap.foliumap as leafmap

st.set_page_config(page_title='Dashboard', layout='wide')

st.title('Highway Dashboard')

st.sidebar.title('About')
st.sidebar.info('Explore the Highway Statistics')


data_url = 'https://storage.googleapis.com/spatialthoughts-public-data/python-dataviz/osm/'
gpkg_file = 'karnataka.gpkg'
csv_file = 'highway_lengths_by_district.csv'

@st.cache_data
def read_gdf(url, layer):
    gdf = gpd.read_file(url, layer=layer)
    return gdf

@st.cache_data
def read_csv(url):
    df = pd.read_csv(url)
    return df

gpkg_url = data_url + gpkg_file
csv_url = data_url + csv_file
districts_gdf = read_gdf(gpkg_url, 'karnataka_districts')
roads_gdf = read_gdf(gpkg_url, 'karnataka_highways')
lengths_df = read_csv(csv_url)

# Create the chart
districts = districts_gdf.DISTRICT.values
district = st.sidebar.selectbox('Select a District', districts)
overlay = st.sidebar.checkbox('Overlay roads')
district_lengths = lengths_df[lengths_df['DISTRICT'] == district]

fig, ax = plt.subplots(1, 1)
district_lengths.plot(kind='bar', ax=ax, color=['blue', 'red'],
    ylabel='Kilometers', xlabel='Category')
ax.get_xaxis().set_ticklabels([])
stats = st.sidebar.pyplot(fig)

## Create the map

m = leafmap.Map(
    layers_control=True,
    draw_control=False,
    measure_control=False,
    fullscreen_control=False,
)
m.add_basemap('CartoDB.DarkMatter')
m.add_gdf(
    gdf=districts_gdf,
    zoom_to_layer=False,
    layer_name='districts',
    info_mode='on_click',
    style={'color': '#7fcdbb', 'fillOpacity': 0.3, 'weight': 0.5},
    )

if overlay:
    m.add_gdf(
        gdf=roads_gdf,
        zoom_to_layer=False,
        layer_name='highways',
        info_mode=None,
        style={'color': '#225ea8', 'weight': 1.5},
    )
    
selected_gdf = districts_gdf[districts_gdf['DISTRICT'] == district]

m.add_gdf(
    gdf=selected_gdf,
    layer_name='selected',
    zoom_to_layer=True,
    info_mode=None,
    style={'color': 'yellow', 'fill': None, 'weight': 2}
 )


m_streamlit = m.to_streamlit(600, 600)
