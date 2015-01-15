#  Copyright (c) 2015 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

"""
This script creates a region and a neurons to demonstrate how the links work with neurons.
"""

regionA = network.createRegion(name = 'reg1')
neuron1 = network.createNeuron(name = 'neu1', links=['http://github.com/JaneliaSciComp/Neuroptikon', 'http://github.com/JaneliaSciComp/Neuroptikon/wiki'])
neuron1.arborize(regionA, True, False)

neuron2 = network.createNeuron(name = 'neu2')
neuron2.arborize(regionA, True, True)
