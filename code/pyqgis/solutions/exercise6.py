layer = iface.activeLayer()
field_names = [field.name() for field in layer.fields()]

print(field_names)