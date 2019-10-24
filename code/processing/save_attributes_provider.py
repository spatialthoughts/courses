import os
import inspect
from PyQt5.QtGui import QIcon

from qgis.core import QgsProcessingProvider
from .save_attributes_algorithm import SaveAttributesAlgorithm


class SaveAttributesProvider(QgsProcessingProvider):

    def __init__(self):
        QgsProcessingProvider.__init__(self)

    def unload(self):
        pass

    def loadAlgorithms(self):
        self.addAlgorithm(SaveAttributesAlgorithm())

    def id(self):
        return 'save_attributes'

    def name(self):
        return self.tr('Save Attributes')

    def icon(self):
        cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]
        icon = QIcon(os.path.join(os.path.join(cmd_folder, 'logo.png')))
        return icon

    def longName(self):
        return self.name()

