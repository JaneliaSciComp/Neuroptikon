""" A script to demonstrate creating a segmented ring."""

from math import pi, cos, sin

segments = 8    # The number of segments in the ring
segmentSize = 2 * pi / segments

# The segments will be contained by a parent region with no shape of its own.
ring = network.createRegion(name = 'Ring')
display.setVisibleShape(ring, None)
display.setVisiblePosition(ring, (0.0, 0.0, 0.0), fixed = True)
display.setArrangedAxis(ring, None)

regions = {}

# Create each segment.
for i in range(0, segments):
    regions[i] = network.createRegion(parentRegion = ring)
    startAngle = i * segmentSize
    segmentShape = shapes['Ring'](startAngle = startAngle, endAngle = startAngle + segmentSize)
    display.setVisibleShape(regions[i], segmentShape)
    # The segment will have expanded and shifted to fill the bounds of the whole ring.  Recenter and rescale it to line up with the other segments.   
    display.setVisiblePosition(regions[i], (-segmentShape.ringCenter[0], -segmentShape.ringCenter[1], -segmentShape.ringCenter[2]), fixed = True)
    display.setVisibleSize(regions[i], (segmentShape.ringSize, segmentShape.ringSize, 1.0), fixed = True)

# Create some arbitrary other regions to have something to connect to the segments.
regions['A'] = network.createRegion(name = 'A')
display.setVisiblePosition(regions['A'], (-0.2, 0.1, 0.0), fixed = True)
regions['B'] = network.createRegion(name = 'B')
display.setVisiblePosition(regions['B'], (0.2, 0.1, 0.0), fixed = True)
regions['C'] = network.createRegion(name = 'C')
display.setVisiblePosition(regions['C'], (-0.2, -0.1, 0.0), fixed = True)
regions['D'] = network.createRegion(name = 'D')
display.setVisiblePosition(regions['D'], (0.2, -0.1, 0.0), fixed = True)

neuron1 = network.createNeuron()
neuron1.arborize(regions['A'])
neuron1.arborize(regions[2])
neuron1.arborize(regions[4])

neuron2 = network.createNeuron()
neuron2.arborize(regions['B'])
neuron2.arborize(regions[0])

neuron3 = network.createNeuron()
neuron3.arborize(regions['C'])
neuron3.arborize(regions[4])

neuron4 = network.createNeuron()
neuron4.arborize(regions['D'])
neuron4.arborize(regions[7])

display.performLayout()
display.setLabelsFloatOnTop(True)

