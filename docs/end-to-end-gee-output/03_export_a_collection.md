One of the most commonly asked questions by Earth Engine users is - *How do I download all images in a collection*? The Earth Engine Python API comes with a `ee.batch` module that allows you to launch batch exports and manage tasks. The recommended way to do batch exports like this is to use the Python API's `ee.batch.Export` functions and use a Python for-loop to iterate and export each image. The `ee.batch` module also gives you ability to control *Tasks* - allowing you to automate exports.

> You can also export images in a collection using Javascript API in the Code Editor but this requires you to manually start the tasks for each image. This approach is fine for small number of images. You can check out the [recommended script](https://code.earthengine.google.co.in/?scriptPath=users%2Fujavalgandhi%2FEnd-to-End-GEE%3ASupplement%2FImage_Collections%2FExporting_ImageCollections).

#### Initialization

First of all, you need to run the following cells to initialize the API and authorize your account. You must have a Google Cloud Project associated with your GEE account. Replace the `cloud_project` with your own project from [Google Cloud Console](https://console.cloud.google.com/).


```python
import ee
```


```python
cloud_project = 'spatialthoughts'

try:
    ee.Initialize(project=cloud_project)
except:
    ee.Authenticate()
    ee.Initialize(project=cloud_project)
```

#### Create a Collection


```python
geometry = ee.Geometry.Point([107.61303468448624, 12.130969369851766])
s2 = ee.ImageCollection('COPERNICUS/S2_HARMONIZED')
rgbVis = {
  'min': 0.0,
  'max': 3000,
  'bands': ['B4', 'B3', 'B2'],
}

filtered = s2 \
  .filter(ee.Filter.date('2019-01-01', '2020-01-01')) \
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30)) \
  .filter(ee.Filter.bounds(geometry)) \

# Load the Cloud Score+ collection
csPlus = ee.ImageCollection('GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED')
csPlusBands = csPlus.first().bandNames()

# We need to add Cloud Score + bands to each Sentinel-2
# image in the collection
# This is done using the linkCollection() function
filteredS2WithCs = filtered.linkCollection(csPlus, csPlusBands)

# Function to mask pixels with low CS+ QA scores.
def maskLowQA(image):
  qaBand = 'cs'
  clearThreshold = 0.5
  mask = image.select(qaBand).gte(clearThreshold)
  return image.updateMask(mask)

filteredMasked = filteredS2WithCs \
  .map(maskLowQA)

# Write a function that computes NDVI for an image and adds it as a band
def addNDVI(image):
  ndvi = image.normalizedDifference(['B5', 'B4']).rename('ndvi')
  return image.addBands(ndvi)

withNdvi = filteredMasked.map(addNDVI)
```

#### Export All Images

Exports are done via the ``ee.batch`` module. This module allows you to automatically start an export - making it suitable for batch exports.


```python
image_ids = withNdvi.aggregate_array('system:index').getInfo()
print('Total images: ', len(image_ids))
```


```python
# Export with 100m resolution for this demo
for i, image_id in enumerate(image_ids):
  image = ee.Image(withNdvi.filter(ee.Filter.eq('system:index', image_id)).first())
  task = ee.batch.Export.image.toDrive(**{
    'image': image.select('ndvi'),
    'description': 'Image Export {}'.format(i+1),
    'fileNamePrefix': image_id,
    'folder':'earthengine',
    'scale': 100,
    'region': image.geometry(),
    'maxPixels': 1e10
  })
  task.start()
  print('Started Task: ', i+1)
```

#### Manage Running/Waiting Tasks

You can manage tasks as well. Get a list of tasks and get state information on them


```python
tasks = ee.batch.Task.list()
for task in tasks:
  task_id = task.status()['id']
  task_state = task.status()['state']
  print(task_id, task_state)
```

You can cancel tasks as well


```python
tasks = ee.batch.Task.list()
for task in tasks:
    task_id = task.status()['id']
    task_state = task.status()['state']
    if task_state == 'RUNNING' or task_state == 'READY':
        task.cancel()
        print('Task {} canceled'.format(task_id))
    else:
        print('Task {} state is {}'.format(task_id, task_state))
```

### Exercise

The code below uses the TerraClimate data and creates an ImageCollection with 12 monthly images of maximum temperature. It also extract the geometry for Australia from the LSIB collection. Add the code to start an export task for each image in the collection for australia.

- **Hint1**: TerraClimate images have a scale of 4638.3m
- **Hint2**: You need to export the image contained in the clippedImage variable


```python
import ee

lsib = ee.FeatureCollection('USDOS/LSIB_SIMPLE/2017')
australia = lsib.filter(ee.Filter.eq('country_na', 'Australia'))
geometry = australia.geometry()

terraclimate = ee.ImageCollection('IDAHO_EPSCOR/TERRACLIMATE')
tmax = terraclimate.select('tmmx')

def scale(image):
  return image.multiply(0.1) \
    .copyProperties(image,['system:time_start'])

tmaxScaled = tmax.map(scale)

filtered = tmaxScaled \
  .filter(ee.Filter.date('2020-01-01', '2021-01-01')) \
  .filter(ee.Filter.bounds(geometry))

image_ids = filtered.aggregate_array('system:index').getInfo()
print('Total images: ', len(image_ids))
```

Replace the comments with your code.


```python
for i, image_id in enumerate(image_ids):
    exportImage = ee.Image(filtered.filter(ee.Filter.eq('system:index', image_id)).first())
    # Clip the image to the region geometry
    clippedImage = exportImage.clip(geometry)

    ## Create the export task using ee.batch.Export.image.toDrive()

    ## Start the task
```
