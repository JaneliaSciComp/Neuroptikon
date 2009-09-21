'''
A very simple example of neural morphology.

A neuron is created with a single process that branches multiple times to form two separate arbors and synapse onto a second neuron.
'''

neuron1 = network.createNeuron(name = '1')
neuron2 = network.createNeuron(name = '2')
regionA = network.createRegion(name = 'A')
regionB = network.createRegion(name = 'B')

# Create the root of the process.
neurite1 = neuron1.extendNeurite()

# The process first branches to arborize region A.
neurite2 = neurite1.extendNeurite()
neurite2.arborize(regionA, sendsOutput = True)
neurite3 = neurite1.extendNeurite()

# The process then branches again to arborize region B.
neurite4 = neurite3.extendNeurite()
neurite4.arborize(regionB, sendsOutput = True)

# The process branches a final time and synapses on the second neuron.
neurite5 = neurite3.extendNeurite()
neurite5.synapseOn(neuron2)

# By default the morphology of the process is not shown, the arborizations and synapse in the visualization will connect directly to the neuron's soma.
# The 'Show Neurites' scripts exposes the morphology.
execfile('Show Neurites.py')

# Now layout the whole mess and make the flow look better than the defaults.
display.performLayout()
display.setDefaultFlowSpacing(0.02)
display.setDefaultFlowSpeed(0.02)
display.setShowNeuronNames(True)
