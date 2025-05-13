import os
import inspect
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon
from qgis.core import QgsRasterLayer, QgsProject

plugin_dir = os.path.dirname(__file__)

class BasemapLoaderPlugin:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        icon = os.path.join(os.path.join(plugin_dir, 'logo.png'))
        self.action = QAction(QIcon(icon), 'Load Basemap', self.iface.mainWindow())
        self.iface.addToolBarIcon(self.action)
        self.action.triggered.connect(self.run)
      
    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):
        basemap_url = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
        zmin = 0
        zmax = 19
        crs = 'EPSG:3857'
        
        uri = f'type=xyz&url={basemap_url}&zmax={zmax}&zmin={zmin}$crs={crs}'
        rlayer = QgsRasterLayer(uri, 'OpenStreetMap', 'wms')
        if rlayer.isValid():
            QgsProject.instance().addMapLayer(rlayer)
            self.iface.messageBar().pushSuccess('Success', 'Basemap Layer Loaded')
        else:
            self.iface.messageBar().pushCritical('Error', 'Invalid Basemap Layer')
            
  




