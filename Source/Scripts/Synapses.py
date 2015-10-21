#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

"""
This script creates a simple network that includes each type of network component. 
"""

regionA = network.createRegion(name = 'A')
regionB = network.createRegion(name = 'B')

neuron1 = network.createNeuron(name = '1', neurotransmitters = [library.neurotransmitter('GABA')], functions = [Neuron.Function.SENSORY], activation = 'excitatory')
neuron1.arborize(regionA, True, False)
neuron1.arborize(regionB, True, False)

neuron2 = network.createNeuron(name = '2', functions = [Neuron.Function.SENSORY])
neuron2.arborize(regionA, True, False)
neuron2.arborize(regionB, True, False)

neuron1.synapseOn(neuron2, preSynapticRegion=regionA, postSynapticRegion=regionB)

neuron2.synapseOn(neuron1)

neuron3 = network.createNeuron(name = '3', functions = [Neuron.Function.INTERNEURON])
neuron3.arborize(regionA)
neuron3.arborize(regionB)

neuron1.synapseOn(neuron3)

neuron4 = network.createNeuron(name = '4', neurotransmitters = [library.neurotransmitter('ACh')], functions = [Neuron.Function.MOTOR])
neuron4.arborize(regionA, False, True)
neuron4.arborize(regionB, False, True)

neuron1.synapseOn(neuron4)

neuron5 = network.createNeuron(name = '5', neurotransmitters = [library.neurotransmitter('ACh')], functions = [Neuron.Function.MOTOR])
neuron5.arborize(regionA, False, True)
neuron5.arborize(regionB, False, True)

neuron2.synapseOn(neuron5)

display.performLayout()
