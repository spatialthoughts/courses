feature_id = [%$id%]
layer_id = '[%@layer_id%]'

layer = QgsProject.instance().mapLayer(layer_id)

with edit(layer):
    layer.deleteFeature(feature_id)
    iface.messageBar().pushSuccess('Success', f'Feature {feature_id} Deleted')