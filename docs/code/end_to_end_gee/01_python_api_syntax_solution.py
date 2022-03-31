geometry = ee.Geometry.Point([77.60412933051538, 12.952912912328241])

s2 = ee.ImageCollection('COPERNICUS/S2')

filtered = s2.filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30)) \
  .filter(ee.Filter.date('2019-01-01', '2020-01-01')) \
  .filter(ee.Filter.intersects('.geo', geometry))
  
print(filtered.size().getInfo())