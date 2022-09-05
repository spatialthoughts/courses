fig = Figure(width=800, height=400)

m = folium.Map(tiles='Stamen Terrain')
m.fit_bounds([[bounds[1],bounds[0]], [bounds[3],bounds[2]]])

districts_gdf.explore(
    m=m,
    color='black', 
    style_kwds={'fillOpacity': 0.3, 'weight':0.5},
    name='districts',
    tooltip=False)

roads_gdf.explore(
    m=m,
    column='category', 
    categories=['NH', 'SH'], 
    cmap=['#1f78b4', '#e31a1c'],
    categorical=True,
    name='highways'
)

state_gdf.explore(
    m=m,
    color='blue',
    style_kwds={'fill': None, 'weight': 2},
    name='state'
)

fig.add_child(m)
folium.LayerControl().add_to(m)
m
