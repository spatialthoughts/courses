import ee
# Replace the service account with your service account email
service_account = 'export-data-gee@spatialthoughts.iam.gserviceaccount.com'
# Replace the value with the path to your private key json file
private_key_path = '.private_key.json'
credentials = ee.ServiceAccountCredentials(service_account, private_key_path)
ee.Initialize(credentials)

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

for i, image_id in enumerate(image_ids):
    exportImage = ee.Image(filtered.filter(
        ee.Filter.eq('system:index', image_id)).first())

    clippedImage = exportImage.clip(geometry)
    
    task = ee.batch.Export.image.toDrive(**{
        'image': clippedImage,
        'description': 'Terraclimate Image Export {}'.format(i+1),
        'fileNamePrefix': image_id,
        'folder':'earthengine',
        'scale': 4638.3,
        'region': geometry,
        'maxPixels': 1e10
    })
    task.start()
    print('Started Task: ', i+1)
