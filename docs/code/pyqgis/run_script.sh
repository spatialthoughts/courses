export PYQGIS_STARTUP=/Applications/QGIS3.10.app/Contents/Resources/python/pyqgis-startup.py
export PYTHONHOME=/Applications/QGIS3.10.app/Contents/Frameworks/Python.framework/Versions/Current
export PYTHONPATH=/Applications/QGIS3.10.app/Contents/Resources/python:${PYTHONPATH}
export QGIS_PREFIX_PATH=/Applications/QGIS3.10.app/Contents/MacOS
export GDAL_DRIVER_PATH=/Applications/QGIS3.10.app/Contents/Resources/gdal/gdalplugins
export GDAL_DATA=/Applications/QGIS3.10.app/Contents/Resources/gdal
export QT_QPA_PLATFORM_PLUGIN_PATH=/Applications/QGIS3.10.app/Contents/Plugins

python3 save_attributes_standalone.py