import os, os.path

display.setViewDimensions(3)
display.setShowNeuronNames(True)
display.setUseGhosts(True)

execfile(os.path.dirname(__file__) + os.sep + 'C. elegans.py')

for neuron in display.network.neurons():
	red = green = blue = 0.0
	if neuron.hasFunction(NeuralFunction.SENSORY):
		red = 1.0
	if neuron.hasFunction(NeuralFunction.INTERNEURON):
		blue = 1.0
	if neuron.hasFunction(NeuralFunction.MOTOR):
		green = 1.0
	display.setVisibleColor(neuron, (red, green, blue))

for synapse in display.network.synapses():
	display.setVisibleColor(synapse, (0.75, 0.75, 0.75))

for gapJunction in display.network.gapJunctions():
	display.setVisibleColor(gapJunction, (0.75, 0.75, 0.75))

def weightByCount(edgeVisible):
	return edgeVisible.client.getAttribute('Count').value

display.performLayout(layouts['SpectralLayout'](weightFunction = weightByCount, scaling = (-40.0, 12.5, 0.25)))
