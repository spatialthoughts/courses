```python
import os
import rasterio
import glob
import numpy as np
```


```python
home_dir = os.path.expanduser('~')
data_pkg_path = 'Downloads/python_foundation'
sentinel2_dir = 'sentinel2'
pattern = '*.jp2'

path = os.path.join(home_dir, data_pkg_path, sentinel2_dir, pattern)
files = glob.glob(path)
```


```python
red_band = 'B04'
green_band = 'B03'
blue_band = 'B02'
nir_band = 'B08'
for file in files:
    if red_band in file:
        red_band_file = file
    if green_band in file:
        green_band_file = file
    if blue_band in file:
        blue_band_file = file
    if nir_band in file:
        nir_band_file = file
(red_band_file, nir_band_file)
```




    ('/Users/ujaval/Downloads/python_foundation/sentinel2/T43PGQ_20200218T050851_B04.jp2',
     '/Users/ujaval/Downloads/python_foundation/sentinel2/T43PGQ_20200218T050851_B08.jp2')




```python
red_dataset = rasterio.open(red_band_file)
green_dataset = rasterio.open(green_band_file)
blue_dataset = rasterio.open(blue_band_file)
nir_dataset = rasterio.open(nir_band_file)
red = red_dataset.read(1)
green = green_dataset.read(1)
blue = blue_dataset.read(1)
nir = nir_dataset.read(1)
```


```python
metadata = red_dataset.meta
transform = red_dataset.transform
metadata.update({'count':3})
```


```python
output_filename = 'rgb.jp2'
output_dir = 'Downloads'
output_path = os.path.join(home_dir, output_dir, output_filename)

new_dataset = rasterio.open(output_path, 'w', 
                            **metadata)
new_dataset.write(red, 1)
new_dataset.write(green, 2)
new_dataset.write(blue, 3)
new_dataset.close()
```


```python

```




    array([[       nan,        nan,        nan, ..., 0.71678024, 0.71648164,
            0.71259324],
           [       nan,        nan,        nan, ..., 0.61104629, 0.69983884,
            0.71975363],
           [       nan,        nan,        nan, ..., 0.5365353 , 0.64309623,
            0.5819135 ],
           ...,
           [0.54329609, 0.56717147, 0.52723638, ..., 0.61158711, 0.58892482,
            0.56165443],
           [0.55857078, 0.56413925, 0.54087737, ..., 0.60589922, 0.60695297,
            0.58389262],
           [0.57458315, 0.60047619, 0.58546366, ..., 0.62718763, 0.62841976,
            0.57404521]])




```python
red = red.astype('float32')
nir = nir.astype('float32')
```


```python

```


```python
np.seterr(divide='ignore', invalid='ignore')

ndvi = (nir - red) / (nir + red)

```


    ---------------------------------------------------------------------------

    AttributeError                            Traceback (most recent call last)

    <ipython-input-78-46bf50437848> in <module>
          2 
          3 ndvi = (nir - red) / (nir + red)
    ----> 4 ndvi.where(ndvi > 1)
    

    AttributeError: 'numpy.ndarray' object has no attribute 'where'



```python
np.where(ndvi==100)
```




    (array([6992]), array([360]))




```python

ndvi[6992][360]
```




    100.0




```python
metadata = red_dataset.meta
transform = red_dataset.transform
metadata.update({'dtype': 'float64', 'driver': 'GTiff'})
metadata
```




    {'driver': 'GTiff',
     'dtype': 'float64',
     'nodata': None,
     'width': 10980,
     'height': 10980,
     'count': 1,
     'crs': CRS.from_epsg(32643),
     'transform': Affine(10.0, 0.0, 699960.0,
            0.0, -10.0, 1500000.0)}




```python
output_filename = 'ndvi.tif'
output_dir = 'Downloads'
output_path = os.path.join(home_dir, output_dir, output_filename)

new_dataset = rasterio.open(output_path, 'w', 
                            **metadata)
new_dataset.write(ndvi, 1)
new_dataset.close()
```
