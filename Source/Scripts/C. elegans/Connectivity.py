display.setViewDimensions(3)
display.setShowNeuronNames(True)
display.setUseGhosts(True)
display.setDefaultFlowColor((1.0, 1.0, 1.0))
display.setDefaultFlowSpread(0.5)

# Load the base network.
if not any(network.neurons()):
    execfile('Neurons.py')

# Set up the visualization

for neuron in display.network.neurons():
    red = green = blue = 0.0
    if neuron.hasFunction(NeuralFunction.SENSORY):
        red = 1.0
    if neuron.hasFunction(NeuralFunction.INTERNEURON):
        blue = 1.0
    if neuron.hasFunction(NeuralFunction.MOTOR):
        green = 1.0
    display.setVisibleColor(neuron, (red, green, blue))
    display.setVisiblePosition(neuron, fixed = True)

for synapse in display.network.synapses():
    display.setVisibleColor(synapse, (0.75, 0.75, 0.75))

for gapJunction in display.network.gapJunctions():
    display.setVisibleColor(gapJunction, (0.0, 0.75, 0.0))
#    display.setVisibleFlowTo(gapJunction, color = (0.0, 0.0, 0.0))
#    display.setVisibleFlowFrom(gapJunction, color = (0.0, 0.0, 0.0))

def weightByCount(edgeVisible):
    countAttr = edgeVisible.client.getAttribute('Count')
    return 0 if not countAttr else countAttr.value

display.performLayout(layouts['SpectralLayout'](weightFunction = weightByCount, scaling = (-40.0, 12.5, 0.25)))
