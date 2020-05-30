```python
import os
import rasterio
import numpy as np
from numpy import random
```


```python
home_dir = os.path.expanduser('~')
data_pkg_path = 'Downloads/python_foundation'
filename = 'demo.jp2'

path = os.path.join(home_dir, data_pkg_path, filename)
print(path)
```

    /Users/ujaval/Downloads/python_foundation/demo.jp2



```python
dataset = rasterio.open(path)
```


```python
dataset.meta
```




    {'driver': 'JP2OpenJPEG',
     'dtype': 'uint8',
     'nodata': None,
     'width': 5000,
     'height': 5000,
     'count': 3,
     'crs': CRS.from_epsg(26910),
     'transform': Affine(0.5999999999999999, 0.0, 554028.0,
            0.0, -0.6000000005999999, 4246325.999943)}




```python
red = dataset.read(1)
```


```python
red.shape
```




    (5000, 5000)




```python
x = random.randint(100, size=(5000))
zeros = np.where(x==10)
```


```python
zeros
```




    (array([  86,  214,  242,  463,  565,  647,  703,  712,  797, 1034, 1103,
            1213, 1460, 1613, 1734, 1933, 2050, 2052, 2112, 2137, 2225, 2256,
            2370, 2469, 2596, 2744, 2885, 2893, 2988, 3063, 3137, 3232, 3331,
            3376, 3528, 3583, 3629, 3654, 3686, 3782, 3792, 3827, 3891, 3947,
            3968, 4001, 4192, 4232, 4438, 4588, 4604, 4652, 4683, 4771, 4829,
            4870]),)




```python
grid = np.array([[ 1, 3, 4, 2],
                [3, 5, 7, 8],
                [0, 0, 0, 0],
                [5, 0, 6, 8],
                [0, 0, 0, 0],
                [10, 3, 5, 6]])
grid
```




    array([[ 1,  3,  4,  2],
           [ 3,  5,  7,  8],
           [ 0,  0,  0,  0],
           [ 5,  0,  6,  8],
           [ 0,  0,  0,  0],
           [10,  3,  5,  6]])




```python
idx = np.argwhere(np.all(grid == 0, axis=1))

```


    ---------------------------------------------------------------------------

    NameError                                 Traceback (most recent call last)

    <ipython-input-28-91e86b6369f8> in <module>
    ----> 1 idx = np.argwhere(np.all(grid == 0, axis=1))
    

    NameError: name 'grid' is not defined

