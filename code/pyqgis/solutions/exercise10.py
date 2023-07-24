layer_id = '[%@layer_id%]'
fid = [% $id %]

layer = QgsProject.instance().mapLayer(layer_id)

def get_neighbors(fid):
    f = layer.getFeature(fid)
    # Use list comprehension to get all intersecting features
    # You may also use touches() if your data is topologically correct
    # Supply the bounding box to getFeatures() to use Spatial Index
    neighbors = [
        c.id()
        for c in layer.getFeatures(f.geometry().boundingBox())
        if c.geometry().intersects(f.geometry()) and c.id() != f.id()
    ]
    return neighbors


first_degree_neighbors = get_neighbors(fid)

second_degree_neighbors = set()

for n in first_degree_neighbors:
    neighbors = get_neighbors(n)
    second_degree_neighbors.update(neighbors)

# Remove all first-degree neighbors from the set
second_degree_neighbors = second_degree_neighbors.difference(
    set(first_degree_neighbors))
    
# Remove the feature itself from the set if it exists
second_degree_neighbors.discard(fid)

# Apply the selection
layer.selectByIds(list(second_degree_neighbors), QgsVectorLayer.AddToSelection)