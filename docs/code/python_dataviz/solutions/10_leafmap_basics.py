m = leafmap.Map(width=800, height=500, google_map='SATELLITE')

bounds = leafmap.cog_bounds(ntl2015_url)
m.zoom_to_bounds(bounds)

m.add_cog_layer(ntl2015_url, name='ntl2015')
m.add_cog_layer(ntl2022_url, name='ntl2022')

m
