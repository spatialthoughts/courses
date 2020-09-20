import requests
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtWebKitWidgets import QWebView
from qgis.utils import iface

parameters = {
    'client_id': '<REPLACE WITH YOUR CLIENT_ID>',
    'closeto': '{},{}'.format([%$x%],[%$y%]),
    'per_page': 1,
    'radius': 1000 
}
response = requests.get(
        'https://a.mapillary.com/v3/images', params=parameters)

if response.status_code == 200:
    data = response.json()
    if data['features']:
        key = data['features'][0]['properties']['key']
        url = 'https://images.mapillary.com/{}/thumb-640.jpg'.format(key)
        myWV = QWebView(None)
        myWV.load(QUrl(url))
        myWV.show()
    else:
        iface.messageBar().pushMessage('No images found')
