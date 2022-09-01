fig, ax = plt.subplots(1, 1)
fig.set_size_inches(15,7)

path_reprojected.plot(ax=ax, facecolor='#cccccc', edgecolor='#969696', alpha=0.5)
umbra_reprojected.plot(ax=ax, facecolor='#636363', edgecolor='none')

ax.set_ylim([1e6, 7e6])

cx.add_basemap(ax, crs=path_reprojected.crs, source=cx.providers.Stamen.Toner)

ax.set_axis_off()
ax.set_title('2017 Total Solar Eclipse Path', size = 18)
output_path = os.path.join(output_folder, 'eclipse_path.png')
plt.savefig(output_path, dpi=300)

plt.show()
