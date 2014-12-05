#  Copyright (c) 2014 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

"""
This script creates a region and 2 neuron to demonstrate how the neuron image field works.
"""

regionA = network.createRegion(name = 'A')
neuron1 = network.createNeuron(name = '1', neuronImage='../Images/Neurite.png')
neuron1.arborize(regionA, True, False)

neuron1 = network.createNeuron(name = '2', neuronImage='../Images/Neuron.png')
neuron1.arborize(regionA, True, False)
display.performLayout()