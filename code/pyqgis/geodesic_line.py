from qgis.core import QgsDistanceArea

new_york = (40.661, -73.944)
london = (51.5072, 0.1276)

lat1, lon1 = new_york
lat2, lon2 = london

# Remember the order is X,Y
point1 = QgsPointXY(lon1, lat1)
point2 = QgsPointXY(lon2, lat2)

d = QgsDistanceArea()
d.setEllipsoid('WGS84')

# Create a geodesic line with vertices every 100km
vertices = d.geodesicLine(point1, point2, 100000)

# Create a polyline from the vertices
# The method returns 1 geometry unless the line crosses antimeridien
geodesic_line = QgsGeometry.fromPolylineXY(vertices[0])

# Create a line layer to display the route
vlayer = QgsVectorLayer('LineString?crs=EPSG:4326', 'route', 'memory')
provider = vlayer.dataProvider()

f = QgsFeature()
f.setGeometry(geodesic_line)
provider.addFeature(f)
vlayer.updateExtents() 
QgsProject.instance().addMapLayer(vlayer)