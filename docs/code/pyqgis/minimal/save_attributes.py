import os
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon

plugin_dir = os.path.dirname(__file__)

class SaveAttributesPlugin:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
      icon = os.path.join(os.path.join(plugin_dir, 'logo.png'))
      self.action = QAction(QIcon(icon), 'Save Attributes as CSV', self.iface.mainWindow())
      self.action.triggered.connect(self.run)
      self.iface.addPluginToMenu('&Save Attributes', self.action)
      self.iface.addToolBarIcon(self.action)

    def unload(self):
      self.iface.removeToolBarIcon(self.action)
      self.iface.removePluginMenu('&Save Attributes', self.action)  
      del self.action

    def run(self):
      self.iface.messageBar().pushMessage('Hello from Plugin')

