import os
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsRasterLayer, QgsProject, QgsCoordinateReferenceSystem

plugin_dir = os.path.dirname(__file__)

class BasemapLoaderPlugin:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        # Create an action (i.e. a button) with Logo
        icon = os.path.join(os.path.join(plugin_dir, 'logo.png'))
        self.action = QAction(QIcon(icon), 'Load Basemap', self.iface.mainWindow())
        # Add the action to the toolbar
        self.iface.addToolBarIcon(self.action)
        # Connect the run() method to the action
        self.action.triggered.connect(self.run)
      
    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):
        basemap_url = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
        zmin = 0
        zmax = 19
        crs = 'EPSG:3857'
        
        # Replace '=' and '&' in the URL to ensure it is properly encoded
        encoded_url = basemap_url.replace('=', '%3D').replace('&', '%26')
        uri = f'type=xyz&url={encoded_url}&zmax={zmax}&zmin={zmin}$crs={crs}'
        
        # Create a QgsRasterLayer with the URI
        rlayer = QgsRasterLayer(uri, 'OpenStreetMap', 'wms')
        if rlayer.isValid():
            QgsProject.instance().addMapLayer(rlayer)
            self.iface.messageBar().pushSuccess('Success', 'Basemap Layer Loaded')
        else:
            self.iface.messageBar().pushCritical('Error', 'Invalid Basemap Layer')
            
