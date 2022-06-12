@echo off 

set OSGEO4W_ROOT=C:\OSGeo4W64
 
call "%OSGEO4W_ROOT%\bin\o4w_env.bat" 
call "%OSGEO4W_ROOT%\bin\qt5_env.bat" 
call "%OSGEO4W_ROOT%\bin\py3_env.bat" 
 
set PATH=%OSGEO4W_ROOT%\bin;%OSGEO4W_ROOT%\apps\qgis-ltr\bin;C:\OSGeo4W64\apps\Qt5\bin;%PATH%
set PYTHONPATH=%OSGEO4W_ROOT%\apps\qgis-ltr\python;%OSGEO4W_ROOT%\apps\qgis-ltr\python\plugins;%PYTHONPATH%
set QGIS_PREFIX_PATH=%OSGEO4W_ROOT%\apps\qgis-ltr
set QT_QPA_PLATFORM_PLUGIN_PATH=%OSGEO4W_ROOT%\apps\Qt5\plugins

python3 save_attributes_standalone.py

