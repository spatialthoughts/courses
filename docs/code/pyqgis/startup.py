from qgis.utils import iface
from qgis.core import QgsExpressionContextUtils

def customize():
	version = QgsExpressionContextUtils.globalScope().variable('qgis_version')
	title = iface.mainWindow().windowTitle()
	iface.mainWindow().setWindowTitle(f'{title} | {version}')


iface.initializationCompleted.connect(customize)

