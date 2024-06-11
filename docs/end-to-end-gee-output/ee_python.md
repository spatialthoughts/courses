### Access and Visualize CMIP6 Data in GEE


```python
import ee
import geemap
```


```python
cloud_project = 'spatialthoughts'

try:
    ee.Initialize(project=cloud_project)
except:
    ee.Authenticate()
    ee.Initialize(project=cloud_project)

```


```python
# Use the CMIP6 Climate Projections Dataset
cmip6 = ee.ImageCollection('NASA/GDDP-CMIP6')

# Select a model and a scenario

model = 'ACCESS-CM2'
scenario = 'ssp245'

# Select the band
# Here we are using maximum air temperature
band = 'tasmax'

# Select the date range
startDate = ee.Date.fromYMD(2030, 3, 1)
endDate = startDate.advance(1, 'month')

filtered = cmip6 \
  .filter(ee.Filter.date(startDate, endDate)) \
  .filter(ee.Filter.eq('model', model)) \
  .filter(ee.Filter.eq('scenario', scenario)) \
  .select(band)

# Temperature values are in Kelvin
# convert to Celcius

def scaleValues(image):
  return image \
    .subtract(273.15) \
    .copyProperties(image,
      ['system:time_start', 'model', 'scenario'])

scaled = filtered.map(scaleValues)

# Calculate average daily maximum temperature
mean = scaled.mean()
```


```python
tempVis = {
  'min': 10,
  'max': 40,
  'palette': ['blue', 'purple', 'cyan', 'green', 'yellow', 'red'],
}

Map = geemap.Map(width=800)
Map.addLayer(mean, tempVis, 'Average Daily Maximum Air Temperature')
Map
```
