from qgis.core import QgsDistanceArea

san_francisco = (37.7749, -122.4194)
new_york = (40.661, -73.944)
las_vegas = (36.1699, -115.1398)

d = QgsDistanceArea()
d.setEllipsoid('WGS84')


lat1, lon1 = san_francisco
lat2, lon2 = las_vegas
lat3, lon3 = new_york
# Remember the order is X,Y
point1 = QgsPointXY(lon1, lat1)
point2 = QgsPointXY(lon2, lat2)
point3 = QgsPointXY(lon3, lat3)

distance = d.measureLine([point1, point2, point3])
print(distance/1000)

distance_mi = d.convertLengthMeasurement(distance, QgsUnitTypes.DistanceMiles)
print(distance_mi)
