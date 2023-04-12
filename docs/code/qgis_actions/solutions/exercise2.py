from qgis.utils import iface

layer_id = '[%@layer_id%]'

layer = QgsProject.instance().mapLayer(layer_id)
selected_ids = [feature.id() for feature in layer.selectedFeatures()]

if selected_ids:
    new_layer = layer.materialize(QgsFeatureRequest(selected_ids))
    new_layer.setName('selected')
    QgsProject.instance().addMapLayer(new_layer)
    iface.messageBar().pushInfo('Success', 'New layer created')
else:
    iface.messageBar().pushCritical('Error', 'No selected features')