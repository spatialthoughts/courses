import datetime
import ee
import json
import os

ee.Initialize()

# Get current date and convert to milliseconds 
end_date = ee.Date(datetime.datetime.now().timestamp()*1000)
start_date = end_date.advance(-1, 'week')

date_string = end_date.format('YYYY_MM_dd')
filename = 'ssm_{}.geojson'.format(date_string.getInfo())

# Saving to current directory. You can change the path to appropriate location
output_path = os.path.join(filename)

# Datasets
soilmoisture = ee.ImageCollection("NASA_USDA/HSL/SMAP10KM_soil_moisture")
admin2 = ee.FeatureCollection("FAO/GAUL_SIMPLIFIED_500m/2015/level2")

# Filter to a state
karnataka = admin2.filter(ee.Filter.eq('ADM1_NAME', 'Karnataka'))

# Select the ssm band
ssm  = soilmoisture.select('ssm')

filtered = ssm .filter(ee.Filter.date(start_date, end_date))

mean = filtered.mean()

stats = mean.reduceRegions(**{
  'collection': karnataka,
  'reducer': ee.Reducer.mean().setOutputs(['meanssm']),
  'scale': 10000,
  })

# Select columns to keep and remove geometry to make the result lightweight
# Change column names to match your uploaded shapefile
columns = ['ADM2_NAME', 'meanssm']
exportCollection = stats.select(**{
    'propertySelectors': columns,
    'retainGeometry': False})

# Get the result from the server
output = json.dumps(exportCollection.getInfo())

with open(output_path, 'w') as f:
    f.write(output)
    print('Success: File written at', output_path)