import os, os.path

display.autoVisualize = False
display.setShowNeuronNames(True)
display.setUseGhosts(True)

execfile(os.path.dirname(__file__) + os.sep + 'C. elegans.py')

neurons = []

verticalSpacing = 0.15

for index in range(1, 8):
    neuron = network.findNeuron('DB%02d' % index)
    display.visualizeObject(neuron, position = (1.0 / 8.0 * index - 0.5, verticalSpacing * 1.5, 0.0), positionIsFixed = True)
    neurons.append(neuron)

for index in range(1, 14):
    neuron = network.findNeuron('VD%02d' % index)
    display.visualizeObject(neuron, position = (1.0 / 14.0 * index - 0.5, verticalSpacing * 0.5, 0.0), positionIsFixed = True)
    neurons.append(neuron)

for index in range(1, 7):
    neuron = network.findNeuron('DD%02d' % index)
    display.visualizeObject(neuron, position = (1.0 / 7.0 * index - 0.5, verticalSpacing * -0.5, 0.0), positionIsFixed = True)
    neurons.append(neuron)

for index in range(1, 12):
    neuron = network.findNeuron('VB%02d' % index)
    display.visualizeObject(neuron, position = (1.0 / 12.0 * index - 0.5, verticalSpacing * -1.5, 0.0), positionIsFixed = True)
    neurons.append(neuron)

ACh = library.neurotransmitter('ACh')
GABA = library.neurotransmitter('GABA')

for neuron in neurons:
    for synapse in neuron.incomingSynapses():
        if synapse.preSynapticNeurite.neuron() in neurons:
            display.visualizeObject(synapse)
            if ACh in synapse.preSynapticNeurite.neuron().neurotransmitters:
                display.setVisibleColor(synapse, (0.5, 0.5, 1.0))
            elif GABA in synapse.preSynapticNeurite.neuron().neurotransmitters:
                display.setVisibleColor(synapse, (1.0, 0.5, 0.5))
    for synapse in neuron.outgoingSynapses():
        if synapse.postSynapticNeurites[0].neuron() in neurons:
            display.visualizeObject(synapse)
            if ACh in neuron.neurotransmitters:
                display.setVisibleColor(synapse, (0.5, 0.5, 1.0))
            elif GABA in neuron.neurotransmitters:
                display.setVisibleColor(synapse, (1.0, 0.5, 0.5))
    for gapJunction in neuron.gapJunctions():
        neurites = list(gapJunction.neurites)
        if (neurites[0].neuron() == neuron and neurites[1].neuron() in neurons) or (neurites[1].neuron() == neuron and neurites[0].neuron() in neurons):
            display.visualizeObject(gapJunction)
            display.setVisibleColor(gapJunction, (0.5, 0.5, 0.5))

display.centerView()
