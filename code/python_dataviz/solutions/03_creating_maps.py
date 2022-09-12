# Exercise Solution
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(10,10)
tracts.plot(ax=ax, facecolor='none', edgecolor='black')
plt.show()

# Customize Legend
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(10,10)
gdf.plot(ax=ax, column='density', cmap='RdYlGn_r', scheme='User_Defined', 
         classification_kwds=dict(bins=[1,10,25,50,100, 250, 500, 1000, 5000]),
         legend=True)
ax.set_axis_off()
ax.set_title('California Population Density (2019)', size = 18)
legend = ax.get_legend()
legend.set_title('Legend')
legend._legend_box.align = 'left'
for t in ax.get_legend().get_texts():
  t.set_text(t.get_text().replace(' ', ''))
plt.show()
