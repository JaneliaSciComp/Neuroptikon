""" This script demonstrates creating a simple visualization without anything in the biological layer. """

nodes = {}
for i in range(10):
    nodes[i] = display.visualizeObject(None)

for i in range(1):
    for j in range(2):
        if i != j:
            edge = display.visualizeObject(None, shape = shapes['Line']())
            edge.setPathEndPoints(nodes[i], nodes[j])
            edge.setFlowTo(True)

display.performLayout(layouts['ForceDirectedLayout'])
