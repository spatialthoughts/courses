from qgis.core import QgsDistanceArea

san_francisco = (37.7749, -122.4194)
new_york = (40.661, -73.944)
las_vegas = (36.1699, -115.1398)

d = QgsDistanceArea()
d.setEllipsoid('WGS84')


lat1, lon1 = san_francisco
lat2, lon2 = new_york
lat3, lon3 = las_vegas

# Remember the order is X,Y
point1 = QgsPointXY(lon1, lat1)
point2 = QgsPointXY(lon2, lat2)
point3 = QgsPointXY(lon3, lat3)

distance = d.measureLine([point1, point3, point2])
print('Total Distance {} meters'.format(distance))

# We can conver the distance to miles
distance_miles = d.convertLengthMeasurement(distance, QgsUnitTypes.DistanceMiles)

print('Total Distance {} miles'.format(distance_miles))

# We can also format the distance by rounding to 2 decimals
distance_formatted = QgsDistanceArea.formatDistance(
  distance_miles, 2, QgsUnitTypes.DistanceKilometers)
  
print('Total Distance {}'.format(distance_formatted))

# Create a line layer to display the route
vlayer = QgsVectorLayer('LineString?crs=EPSG:4326', 'route', 'memory')
provider = vlayer.dataProvider()
provider.addAttributes([QgsField('distance', QVariant.Double)])
vlayer.updateFields() 
f = QgsFeature()
f.setGeometry(QgsGeometry.fromPolylineXY([point1, point3, point2]))
f.setAttributes([distance_miles])
provider.addFeature(f)
vlayer.updateExtents() 
QgsProject.instance().addMapLayer(vlayer)

# You can also measure distance on a sphere by setting a custom ellipsoid
# Use 6371km as the radius
d.setEllipsoid(6371000, 6371000)
distance_sphere = d.measureLine([point1, point3, point2])
print('Total Distance {} meters (sphere)'.format(distance_sphere))
