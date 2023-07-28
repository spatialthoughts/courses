from qgis.utils import iface

feature_name = '[%NAME%]'
feature_id = [%$id%]
layer_id = '[%@layer_id%]'

layer = QgsProject.instance().mapLayer(layer_id)
new_layer = layer.materialize(
    QgsFeatureRequest().setFilterFids([feature_id]))
new_layer.setName(feature_name)
QgsProject.instance().addMapLayer(new_layer)
iface.setActiveLayer(layer)
iface.messageBar().pushInfo('New Layer Created', feature_name)
