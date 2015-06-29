#  Copyright (c) 2015 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

"""
This script creates a cycle of connected neurons. 
"""


neuron1 = network.createNeuron(name = '1', neurotransmitters = [library.neurotransmitter('GABA')], functions = [Neuron.Function.SENSORY])
neuron2 = network.createNeuron(name = '2', functions = [Neuron.Function.SENSORY])
neuron3 = network.createNeuron(name = '3', functions = [Neuron.Function.INTERNEURON])
neuron4 = network.createNeuron(name = '4', neurotransmitters = [library.neurotransmitter('ACh')], functions = [Neuron.Function.MOTOR])
neuron5 = network.createNeuron(name = '5', neurotransmitters = [library.neurotransmitter('ACh')], functions = [Neuron.Function.MOTOR])

neuron1.synapseOn(neuron2)
neuron2.synapseOn(neuron3)
neuron3.synapseOn(neuron4)
neuron4.synapseOn(neuron5)
neuron5.synapseOn(neuron1)

display.performLayout()
