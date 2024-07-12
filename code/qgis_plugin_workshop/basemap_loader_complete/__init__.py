from .load_basemap import BasemapLoaderPlugin

def classFactory(iface):
    return BasemapLoaderPlugin(iface)