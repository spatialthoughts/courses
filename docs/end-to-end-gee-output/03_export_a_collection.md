One of the most commonly asked questions by Earth Engine users is - *How do I download all images in a collection*? The Earth Engine Python API comes with a `ee.batch` module that allows you to launch batch exports and manage tasks. The recommended way to do batch exports like this is to use the Python API's `ee.batch.Export` functions and use a Python for-loop to iterate and export each image. The `ee.batch` module also gives you ability to control *Tasks* - allowing you to automate exports.


```python
import ee
```


```python
ee.Authenticate()
```


```python
ee.Initialize()
```

#### Create a Collection


```python
geometry = ee.Geometry.Point([107.61303468448624, 12.130969369851766])
s2 = ee.ImageCollection("COPERNICUS/S2")
rgbVis = {
  'min': 0.0,
  'max': 3000,
  'bands': ['B4', 'B3', 'B2'],
}

# Write a function for Cloud masking
def maskS2clouds(image):
  qa = image.select('QA60')
  cloudBitMask = 1 << 10
  cirrusBitMask = 1 << 11
  mask = qa.bitwiseAnd(cloudBitMask).eq(0).And(
             qa.bitwiseAnd(cirrusBitMask).eq(0))
  return image.updateMask(mask) \
      .select("B.*") \
      .copyProperties(image, ["system:time_start"])

filtered = s2 \
  .filter(ee.Filter.date('2019-01-01', '2020-01-01')) \
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30)) \
  .filter(ee.Filter.bounds(geometry)) \
  .map(maskS2clouds)

# Write a function that computes NDVI for an image and adds it as a band
def addNDVI(image):
  ndvi = image.normalizedDifference(['B5', 'B4']).rename('ndvi')
  return image.addBands(ndvi)

withNdvi = filtered.map(addNDVI)
```

#### Export All Images

Exports are done via the ``ee.batch`` module. A key difference between javascript and Python version is that the `region` parameter needs to be supplied with actual geometry coordinates.


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
    'fileNamePrefix': image.id().getInfo(),
    'folder':'earthengine',
    'scale': 100,
    'region': image.geometry().bounds().getInfo()['coordinates'],
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
