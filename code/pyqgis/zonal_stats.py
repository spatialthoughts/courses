import os
from qgis.core import QgsApplication

qgs = QgsApplication([], False)
qgs.initQgis()

import processing
from processing.core.Processing import Processing
Processing.initialize()

data_dir = os.path.join(os.path.expanduser('~'), 'Downloads', 'pyqgis_masterclass')

vector_layer = 'seismic_zones.shp'
vector_layer_path = os.path.join(data_dir, vector_layer)

raster_layer = 'srtm.tif'
raster_layer_path = os.path.join(data_dir, raster_layer)

# Input vector has invalid geometries
# Fix them first
results = processing.run("native:fixgeometries", {
  'INPUT':vector_layer_path,
  'OUTPUT':'TEMPORARY_OUTPUT'})

fixed_vector_layer = results['OUTPUT']

# Run Zonal Statistics

# Save output to a geopackage
output_name = 'seismic_zones_with_elevation.gpkg'
output_path = os.path.join(data_dir, output_name)

processing.run("native:zonalstatisticsfb", {
  'INPUT': fixed_vector_layer,
  'INPUT_RASTER': raster_layer_path,
  'RASTER_BAND':1,
  'COLUMN_PREFIX':'elevation_',
  'STATISTICS':[2],
  'OUTPUT':output_path})

print('Output Layer Created', output_path)
qgs.exitQgis()
