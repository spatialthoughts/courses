line_layer = QgsProject.instance().mapLayer('[% @layer_id %]')
point_layer_name = 'points'
distance = 10000
fid = [% $id %]
line_feature = line_layer.getFeature(fid)
line_geometry = line_feature.geometry().buffer(distance, 5)
point_layer = QgsProject.instance().mapLayersByName(point_layer_name)[0]
nearby_points = [p.id() for p in point_layer.getFeatures() 
    if p.geometry().intersects(line_geometry) ]
layer.selectByIds(nearby_points)
