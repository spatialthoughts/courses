import math
from qgis.core import *
from qgis.gui import *

@qgsfunction(args=0, group='Custom', usesgeometry=True)
def GetUtmZone(value1, feature, parent):
    """Return the UTM Zone of the feature's geometry as a String"""
    centroid = feature.geometry()
    longitude = centroid.asPoint().x()
    latitude = centroid.asPoint().y()
    zone_number = math.floor(((longitude + 180) / 6) % 60) + 1

    if latitude >= 0:
        zone_letter = 'N'
    else:
        zone_letter = 'S'

    return '%d%s' % (int(zone_number), zone_letter)
