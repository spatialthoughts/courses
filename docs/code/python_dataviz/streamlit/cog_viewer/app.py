import streamlit as st
import leafmap.foliumap as leafmap
import os
from google.oauth2 import service_account
from google.cloud import storage

@st.cache_resource
def get_gcp_credentials():
    credentials = service_account.Credentials.from_service_account_info(
                st.secrets['gcp_service_account']
                )
    return credentials

st.set_page_config(page_title='GCS COG Viewer', layout='wide')

st.title('Cloud Optimized GeoTIFF Viewer')
st.markdown('This is a demo app showing how to lead a COG file stored in a private Google Cloud Storage (GCS) bucket using a signed URL.')

bucket_name = 'spatialthoughts-private-data'
blob_path = 'merged.tif'
credentials = get_gcp_credentials()

st.write(f"**Bucket:** {bucket_name}")
st.write(f"**Path:** {blob_path}")

with st.spinner('Reading Private COG from GCS...'):
    storage_client = storage.Client(credentials=credentials)

    # Get the blob
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    
    # Create a signed URL for authenticated access
    # This URL will be valid for 1 hour
    signed_url = blob.generate_signed_url(
        version='v4',
        expiration=3600,  # 1 hour
        method='GET',
        credentials=credentials
    )    
    # Add the COG layer using the signed URL
    m = leafmap.Map()
    bounds = leafmap.cog_bounds(signed_url)

    m.add_cog_layer(
        signed_url, 
        name='Private COG Layer', 
        colormap_name='viridis',
        titiler_endpoint='https://giswqs-titiler-endpoint.hf.space'
    )
    m.zoom_to_bounds(bounds)


    # Add layer control
    m.add_layer_control()
    
    # Display the map
    m.to_streamlit(800, 600)