import os

qgis_dir = QgsApplication.pkgDataPath()
icon_path = os.path.join(qgis_dir, 'svg', 'crosses', 'Cross6.svg')

def show_statistics():

    mc = iface.mapCanvas()
    extent = mc.extent()
    geometry = QgsGeometry.fromRect(extent)

    vlayer = QgsVectorLayer('Polygon?crs=EPSG:4326', 'extent', 'memory')
    provider = vlayer.dataProvider()

    f = QgsFeature()
    f.setGeometry(geometry)
    provider.addFeature(f)
    vlayer.updateExtents() 

    srtm = QgsProject.instance().mapLayersByName('srtm')[0]

    results = processing.run("native:zonalstatisticsfb", {
      'INPUT': vlayer,
      'INPUT_RASTER': srtm,
      'RASTER_BAND':1,
      'COLUMN_PREFIX':'elevation_',
      'STATISTICS':[2],
      'OUTPUT':'TEMPORARY_OUTPUT'})

    stats_layer = results['OUTPUT']

    features = stats_layer.getFeatures()
    feature = next(features)
    elevation = feature.attributes()[0]
    if elevation:
      iface.messageBar().pushInfo(
        'Processing done', f'Average Elevation in Extent {elevation:.2f}m')
    else:
      iface.messageBar().pushCritical(
        'Error', 'No pixels in current extent')

action = QAction('Show Raster Statistics')
action.triggered.connect(show_statistics)
action.setIcon(QIcon(icon_path))
iface.addToolBarIcon(action)