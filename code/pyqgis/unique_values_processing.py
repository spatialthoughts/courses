import os
from qgis.core import QgsApplication, QgsVectorLayer, QgsProject
qgs = QgsApplication([], False)
qgs.initQgis()

import processing
from processing.core.Processing import Processing
Processing.initialize()

data_dir = os.path.join(os.path.expanduser('~'), 'Downloads', 'pyqgis_in_a_day')

filename = 'sf.gpkg|layername=zoning'
uri = os.path.join(data_dir, filename)
layer = QgsVectorLayer(uri, 'zoning', 'ogr')

output_name = 'unique_values.csv'

results = processing.run("qgis:listuniquevalues", {
    'INPUT': layer,
    'FIELDS': ['zoning']
    })

unique_values = results['UNIQUE_VALUES']

print('Unique values in the zoning field', unique_values)

# Delete the layer object from memory
# Without this you may get a Segmentation Fault on exit
# when the exitQgis() method will try clearning the layer registry
# Alternatively, you can add the layer so it is present in the registry
# QgsProject.instance().addMapLayer(layer, False)
del(layer)
qgs.exitQgis()