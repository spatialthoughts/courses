javascript_code = """
var geometry = ee.Geometry.Point([77.60412933051538, 12.952912912328241])
var s2 = ee.ImageCollection("COPERNICUS/S2");

var rgbVis = {
  min: 0.0,
  max: 3000,
  bands: ['B4', 'B3', 'B2'],
};
var filtered = s2.filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30))
  .filter(ee.Filter.date('2019-01-01', '2020-01-01'))
  .filter(ee.Filter.bounds(geometry))
 
var mosaic = filtered.mosaic() 
 
var medianComposite = filtered.median();

Map.centerObject(geometry, 10);
Map.addLayer(medianComposite, rgbVis, 'Median Composite')
"""

lines = geemap.js_snippet_to_py(javascript_code, add_new_cell=False, import_ee=True, import_geemap=True, show_map=True)
for line in lines:
    print(line.rstrip())