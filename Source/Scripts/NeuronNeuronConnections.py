#  Copyright (c) 2015 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

"""
This script creates a cycle of connected neurons. 
"""

# Create 5 neurons
neuron1 = network.createNeuron(name = '1', neurotransmitters = [library.neurotransmitter('GABA')], functions = [Neuron.Function.SENSORY])
neuron2 = network.createNeuron(name = '2', functions = [Neuron.Function.SENSORY])
neuron3 = network.createNeuron(name = '3', functions = [Neuron.Function.INTERNEURON])
neuron4 = network.createNeuron(name = '4', neurotransmitters = [library.neurotransmitter('ACh')], functions = [Neuron.Function.MOTOR])
neuron5 = network.createNeuron(name = '5', neurotransmitters = [library.neurotransmitter('ACh')], functions = [Neuron.Function.MOTOR])

# Create neuron-neuron connections (synapses)
synapse1_2 = neuron1.synapseOn(neuron2)
synapse2_3 = neuron2.synapseOn(neuron3)
synapse3_4 = neuron3.synapseOn(neuron4)
synapse4_5 = neuron4.synapseOn(neuron5)
synapse5_1 = neuron5.synapseOn(neuron1)

# Set one of the synapses to be green.
green = (0.5,1.0,0.5)
display.setVisibleColor(synapse5_1, green)

display.performLayout()
