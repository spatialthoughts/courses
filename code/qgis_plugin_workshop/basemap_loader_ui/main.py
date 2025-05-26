import os
from PyQt5.QtWidgets import QAction, QComboBox, QLabel, QPushButton
from PyQt5.QtGui import QIcon
from qgis.core import QgsRasterLayer, QgsProject, QgsCoordinateReferenceSystem

plugin_dir = os.path.dirname(__file__)

# We create a dictionary of all the basemaps and their URLs to be used
osm = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
cartodb_darkmatter = 'https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png'
cartodb_positron = 'https://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png'
esri_shaded_relief = 'https://server.arcgisonline.com/ArcGIS/rest/services/' \
    'World_Street_Map/MapServer/tile/{z}/{y}/{x}' 

BASEMAPS = {
    'OpenStreetMap': osm,
    'CartoDB DarkMatter': cartodb_darkmatter,
    'CartoDB Positron': cartodb_positron,
    'Esri World Shaded Relief': esri_shaded_relief
}

class BasemapLoaderPlugin:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        # Create a Toolbar
        self.basemapToolbar = self.iface.addToolBar('Basemap Selector')
        
        # Create an action with Logo
        icon = os.path.join(os.path.join(plugin_dir, 'logo.png'))
        self.action = QAction(QIcon(icon), 'Load Basemap', self.basemapToolbar)
        
        # Create a label
        self.label = QLabel('Select a basemap', parent=self.basemapToolbar)

        # Create a dropdown menu
        self.basemapSelector = QComboBox(parent=self.basemapToolbar)
        self.basemapSelector.setFixedWidth(150)
        # Populate it with names of all the basemaps
        for basemap_name in BASEMAPS.keys():
            self.basemapSelector.addItem(basemap_name)
            
        # Add all the widgets to the toolbar
        self.basemapToolbar.addWidget(self.label)
        self.basemapToolbar.addWidget(self.basemapSelector)
        self.basemapToolbar.addAction(self.action)
      
        # Connect the run() method to the action
        self.action.triggered.connect(self.run)
      
    def unload(self):
        del self.basemapToolbar

    def run(self):
        selected_basemap = self.basemapSelector.currentText()
        basemap_url = BASEMAPS[selected_basemap]
        zmin = 0
        zmax = 19
        crs = 'EPSG:3857'
        
        # Replace '=' and '&' in the URL to ensure it is properly encoded
        encoded_url = basemap_url.replace('=', '%3D').replace('&', '%26')
        uri = f'type=xyz&url={encoded_url}&zmax={zmax}&zmin={zmin}$crs={crs}'

        # Create a QgsRasterLayer with the constructed URI
        rlayer = QgsRasterLayer(uri, selected_basemap, 'wms')
        if rlayer.isValid():
            QgsProject.instance().addMapLayer(rlayer)
            self.iface.messageBar().pushSuccess('Success', 'Basemap Layer Loaded')
        else:
            self.iface.messageBar().pushCritical('Error', 'Invalid Basemap Layer')
            
