import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title('A Simple Dashboard')
st.write('This dashboard displays a chart for the selected region.')

@st.cache_data
def load_data():
    data_url = 'https://storage.googleapis.com/spatialthoughts-public-data/python-dataviz/osm/'
    csv_file = 'highway_lengths_by_district.csv'

    url = data_url + csv_file
    df = pd.read_csv(url)
    
    return df

df = load_data()

districts = df.DISTRICT.values
district = st.selectbox('Select a district', districts)
filtered = df[df['DISTRICT'] == district] 

col1, col2 = st.columns(2)

nh_color = col1.color_picker('Pick NH Color', '#0000FF', key='nh')
sh_color = col2.color_picker('Pick SH Color', '#FF0000', key='sh')

    
fig, ax = plt.subplots(1, 1)

filtered.plot(kind='bar', ax=ax, color=[nh_color, sh_color],
    ylabel='Kilometers', xlabel='Category')
ax.set_title('Length of Highways')
ax.set_ylim(0, 2500)
ax.set_xticklabels([])
stats = st.pyplot(fig)
