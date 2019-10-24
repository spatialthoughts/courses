from .save_attributes import SaveAttributesPlugin

def classFactory(iface):
    return SaveAttributesPlugin(iface)


