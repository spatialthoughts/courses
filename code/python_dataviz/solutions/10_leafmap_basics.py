m = leafmap.Map(width=800, height=500)

cog_url = os.path.join(data_url, 'bangalore_lulc.tif')
bounds = leafmap.cog_bounds(cog_url)

m.add_cog_layer(cog_url, layer_name='Land Use Land Cover')
m.zoom_to_bounds(bounds)

# Add a Legend
colors = ['#006400', '#ffbb22','#ffff4c','#f096ff','#fa0000',
          '#b4b4b4','#f0f0f0','#0064c8','#0096a0','#00cf75','#fae6a0']
labels = ["Trees","Shrubland","Grassland","Cropland","Built-up",
          "Barren / sparse vegetation","Snow and ice","Open water",
          "Herbaceous wetland","Mangroves","Moss and lichen"]
# Use m.add_legend() function to add a legend
m.add_legend(colors=colors, labels=labels)

m
