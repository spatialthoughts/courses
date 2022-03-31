task = ee.batch.Export.image.toDrive(**{
    'image': clippedImage,
    'description': 'Terraclimate Image Export {}'.format(i+1),
    'fileNamePrefix': clippedImage.id().getInfo(),
    'folder':'earthengine',
    'scale': 4638.3,
    'region': geometry.bounds().getInfo()['coordinates'],
    'maxPixels': 1e10
})
task.start()
print('Started Task: ', i+1)