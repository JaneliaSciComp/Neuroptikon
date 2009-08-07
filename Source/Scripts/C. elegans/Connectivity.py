display.setViewDimensions(3)
display.setShowNeuronNames(True)
display.setUseGhosts(True)
display.setDefaultFlowColor((1.0, 1.0, 1.0))
display.setDefaultFlowSpread(0.5)

# Load the base network.
if not any(network.neurons()):
    execfile('Neurons.py')

# Remove the muscles if they were added by another script.
for muscle in network.muscles():
    display.removeVisualization(muscle)

# Set up the visualization

for neuron in display.network.neurons():
    red = green = blue = 0.5
    if neuron.hasFunction(NeuralFunction.SENSORY):
        red = 1.0
    if neuron.hasFunction(NeuralFunction.INTERNEURON):
        blue = 1.0
    if neuron.hasFunction(NeuralFunction.MOTOR):
        green = 1.0
    display.setVisibleColor(neuron, (red, green, blue))
    display.setLabelColor(neuron, (red * 0.125, green * 0.125, blue * 0.125))
    display.setVisiblePosition(neuron, fixed = True)

for synapse in display.network.synapses():
    display.setVisibleColor(synapse, (0.75, 0.75, 0.75))

for gapJunction in display.network.gapJunctions():
    display.setVisibleColor(gapJunction, (0.0, 0.75, 0.0))

def weightByCount(edgeVisible):
    countAttr = edgeVisible.client.getAttribute('Count')
    return 0 if not countAttr else countAttr.value

display.performLayout(layouts['SpectralLayout'](weightFunction = weightByCount, scaling = (-40.0, 12.5, 0.25)))
