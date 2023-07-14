crsToolbar = iface.addToolBar('CRS Toolbar')

label = QLabel('Enter a EPSG Code', parent=projectToolbar)
crsTextBox = QLineEdit('4326', parent=projectToolbar)
crsTextBox.setFixedWidth(80)
button = QPushButton('Go!', parent=projectToolbar)

crsToolbar.addWidget(label)
crsToolbar.addWidget(crsTextBox)
crsToolbar.addWidget(button)


def changeCrs(crsText):
    crsText = int(crsTextBox.text())
    crs = QgsCoordinateReferenceSystem(crsText)
    QgsProject.instance().setCrs(crs)

button.clicked.connect(changeCrs)
