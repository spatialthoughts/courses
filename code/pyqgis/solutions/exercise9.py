import os
import time

data_dir = os.path.join(os.path.expanduser('~'), 'Downloads', 'pyqgis_masterclass')

layer = iface.activeLayer()

# Check if a layer is selected
if not layer:
    iface.messageBar().pushMessage('Please select a layer',  level=Qgis.Critical) 
# Check if the selected layer is a vector layer
if layer.type() != QgsMapLayer.VectorLayer:
    iface.messageBar().pushMessage('Please select a vector layer',  level=Qgis.Critical)

# Define parameters for QgsVectorFileWriter
output_name = 'output.csv'
output_path = os.path.join(data_dir, output_name)

# We will use QgsVectorFileWriter.create() method
# It takes the following parameters
# fileName: Path to the file
# fields: Fields to write
# geometryType: geometry type of output file
# srs: CRS of the output file
# transformContext: Datum transformation settings
# options: Save Options such as format, encoding etc.

# Define the options for saving the layer
save_options = QgsVectorFileWriter.SaveVectorOptions()
save_options.driverName = 'CSV'
save_options.fileEncoding = 'UTF-8'
# We can also add some format-specific layer options 
# These come from GDAL/OGR
# https://gdal.org/drivers/vector/csv.html
save_options.layerOptions = ['SEPARATOR=COMMA']

# Write the file
writer = QgsVectorFileWriter.create(
    fileName=output_path,
    fields=layer.fields(),
    geometryType=QgsWkbTypes.NoGeometry,
    srs=layer.crs(),
    transformContext=transform_context,
    options=save_options)

# Check if we were able to create the writer
if writer.hasError() != QgsVectorFileWriter.NoError:
    iface.messageBar().pushMessage(
        'Error:', writer.errorMessage, level=Qgis.Critical)

selected_count = layer.selectedFeatureCount()
if selected_count == 0:
    iface.messageBar().pushMessage(
        'Error:', 'No selected features', level=Qgis.Critical)
else:
    for f in layer.selectedFeatures():
        writer.addFeature(f)

    # delete the writer to flush features to disk
    del writer
    iface.messageBar().pushMessage(
    'Success:',
    f'Output file with {selected_count} features written at {output_path}',
    level=Qgis.Success)
