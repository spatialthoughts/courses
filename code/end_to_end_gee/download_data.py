import datetime
import ee
import csv
import os

cloud_project = 'spatialthoughts'

try:
    ee.Initialize(project=cloud_project)
except:
    ee.Authenticate()
    ee.Initialize(project=cloud_project)

# Get current date
now = datetime.datetime.now()

# Define the period of past 1-week
end_date = ee.Date(now)
start_date = end_date.advance(-1, 'week')

date_string = end_date.format('YYYY_MM_dd')
filename = 'ssm_{}.csv'.format(date_string.getInfo())

# Saving to current directory. You can change the path to appropriate location
output_path = os.path.join(filename)

soilmoisture = ee.ImageCollection('NASA/SMAP/SPL4SMGP/008')
admin2 = ee.FeatureCollection('FAO/GAUL_SIMPLIFIED_500m/2015/level2')

# Filter to a state
karnataka = admin2.filter(ee.Filter.eq('ADM1_NAME', 'Karnataka'))

# Select the ssm band
ssm  = soilmoisture.select('sm_surface')

filtered = ssm .filter(ee.Filter.date(start_date, end_date))

mean = filtered.mean()

stats = mean.reduceRegions(**{
  'collection': karnataka,
  'reducer': ee.Reducer.mean().setOutputs(['meanssm']),
  'scale': 11000,
  'crs': 'EPSG:32643'
  })

# Select columns to keep and remove geometry to make the result lightweight
# Change column names to match your uploaded shapefile
columns = ['ADM2_NAME', 'meanssm']
exportCollection = stats.select(**{
    'propertySelectors': columns,
    'retainGeometry': False})

features = exportCollection.getInfo()['features']

data = []

for f in features:
    data.append(f['properties'])

field_names = ['ADM2_NAME', 'meanssm']

with open(output_path, 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames = field_names)
    writer.writeheader()
    writer.writerows(data)
    print('Success: File written at', output_path)
