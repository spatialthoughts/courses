import os
from qgis.core import QgsApplication, QgsVectorLayer

qgs = QgsApplication([], False)
qgs.initQgis()

data_dir = os.path.join(os.path.expanduser('~'), 'Downloads/pyqgis_in_a_day/')

filename = 'sf.gpkg|layername=zoning'
uri = os.path.join(data_dir, filename)
layer = QgsVectorLayer(uri, 'zoning', 'ogr')

output_name = 'output.csv'
output_path = os.path.join(data_dir, output_name)
    
with open(output_path, 'w') as output_file:
	fieldnames = [field.name() for field in layer.fields()]
	line = ','.join(name for name in fieldnames) + '\n'
	output_file.write(line)
	for f in layer.getFeatures():
		line = ','.join(str(f[name]) for name in fieldnames) + '\n'
		output_file.write(line)
        
print('Success: ', 'Output file written at' + output_path)

# Delete the layer object from memory
# Without this you may get a Segmentation Fault on exit
del(layer)
qgs.exitQgis()
