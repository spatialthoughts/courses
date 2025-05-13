import os
import sys
import inspect
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon

from qgis.core import QgsProcessingAlgorithm, QgsApplication
import processing
from .save_attributes_provider import SaveAttributesProvider


plugin_dir = os.path.dirname(__file__)

class SaveAttributesPlugin:
    def __init__(self, iface):
        self.iface = iface

    def initProcessing(self):
      self.provider = SaveAttributesProvider()
      QgsApplication.processingRegistry().addProvider(self.provider)
        
    def initGui(self):
      self.initProcessing()
      icon = os.path.join(os.path.join(plugin_dir, 'logo.png'))
      self.action = QAction(QIcon(icon), 'Save Attributes as CSV', self.iface.mainWindow())
      self.action.triggered.connect(self.run)
      self.iface.addPluginToMenu('&Save Attributes', self.action)
      self.iface.addToolBarIcon(self.action)

    def unload(self):
      QgsApplication.processingRegistry().removeProvider(self.provider)
      self.iface.removeToolBarIcon(self.action)
      self.iface.removePluginMenu('&Save Attributes', self.action)  
      del self.action

    def run(self):
      processing.execAlgorithmDialog('save_attributes:save_attributes')

