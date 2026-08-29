### Exercise

Select only the pixels of *Tree Cover* (class value `10`) from the ESA WorldCover dataset to create a map of tree cover in your region.

Hint: Use the [`where()`](https://docs.xarray.dev/en/stable/generated/xarray.DataArray.where.html) function.


```python
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors

# Select only Tree Cover pixels (class value 10)
tree_cover = xr.where(map_data_clipped == 10, 1, 0)

# Plot the result
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(12, 10)

# Create a preview at coarser resolution for faster rendering
tree_cover_preview = tree_cover.rio.reproject(
    tree_cover.rio.crs, resolution=100
)

tree_cmap = mcolors.ListedColormap(['#e0e0e0', '#2e7d32'])
tree_cover_preview.plot(
    ax=ax, cmap=tree_cmap, vmin=0, vmax=1, add_colorbar=False
)

ax.legend(
    handles=[mpatches.Patch(color='#2e7d32', label='Tree Cover (class 10)')],
    loc='upper right'
)
ax.set_axis_off()
ax.set_title('Tree Cover (ESA WorldCover, Class 10)')
plt.show()
```
