fig, ax = plt.subplots(1, 1)
fig.set_size_inches(12, 10)
merged.plot.imshow(ax=ax, cmap='viridis', add_labels=False)

contours = merged.plot.contour(ax=ax, colors='white', levels=10)
ax.clabel(contours, inline=True, fontsize=8, fmt='%.0f')
plt.tight_layout()
plt.show()
