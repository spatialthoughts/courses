layer = iface.activeLayer()

if layer:
    if layer.name() == 'zoning':
        iface.messageBar().pushSuccess('Success', 'You selected the right layer')
    else:
        iface.messageBar().pushCritical('Error', 'Wrong Layer Selected')
else:
    iface.messageBar().pushCritical('Error', 'You must select a layer')