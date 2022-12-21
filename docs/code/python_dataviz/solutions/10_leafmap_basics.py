gcs_bucket = 'https://storage.googleapis.com/spatialthoughts-public-data/'
cog_url = os.path.join(gcs_bucket, 'viirs_ntl_2021_india.tif')

m = leafmap.Map(width=800, height=500, google_map='SATELLITE')
m.add_cog_layer(cog_url, name='VIIRS NTL 2021', colormap_name='viridis', rescale='0,60', nodata='nan')
m
