import os
import sys
import inspect
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon

cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]

class SaveAttributesPlugin:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
      icon = os.path.join(os.path.join(cmd_folder, 'logo.png'))
      self.action = QAction(QIcon(icon), 'Save Attributes as CSV', self.iface.mainWindow())
      self.action.triggered.connect(self.run)
      self.iface.addPluginToMenu('&Save Attributes', self.action)
      self.iface.addToolBarIcon(self.action)

    def unload(self):
      self.iface.removeToolBarIcon(self.action)
      self.iface.removePluginMenu('&SaveAttributes', self.action)  
      del self.action

    def run(self):
      self.iface.messageBar().pushMessage('Hello from Plugin')

