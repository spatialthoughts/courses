### Exercise

Apply a threshold to the NDVI values to create a binary raster.

Hint:

Xarray offers two different `where()` functions.

* [`xarray.DataArray.where`](https://docs.xarray.dev/en/stable/generated/xarray.DataArray.where.html): Applies a condition and sets the non-matching values to NaN
* [`xarray.where`](https://docs.xarray.dev/en/stable/generated/xarray.where.html): Applies a condition and allows you to set both matching and non-matching values.

Use the `xr.where()` function to set matching values to 1 and non-matching values to 0.


```python
threshold = 0
# Create a new array 'water' where all MNDWI values
#  greater than the threshold is 1 and others are 0
# Visualize the results.
```


```python
# Create a new array 'water' where all MNDWI values
#  greater than the threshold is 1 and others are 0
water = xr.where(mndwi > threshold, 1, 0)
```


```python
from matplotlib.colors import ListedColormap

# Define a custom colormap: white for 0, blue for 1
cmap = ListedColormap(['white', 'blue'])

fig, ax = plt.subplots(1, 1)
fig.set_size_inches(5,5)

water.plot.imshow(
    ax=ax,
    cmap=cmap,
    vmin=0,
    vmax=1,
    add_colorbar=False) 
plt.title('Water Mask') 
ax.set_axis_off()
ax.set_aspect('equal')
plt.show()
```

### Otsu Thresholding of MNDWI


```python
import numpy as np
mndwi_finite_values = mndwi.values[np.isfinite(mndwi.values)]
```


```python
fig, ax = plt.subplots(1, 1, figsize=(8, 5))
ax.hist(mndwi_finite_values, bins=50, color='skyblue', edgecolor='black')
ax.set_title('Histogram of MNDWI Values')
ax.set_xlabel('MNDWI Value')
ax.set_ylabel('Frequency')
plt.grid(axis='y', alpha=0.75)
```


```python
from skimage.filters import threshold_otsu
otsu_threshold = threshold_otsu(mndwi_finite_values)
otsu_threshold
```




    array([[1, 1, 1, ..., 1, 1, 1],
           [1, 1, 1, ..., 1, 1, 0],
           [1, 1, 1, ..., 1, 1, 1],
           ...,
           [0, 0, 0, ..., 0, 0, 0],
           [0, 0, 0, ..., 0, 0, 0],
           [0, 0, 0, ..., 0, 0, 0]], dtype=int8)




```python
fig, ax = plt.subplots(1, 1, figsize=(8, 5))
ax.hist(mndwi_finite_values, bins=50, color='skyblue', edgecolor='black')
ax.set_title('Histogram of MNDWI Values')
ax.set_xlabel('MNDWI Value')
ax.set_ylabel('Frequency')
plt.grid(axis='y', alpha=0.75)

# Add the threshold as a vertical line
if not np.isnan(otsu_threshold):
    ax.axvline(otsu_threshold, color='red', linestyle='dashed', linewidth=2, label=f'Otsu Threshold: {otsu_threshold:.2f}')
    ax.legend()

plt.tight_layout()
plt.show()
```


```python
water_otsu = xr.where(mndwi > otsu_threshold, 1, 0)
```

### Multiple Thresholding (NDVI Example)


```python
vegetation_classes = xr.where(
    ndvi < 0, # Condition 1: ndvi < 0
    1,
    xr.where(
        ndvi > 0.5, # Condition 2: ndvi > 0.5
        3,
        2 # Else (0 <= ndvi <= 0.5)
    )
).astype('byte')
vegetation_classes
```


```python
vegetation_classes.values
```




    array([[3, 3, 3, ..., 3, 3, 3],
           [3, 3, 3, ..., 3, 3, 2],
           [3, 3, 3, ..., 3, 3, 3],
           ...,
           [2, 2, 2, ..., 2, 2, 2],
           [2, 2, 2, ..., 2, 2, 2],
           [2, 2, 2, ..., 2, 2, 2]], dtype=int8)


