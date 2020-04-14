from qgis.core import *
from qgis.gui import *

@qgsfunction(args='auto', group='Custom')
def unique_values(value, feature, parent):
    list = value.split(',')
    unique_list = set(list)
    result = ','.join(unique_list)
    return result