# Initialize QGIS
from qgis.core import QgsApplication

qgs = QgsApplication([], False)
qgs.initQgis()

import processing
from processing.core.Processing import Processing
Processing.initialize()

# Use PyQGIS APIs
from qgis.core import QgsDistanceArea, QgsPointXY

san_francisco = (37.7749, -122.4194)
new_york = (40.661, -73.944)

d = QgsDistanceArea()
d.setEllipsoid('WGS84')


lat1, lon1 = san_francisco
lat2, lon2 = new_york
point1 = QgsPointXY(lon1, lat1)
point2 = QgsPointXY(lon2, lat2)

distance = d.measureLine([point1, point2])
print('Ellipsoid Distance', distance/1000)

# Exit QGIS
qgs.exitQgis()
