@echo off 

:: If you get an error, check if the folder below exists.
set OSGEO4W_ROOT=C:\OSGeo4W
 
call "%OSGEO4W_ROOT%\bin\o4w_env.bat" 

:: If you are not using QGIS LTR version, change qgis-ltr to qgis in all lines below
set PATH=%OSGEO4W_ROOT%\bin;%OSGEO4W_ROOT%\apps\qgis-ltr\bin;C:\OSGeo4W64\apps\Qt5\bin;%PATH%
set PYTHONPATH=%OSGEO4W_ROOT%\apps\qgis-ltr\python;%OSGEO4W_ROOT%\apps\qgis-ltr\python\plugins;%PYTHONPATH%
set QGIS_PREFIX_PATH=%OSGEO4W_ROOT%\apps\qgis-ltr
set QT_QPA_PLATFORM_PLUGIN_PATH=%OSGEO4W_ROOT%\apps\Qt5\plugins

for /f %%i in ('where python3') do set current_python=%%i
echo Using python3 from %current_python%

python3 zonal_stats.py
