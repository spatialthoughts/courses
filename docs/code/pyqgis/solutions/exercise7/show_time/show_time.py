import os
import sys
import inspect
from datetime import datetime
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon

cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]

class ShowTimePlugin:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
      icon = os.path.join(os.path.join(cmd_folder, 'logo.svg'))
      self.action = QAction(QIcon(icon), 'Show Time', self.iface.mainWindow())
      self.action.triggered.connect(self.run)
      self.iface.addPluginToMenu('&Show Time', self.action)
      self.iface.addToolBarIcon(self.action)

    def unload(self):
      self.iface.removeToolBarIcon(self.action)
      self.iface.removePluginMenu('&Show Time', self.action)  
      del self.action

    def run(self):
      now = datetime.now()
      current_time = now.strftime("%H:%M:%S")
      self.iface.messageBar().pushMessage('Time is {}'.format(current_time))