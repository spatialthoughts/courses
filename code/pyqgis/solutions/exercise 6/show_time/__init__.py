from .show_time import ShowTimePlugin

def classFactory(iface):
    return ShowTimePlugin(iface)