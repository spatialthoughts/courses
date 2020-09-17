import math

def ellipsoid_distance(origin, destination):
  lat1, lon1 = origin
  lat2, lon2 = destination
  # Remember the order is X,Y
  point1 = QgsPointXY(lon1, lat1)
  point2 = QgsPointXY(lon2, lat2)

  d = QgsDistanceArea()
  d.setEllipsoid('WGS84')

  #Measure the distance
  distance = d.measureLine([point1, point2])
  return distance/1000
  
def haversine_distance(origin, destination):
  lat1, lon1 = origin
  lat2, lon2 = destination
  radius = 6371 # km
  dlat = math.radians(lat2-lat1)
  dlon = math.radians(lon2-lon1)
  a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
    * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
  c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
  distance = radius * c
  return distance
  
origin = 12.98, 77.58 # Bangalore
destination = 12.30, 76.64 # Mysore

d1 = haversine_distance(origin, destination)
d2 = ellipsoid_distance(origin, destination)

print('Haversine distance: {} km'.format(d1))
print('Ellipsoid distance: {} km'.format(d2))
