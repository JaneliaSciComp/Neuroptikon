""" A script to demonstrate using ring segments in visualizations."""

from math import pi


def createSegmentedRing(segmentCount = 8, offsetAngle = 0.0, **keywordArgs):
    """
    Create a segmented ring composed of segmentCount regions and an invisible container region.
    
    Returns the new container region.
    """
    
    # Create the containing region.
    ring = network.createRegion(**keywordArgs)
    display.setVisibleShape(ring, None)
    display.setArrangedAxis(ring, None)
    
    # Create each segment.
    segmentSize = 2.0 * pi / segmentCount
    for i in range(0, segmentCount):
        segment = network.createRegion(parentRegion = ring)
        startAngle = offsetAngle + i * segmentSize
        segmentShape = shapes['Ring'](startAngle = startAngle, endAngle = startAngle + segmentSize)
        display.setVisibleShape(segment, segmentShape)
        # The segment will have expanded and shifted to fill the bounds of the whole ring.  Recenter and rescale it to line up with the other segments.   
        display.setVisiblePosition(segment, (-segmentShape.ringCenter[0], -segmentShape.ringCenter[1], -segmentShape.ringCenter[2]), fixed = True)
        display.setVisibleSize(segment, (segmentShape.ringSize, segmentShape.ringSize, segmentShape.ringSize), fixed = True)
    
    return ring


# Create the central segmented ring
ring = createSegmentedRing(name = 'Ring')
display.setVisiblePosition(ring, (0.0, 0.0, 0.0), fixed = True)
display.setVisibleSize(ring, (0.1, 0.1, 0.03), fixed = True)

# Create some other regions to have something to connect to the segments.
regionA = network.createRegion(name = 'A')
display.setVisiblePosition(regionA, (-0.2, 0.1, 0.0), fixed = True)
display.setVisibleSize(regionA, (0.1, 0.1, 0.03), fixed = True)
display.setVisibleShape(regionA, shapes['Ring'](startAngle = -pi / 2.0, endAngle = 0.0))
regionB = network.createRegion(name = 'B')
display.setVisiblePosition(regionB, (0.2, 0.1, 0.0), fixed = True)
display.setVisibleSize(regionB, (0.1, 0.1, 0.03), fixed = True)
display.setVisibleShape(regionB, shapes['Ring'](startAngle = pi, endAngle = 3.0 * pi / 2.0))
regionC = network.createRegion(name = 'C')
display.setVisiblePosition(regionC, (-0.2, -0.1, 0.0), fixed = True)
display.setVisibleSize(regionC, (0.1, 0.1, 0.03), fixed = True)
display.setVisibleShape(regionC, shapes['Ring'](startAngle = 0.0, endAngle = pi / 2.0))
regionD = network.createRegion(name = 'D')
display.setVisiblePosition(regionD, (0.2, -0.1, 0.0), fixed = True)
display.setVisibleSize(regionD, (0.1, 0.1, 0.03), fixed = True)
display.setVisibleShape(regionD, shapes['Ring'](startAngle = pi / 2.0, endAngle = pi))

# Create the connections
neuron1 = network.createNeuron()
neuron1.arborize(regionA)
neuron1.arborize(ring.subRegions[2])
neuron1.arborize(ring.subRegions[4])
neuron2 = network.createNeuron()
neuron2.arborize(regionB)
neuron2.arborize(ring.subRegions[0])
neuron3 = network.createNeuron()
neuron3.arborize(regionC)
neuron3.arborize(ring.subRegions[4])
neuron4 = network.createNeuron()
neuron4.arborize(regionD)
neuron4.arborize(ring.subRegions[7])

display.performLayout()
display.setLabelsFloatOnTop(True)

