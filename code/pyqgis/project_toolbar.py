import os
data_dir = os.path.join(os.path.expanduser('~'), 'Downloads', 'pyqgis_in_a_day')

projectToolbar = iface.addToolBar('Project Selector')

label = QLabel('Select a project to load', parent=projectToolbar)
projectSelector = QComboBox(parent=projectToolbar)
projectSelector.addItem('sf.qgz')
projectSelector.addItem('places.qgz')
projectSelector.setCurrentIndex(-1)

def loadProject(projectName):
    project = QgsProject.instance()
    project_path = os.path.join(data_dir, projectName)
    project.read(project_path)

projectSelector.currentTextChanged.connect(loadProject)
projectToolbar.addWidget(label)
projectToolbar.addWidget(projectSelector)
