### Create a Landsat Composite


[Landsat](https://www.usgs.gov/landsat-missions) satellites has been continuously observing the earth for over 40 years - making it an ideal choice for monitoring long term changes. For most parts of the world, the data is consistently available from 1990- onwards. Explore the data and create annual RGB composites for multiple time periods to see how your region of interest has changed.

The entire Landsat archive is available on Microsoft's [Planetary Computer Data Catalog]((https://planetarycomputer.microsoft.com/catalog)) and can be accessed freely. Your task is to access the [Landsat Collection 2 Level-2](https://planetarycomputer.microsoft.com/dataset/landsat-c2-l2) collection and use the techniques learnt in Module 1 to process the data and create annual RGB composites. You can try to create 2 composites - one for 2000 and another for 2025 to visualize how your area of interest has changed.


Notes:

- Data acces from Planetary Computer is largely similar to other STAC APIs but requires obtaining a signed url. This notebook provides the code snippets below to show the access pattern.
- The `landsat-c2-l2` collection contains images from all Landsat satellites. You will need to add a filter in your search query to select images from specific satellites, like `landsat-5`, `landsat-7` or `landsat-8`.
- Early years may not have enough images for your region. Adjust (or remove) the cloud filter to ensure you have 3-5 images for the year to create a cloud-free composite. Change the year if you do not find enough images.
- Landsat image bands have different scale and offsets. Look at the metadata of a STAC item to find the appropriate values.

----

Install and use the [`planetary_computer`](https://pypi.org/project/planetary-computer/) python package.


```python
import planetary_computer as pc
```

Accessing data from Planetary Computer is free but requires getting a Shared Access Signature (SAS) token and sign the URLs. The `planetary_computer` Python package provides a simple mechanism for signing the URLs using `sign()` function. Specify the `patch_url` parameter in `odc.stac.load()` function.


```python
ds = load(
    items,
    bands=['red', 'green', 'blue'],
    bbox=bbox,
    resolution=30,
    crs='utm',
    chunks={'x': 1024, 'y': 1024},  # Explicitly define chunk sizes
    patch_url=pc.sign,
    groupby='solar_day',
)
```
