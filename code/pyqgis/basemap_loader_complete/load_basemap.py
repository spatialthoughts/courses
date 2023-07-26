import os
import inspect
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon
from qgis.core import QgsRasterLayer, QgsProject

cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]

class BasemapLoaderPlugin:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        icon = os.path.join(os.path.join(cmd_folder, 'logo.png'))
        self.action = QAction(QIcon(icon), 'Load Basemap', self.iface.mainWindow())
        self.iface.addToolBarIcon(self.action)
        self.action.triggered.connect(self.run)
      
    def unload(self):
        del self.action

    def run(self):
        basemap_url = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
        uri = f'type=xyz&url={basemap_url}&zmax=19&zmin=0$crs=EPSG:3857'
        rlayer = QgsRasterLayer(uri, 'OpenStreetMap', 'wms')
        if rlayer.isValid():
            QgsProject.instance().addMapLayer(rlayer)
            self.iface.messageBar().pushSuccess('Success', 'Basemap Layer Loaded')
        else:
            self.iface.messageBar().pushCritical('Error', 'Invalid Basemap Layer')
            
  




