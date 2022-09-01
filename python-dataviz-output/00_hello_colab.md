[Google Colab](https://colab.research.google.com/) is a hosted Jupyter notebook environment that allows anyone to run Python code via a web-browser. It provides you free computation and data storage that can be utilized by your Python code.

You can click the `+Code` button to create a new cell and enter a block of code. To run the code, click the **Run Code** button next to the cell, or press `Shirt+Enter` key.


```python
print('Hello World')
```

    Hello World


### Package Management

Colab comes pre-installed with many Python packages. You can use a package by simply importing it.


```python
import pandas as pd
```

Each Colab notebook instance is run on a Ubuntu Linux machine in the cloud. If you want to install any packages, you can run a command by prefixing the command with a `!`. For example, you can install third-party packages via `pip` using the command `!pip`.

> Tip: If you want to list all pre-install packages and their versions in your Colab environemnt, you can run `!pip list -v`.


```python
!pip install --quiet rioxarray
```


```python
import rioxarray
```

Some packages may also require additional binaries or local configuration. This can be achieved using package management commands for Ubuntu Linux. For example, we can run `apt` command to install specific package required for `geopandas` to work correctly.


```python
!apt install -qq libspatialindex-dev
!pip install --quiet fiona shapely pyproj rtree
!pip install --quiet geopandas
```

    libspatialindex-dev is already the newest version (1.8.5-5).
    The following package was automatically installed and is no longer required:
      libnvidia-common-460
    Use 'apt autoremove' to remove it.
    0 upgraded, 0 newly installed, 0 to remove and 20 not upgraded.



```python
import geopandas as gpd
```

### Data Management

Colab provides 100GB of disk space along with your notebook. This can be used to store your data, intermediate outputs and results. 

The code below will create 2 folders named 'data' and 'output' in your local filesystem.


```python
import os

data_folder = 'data'
output_folder = 'output'

if not os.path.exists(data_folder):
    os.mkdir(data_folder)
if not os.path.exists(output_folder):
    os.mkdir(output_folder)
```

We can download some data from the internet and store it in the Colab environment. Below is a helper function that uses `urllib` to fetch any file from a URL.


```python
def download(url):
    filename = os.path.join(data_folder, os.path.basename(url))
    if not os.path.exists(filename):
        from urllib.request import urlretrieve
        local, _ = urlretrieve(url, filename)
        print('Downloaded ' + local)
```

Let's download the [Populated Places](https://www.naturalearthdata.com/downloads/10m-cultural-vectors/) dataset from Natural Earth.


```python
download('https://naciscdn.org/naturalearth/10m/cultural/' + 
         'ne_10m_populated_places_simple.zip')
```

    Downloaded data/ne_10m_populated_places_simple.zip


The file is now in our local filesystem. We can construct the path to the data folder and read it using `geopandas`


```python
file = 'ne_10m_populated_places_simple.zip'
filepath = os.path.join(data_folder, file)
places = gpd.read_file(filepath)
```

Let's do some data processing and write the results to a new file. The code below will filter all places which are also country capitals.


```python
capitals = places[places['adm0cap'] == 1]
capitals
```

We can write the results to the disk as a GeoPackage file.


```python
output_file = 'capitals.gpkg'
output_path = os.path.join(output_folder, output_file)
capitals.to_file(driver='GPKG', filename=output_path)
```

You can open the **Files** tab from the left-hand panel in Colab and browse to the `output` folder. Locate the `capitals.gpkg` file and click the **⋮** button and select *Download* to download the file locally.
