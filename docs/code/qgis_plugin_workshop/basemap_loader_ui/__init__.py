from .main import BasemapLoaderPlugin

def classFactory(iface):
    return BasemapLoaderPlugin(iface)
