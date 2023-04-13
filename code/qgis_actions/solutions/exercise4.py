import os
from qgis.utils import iface

path = r'[%location%]'
file_name = os.path.basename(path)
layer_name = os.path.splitext(file_name)[0]
layer_list = QgsProject.instance().mapLayersByName(layer_name)

if layer_list:
    iface.messageBar().pushCritical('Error', f'Raster Tile {file_name} already loaded.')
else:
    iface.addRasterLayer(path)
    iface.messageBar().pushSuccess('Success', f'Raster Tile {file_name} loaded')

layer_id = '[%@layer_id%]'
layer = QgsProject.instance().mapLayer(layer_id)
iface.setActiveLayer(layer)

