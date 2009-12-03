'''
Load an SWC neural morphology file from www.neuromorpho.org.

You can load your own file by changing the open() call on line 9. 
'''

compartments = {}
branchPoints = {}
swcFile = open('g0762_b.CNG.swc')
for line in swcFile:
    if line[0] != '#':
        fields = line.split()
        compID = int(fields[0])
        compType = int(fields[1])
        x = float(fields[2])
        y = float(fields[3])
        z = float(fields[4])
        radius = float(fields[5])
        parentID = int(fields[6])
        if compID == 1:
            # Create the soma
            compartments[1] = network.createNeuron()
            branchPoints[1] = display.visiblesForObject(compartments[1])[0]
            branchPoints[1].setSize([radius * 1.0] * 3)
            branchPoints[1].setColor((1.0, 1.0, 1.0))
        else:
            # Create a neurite
            compartments[compID] = compartments[parentID].extendNeurite()
            branchPoints[compID] = display.visualizeObject(None, opacity = 0.0, position = (x, y, z), size = (0.005, 0.005, 0.005))
            viz = display.visualizeObject(compartments[compID], shape = shapes['Cylinder'], weight = radius * 10000.0, textureScale = 100.0)
            viz.setPathEndPoints(branchPoints[parentID], branchPoints[compID])
            if compType == 1:   # soma
                branchPoints[1].setColor((1.0, 1.0, 1.0))
            elif compType == 2:   # axon
                viz.setColor((0.5, 0.5, 0.5))
                viz.setFlowTo(True)
                viz.setFlowToColor((0.25, 0.25, 0.25))
            elif compType == 3: # basal dendrite
                viz.setColor((0.0, 1.0, 0.0))
                viz.setFlowFrom(True)
                viz.setFlowFromColor((0.0, 0.5, 0.0))
            elif compType == 4: # apical dendrite
                viz.setColor((1.0, 0.0, 1.0))
                viz.setFlowFrom(True)
                viz.setFlowFromColor((0.5, 0.0, 0.5))
swcFile.close()

display.setViewDimensions(3)
display.resetView()

# Make the flow look better than the defaults.
sizes = display.visiblesSize
avgSize = sum(sizes) / len(sizes)
display.setDefaultFlowSpacing(avgSize / 100.0)
display.setDefaultFlowSpeed(avgSize / 100.0)
display.setDefaultFlowSpread(0.2)
display.setShowFlow(True)
