#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

"""
This script demonstrates creating an arbitrary network.
"""


count = 8
neurons = {}
for i in range(count):
    neurons[i] = network.createNeuron(name = str(i))
for i in range(count):
    for j in range(count):
        if i < j:
            neurons[i].synapseOn(neurons[j])

display.autoLayout()
