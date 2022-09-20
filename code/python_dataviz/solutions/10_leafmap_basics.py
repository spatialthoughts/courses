m = leafmap.Map(width=800, height=500, google_map='SATELLITE')
data_url = 'https://storage.googleapis.com/spatialthoughts-public-data/viirs_ntl_2021_india.tif'
m.add_cog_layer(data_url, name='VIIRS NTL 2021', colormap_name='viridis')
m
