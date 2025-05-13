import os
import inspect
from PyQt5.QtGui import QIcon

from qgis.core import QgsProcessingProvider
from .save_attributes_algorithm import SaveAttributesAlgorithm

plugin_dir = os.path.dirname(__file__)

class SaveAttributesProvider(QgsProcessingProvider):

    def __init__(self):
        QgsProcessingProvider.__init__(self)

    def unload(self):
        QgsProcessingProvider.unload(self)

    def loadAlgorithms(self):
        self.addAlgorithm(SaveAttributesAlgorithm())

    def id(self):
        return 'save_attributes'

    def name(self):
        return self.tr('Save Attributes')

    def icon(self):
        icon = QIcon(os.path.join(os.path.join(plugin_dir, 'logo.png')))
        return icon

    def longName(self):
        return self.name()

