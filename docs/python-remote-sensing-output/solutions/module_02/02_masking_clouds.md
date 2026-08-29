### Exercise

### Exercise

The [`odc-algo`](https://github.com/opendatacube/odc-algo/tree/main) package provides useful algorithms for remote sensing data processing. We will use the `mask_cleanup()` function to apply morphological operators to clean up the cloud mask for more robust cloud masking. 

It supports the following operations

* `closing`: Removes small holes in cloud - morphological closing
* `opening`: Shrinks away small areas of the mask
* `dilation`: Adds padding to the mask
* `erosion`: Shrinks the mask

Along with the operation, you specify a `radius` parameter that controls the size of the window when applying the operations. 

The code snippet below shows how to use the function. Test these operations to see its effect on the mask. Visualize the `mask` and `cleaned_mask` side-by-side to see the results.


```python
from odc.algo import mask_cleanup

# Contract and then expand the cloud mask to remove small areas
cleaned_mask = mask_cleanup(mask, [('opening', 2), ('dilation', 3)])

```


```python
fig, (ax0, ax1) = plt.subplots(1, 2)
fig.set_size_inches(10,5)

mask_colormap = ListedColormap(['#00000000', '#FF0000FF'])
mask.plot.imshow(
    ax=ax0,
    cmap=mask_colormap,
    add_colorbar=False)

ax0.set_title('Original Mask')

# RGBA: Transparent, Red
mask_colormap = ListedColormap(['#00000000', '#FF0000FF'])
cleaned_mask.plot.imshow(
    ax=ax1,
    cmap=mask_colormap,
    add_colorbar=False)

ax1.set_title('Processed Mask')
for ax in (ax0, ax1):
  ax.set_axis_off()
  ax.set_aspect('equal')
plt.show()
```
