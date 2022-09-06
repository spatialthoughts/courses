import streamlit as st
import folium
import leafmap.foliumap as leafmap
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt


st.set_page_config(page_title="Dashboard", layout="wide")

st.title('National Highway Dashboard')

st.sidebar.title("About")
st.sidebar.info('Explore the Roads')

data_url = 'https://github.com/spatialthoughts/python-dataviz-web/raw/main/data/osm/'
gpkg_file = 'karnataka.gpkg'
csv_file = 'highway_lengths_by_district.csv'

@st.cache
def read_gdf(url, layer):
    gdf = gpd.read_file(url, layer=layer)
    return gdf

@st.cache
def read_csv(url):
    df = pd.read_csv(url)
    return df
    
   
gpkg_url = data_url + gpkg_file
csv_url = data_url + csv_file
districts_gdf = read_gdf(gpkg_url, 'karnataka_districts')
roads_gdf = read_gdf(gpkg_url, 'karnataka_highways')
lengths_df = read_csv(csv_url)


districts = districts_gdf.DISTRICT.values
district = st.sidebar.selectbox('Select a District', districts)

district_lengths = lengths_df[lengths_df['DISTRICT'] == district]

fig, ax = plt.subplots(1, 1)
district_lengths.plot(kind='bar', ax=ax, color=['blue', 'red', 'gray'], ylabel='Kilometers', xlabel='Category')
ax.get_xaxis().set_ticklabels([])
stats = st.sidebar.pyplot(fig)

m = leafmap.Map(
    layers_control=True,
    draw_control=False,
    measure_control=False,
    fullscreen_control=False,
)

m.add_gdf(
    gdf=districts_gdf,
    layer_name='districts',
    zoom_to_layer=True,
    info_mode='on_click',
    style={'color': 'black', 'fillOpacity': 0.3, 'weight': 0.5},
    )

selected_gdf = districts_gdf[districts_gdf['DISTRICT'] == district]

m.add_gdf(
    gdf=selected_gdf,
    layer_name='selected',
    zoom_to_layer=False,
    info_mode=None,
    style={'color': 'yellow', 'fill': None, 'weight': 2}
 )

m_streamlit = m.to_streamlit(500, 500)
