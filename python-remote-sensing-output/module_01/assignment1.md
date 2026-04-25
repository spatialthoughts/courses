Microsoft's [Planetary Computer Data Catalog]((https://planetarycomputer.microsoft.com/catalog)) hosts a large collection of remote sensing datasets and is served via STAC API.

Your task is to access the [Landsat Collection 2 Level-2](https://planetarycomputer.microsoft.com/dataset/landsat-c2-l2) collection and create a RGB median composite for Landsat-8 images for your chosen area of interest and year.

Notes:

- Data acces from Planetary Computer is largely similar to other STAC APIs but requires obtaining a signed url. This notebook provides the code snippets below to show the access pattern.
- The `landsat-c2-l2` collection contains images from all Landsat satellites. You will need to add a filter in your search query to select images from `landsat-8` platform.
- Landsat image bands have different scale and offsets. Look at the metadata of a STAC item to find the appropriate values.

----

Install and use the `planetary_computer` python package.


```python
%%capture
if 'google.colab' in str(get_ipython()):
    !pip install planetary_computer
```


```python
import planetary_computer as pc
```

Accessing data from Planetary Computer is free but requires getting a Shared Access Signature (SAS) token and sign the URLs. The `planetary_computer` Python package provides a simple mechanism for signing the URLs using `sign()` function. Specify the `patch_url` parameter in `odc.stac.load()` function.


```python
ds = stac.load(
    items,
    bands=['red', 'green', 'blue'],
    bbox=bbox,
    resolution=30,
    crs='utm',
    chunks={},
    patch_url=pc.sign,
    groupby='solar_day',
)
```
