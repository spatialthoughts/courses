import os

from PyQt5 import uic
from PyQt5 import QtWidgets

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'save_attributes_dialog.ui'))


class SaveAttributesDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(SaveAttributesDialog, self).__init__(parent)
        self.setupUi(self)
