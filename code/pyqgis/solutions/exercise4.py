crsToolbar = iface.addToolBar('CRS Toolbar')

label = QLabel('Enter an EPSG Code', parent=projectToolbar)
crsTextBox = QLineEdit('4326', parent=projectToolbar)
crsTextBox.setFixedWidth(80)
button = QPushButton('Go!', parent=projectToolbar)

crsToolbar.addWidget(label)
crsToolbar.addWidget(crsTextBox)
crsToolbar.addWidget(button)


def changeCrs(crsText):
    currentCrs = QgsProject.instance().crs()
    currentCrsCode = currentCrs.authid()
    epsgCode = int(crsTextBox.text())
    crs = QgsCoordinateReferenceSystem(epsgCode)
    newCrsCode = f'EPSG:{epsgCode}'
    if newCrsCode == currentCrsCode:
        iface.messageBar().pushInfo(
        'No Change Applied', f'Project already set to {newCrsCode}')
    else:
        QgsProject.instance().setCrs(crs)
        iface.messageBar().pushInfo(
        'Project CRS Changed', newCrsCode)


button.clicked.connect(changeCrs)