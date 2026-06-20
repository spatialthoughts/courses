[Google Colab](https://colab.research.google.com/) is a hosted Jupyter notebook environment that allows anyone to run Python code via a web-browser. It provides you free computation and data storage that can be utilized by your Python code.

You can click the `+Code` button to create a new cell and enter a block of code. To run the code, click the **Run Code** button next to the cell, or press `Shift+Enter` key.


```python
print('Hello World')
```

### Package Management

Colab comes pre-installed with many Python packages. You can use a package by simply importing it.


```python
import pandas as pd
import geopandas as gpd
```

Each Colab notebook instance is run on a Ubuntu Linux machine in the cloud. If you want to install any packages, you can run a command by prefixing the command with a `!`. For example, you can install third-party packages via `pip` using the command `!pip`.

> Tip: If you want to list all pre-install packages and their versions in your Colab environemnt, you can run `!pip list -v`.


```python
!pip install rioxarray
```


```python
import rioxarray
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

We can download some data from the internet and store it in the Colab environment. Below is a helper function to download a file from a URL.


```python
import requests

def download(url):
    filename = os.path.join(data_folder, os.path.basename(url))
    if not os.path.exists(filename):
      with requests.get(url, stream=True, allow_redirects=True) as r:
          with open(filename, 'wb') as f:
              for chunk in r.iter_content(chunk_size=8192):
                  f.write(chunk)
      print('Downloaded', filename)
```

Let's download the [Populated Places](https://www.naturalearthdata.com/downloads/10m-cultural-vectors/) dataset from Natural Earth.


```python
download('https://naciscdn.org/naturalearth/10m/cultural/' +
         'ne_10m_populated_places_simple.zip')
```

The file is now in our local filesystem. We can construct the path to the data folder and read it using `geopandas`


```python
file = 'ne_10m_populated_places_simple.zip'
filepath = os.path.join(data_folder, file)
places = gpd.read_file(filepath)
places
```

### Using AI-Assisted Coding

Google Colab comes with an Gemini AI assistant to help you write and debug code. You can click the *Gemini spark* icon in the notebook footer to open the main chat panel.

Let's ask the assistant to write the code to filter our `places` DataFrame. You can write the following prompt and click *send* button:

```
Select all the places from `places` Dataframe which are country capitals and save to a new variable `capitals`.
```

The coding agent will add a new cell in the notebook like below.


```python
capitals = places[places['adm0cap'] == 1]
display(capitals)
```

### Saving Outputs

We can write the results to the disk as a GeoPackage file. After running the cell, open the **Files** tab from the left-hand panel in Colab and browse to the `output` folder. Locate the `capitals.gpkg` file and click the **⋮** button and select *Download* to download the file locally.


```python
output_file = 'capitals.gpkg'
output_path = os.path.join(output_folder, output_file)
capitals.to_file(driver='GPKG', filename=output_path)
```

The local disk is not persistent and the data will be deleted when the Colab Runtime is disconnected. Google Colab has a built-in integration with Google Drive and provides the easiest solution for storing persistent data.

Google Drive integration is only available in the consumer version of Colab so we check the runtime before mounting the drive.


```python
import os

if 'COLAB_RELEASE_TAG' in os.environ:
    environment = 'colab'
    if os.environ.get('VERTEX_PRODUCT') == 'COLAB_ENTERPRISE':
        environment = 'colab_enterprise'
else:
    environment = 'local'
print('Environment:', environment)
```

The following cell mounts your Google Drive in the Colab runtime.


```python
if environment == 'colab':
    from google.colab import drive
    drive.mount('/content/drive')
    drive_folder_root = 'MyDrive'
    drive_data_folder = 'python-remote-sensing'
    drive_folder_path = os.path.join('/content/drive', drive_folder_root, drive_data_folder)
    data_folder = drive_folder_path
    output_folder = drive_folder_path
else:
    data_folder = 'data'
    output_folder = 'output'

if not os.path.exists(data_folder):
    os.mkdir(data_folder)
if not os.path.exists(output_folder):
    os.mkdir(output_folder)

print(f'Environment: {environment}')
print(f'Data folder: {data_folder}')
print(f'Output folder: {output_folder}')
```


```python
output_file = 'capitals.gpkg'
output_path = os.path.join(output_folder, output_file)
capitals.to_file(output_path)
```

### Using the Terminal (Advanced)

A recent update to Google Colab added support for [Terminal](https://medium.com/google-colab/colab-terminal-is-now-free-for-all-users-9a10eaef2ca8) within Google Colab. Terminal access allows you to run Linux commands directly on your Colab Runtime and gives you advanced capabilities to do more analysis in the cloud.

You can open the terminal by clicking on the **Terminal** button in the bottom left of the notebook.

The Terminal opens in the default `/content` directory. As we have created a `data` folder, we can use the `cd` command to navigate to it and `ls` command to list the files.

```
cd data
ls
```

#### Downloading Data

As we have access to standard Linux commands, we can use `wget` command to download data from the internet.

```
wget https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_annual/tifs/chirps-v2.0.2024.tif
```

#### Installing Packages

We can use the popular [GDAL](https://gdal.org/) utilities to help conversion of data formats. Run the following command to install the `gdal-bin` package.

```
apt-get install gdal-bin
```

#### Data Conversion

We can use the `gdal_translate` command to convert the downloaded GeoTIFF file to a Cloud-Optimized GeoTIFF.

```
gdal_translate -of COG chirps-v2.0.2024.tif chirps-v2.0.2024_cog.tif
```

We can copy the resulting file to our Google Drive folder using the Linux `cp` command.

```
cp chirps-v2.0.2024_cog.tif /content/drive/MyDrive/python-remote-sensing/
```
