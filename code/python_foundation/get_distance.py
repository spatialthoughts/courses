from geopy import distance

san_francisco = (37.7749, -122.4194)
new_york = (40.661, -73.944)

ellipsoid_distance = distance.geodesic(san_francisco, new_york, ellipsoid='WGS-84').km

print('Source Coordinates: {},{}'.format(san_francisco[0], san_francisco[1]))
print('Destination Coordinates: {},{}'.format(san_francisco[0], san_francisco[1]))
print('Ellipsoid Distance: {} km'.format(ellipsoid_distance))
