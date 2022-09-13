fig, axes = plt.subplots(2, 2, linewidth=5, edgecolor='black', constrained_layout=True)
fig.set_size_inches(10,10)
fig.suptitle('SRTM 30m Elevation Tiles', fontsize=20)
index = 0
for row in axes:
  for colax in row:
      im = datasets[index].plot.imshow(ax=colax, cmap='Greys_r', add_colorbar=False, add_labels=True)
      filename = srtm_tiles[index]
      index +=1
      colax.set_aspect('equal')
      colax.set_title(filename)
      colax.set_xlabel('longitude')
      colax.set_ylabel('latitude')

plt.savefig('output.png', dpi=100)
plt.show()
