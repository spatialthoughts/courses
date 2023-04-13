import os
from qgis.utils import iface

path = r'[%location%]'
file_name = os.path.basename(path)
layer_name = os.path.splitext(file_name)[0]
layer_list = QgsProject.instance().mapLayersByName(layer_name)

if layer_list:
    QgsProject.instance().removeMapLayer(layer_list[0])
    #iface.mapCanvas().refresh()
