This notebook shows how to use the PyQGIS API from a Jupyter Notebook.

For the best experience, this notebook should be run from a Conda environment with QGIS installed. See our guide to [Install QGIS via Conda](https://courses.spatialthoughts.com/install-qgis-ltr.html#install-qgis-via-conda). Once installed, you can launch Jupyter Lab from the environment and can use the PyQGIS API after the following initialization steps.

If you want to run this in another Python environment, you need to ensure the environment variables are correctly configured before starting the Jupyter Notebook. See the [Windows](https://courses.spatialthoughts.com/pyqgis-masterclass.html#windows-configuration) and [MacOS](https://courses.spatialthoughts.com/pyqgis-masterclass.html#macos-configuration) and [Linux](https://courses.spatialthoughts.com/pyqgis-masterclass.html#linuxconda-configuration) configuration instructions. 

### Initialize QGIS


```python
from qgis.core import QgsApplication

qgs = QgsApplication([], False)
qgs.initQgis()

import processing
from processing.core.Processing import Processing
Processing.initialize()
```

### Use PyQGIS API 

Once the initialization is done, you can use all PyQGIS classes and methods.


```python
from qgis.core import QgsDistanceArea, QgsPointXY

san_francisco = (37.7749, -122.4194)
new_york = (40.661, -73.944)

d = QgsDistanceArea()
d.setEllipsoid('WGS84')


lat1, lon1 = san_francisco
lat2, lon2 = new_york
point1 = QgsPointXY(lon1, lat1)
point2 = QgsPointXY(lon2, lat2)

distance = d.measureLine([point1, point2])
print('Ellipsoid Distance', distance/1000)
```

    Ellipsoid Distance 4145.446977549562


### Exit QGIS


```python
qgs.exitQgis()
```
