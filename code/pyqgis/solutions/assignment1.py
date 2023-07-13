import os
import math

qgis_dir = QgsApplication.prefixPath()
icon_path = os.path.join(qgis_dir, 'svg', 'crosses', 'Cross2.svg')

def show_statistics():
    layer = iface.activeLayer()
    # Check if a layer is selected
    if not layer:
        iface.messageBar().pushMessage('Please select a layer',  level=Qgis.Critical) 
        return None
    # Check if the selected layer is a raster layer
    if layer.type() != QgsMapLayer.RasterLayer:
        iface.messageBar().pushMessage('Please select a raster layer',  level=Qgis.Critical)
        return None
        
    # Get the canvas extent
    mc = iface.mapCanvas()
    extent = mc.extent()
    provider = layer.dataProvider()

    # Get the raster statistics of band 1
    stats = provider.bandStatistics(1, QgsRasterBandStats.All, extent)

    # Get the average value
    mean = stats.mean

    # The value is NaN if there are no valid pixels in the extent
    if not math.isnan(mean):
        iface.messageBar().pushInfo(
            'Average Value of Band 1 in Extent', f'{mean:.2f}')
    else:
        iface.messageBar().pushCritical(
        'Error', 'No pixels in current extent')
      
action = QAction('Show Raster Statistics')
action.triggered.connect(show_statistics)
action.setIcon(QIcon(icon_path))
iface.addToolBarIcon(action)
