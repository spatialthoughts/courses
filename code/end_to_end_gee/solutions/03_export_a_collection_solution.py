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
