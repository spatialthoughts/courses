import streamlit as st
import rioxarray as rxr 
import xarray as xr
import leafmap.foliumap as leafmap
import numpy as np 
import os

st.write('This is a simple Streamlit app to visualize raster data using Leafmap and Rioxarray.')

# Get the directory where app.py lives
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ds = rxr.open_rasterio(os.path.join(BASE_DIR, 'bangalore_lulc_cog.tif'), masked=True)


m = leafmap.Map()
m.add_raster(ds, colormap='plasma', layer_name='LULC', nodata=np.nan, vmin=10, vmax=110)

# Try some data processing to show how you can render data on the fly.
# Here we will create a binary raster where values equal to 50 are set to 1
# and the rest are set to 0.
processed = xr.where(ds == 50, 1, 0)
processed.rio.write_crs(ds.rio.crs, inplace=True)
m.add_raster(processed, colormap='Reds', layer_name='Built', nodata=0)

m.to_streamlit(height=600, zoom=12)