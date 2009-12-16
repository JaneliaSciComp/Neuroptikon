#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

"""
This script demonstrates visualizing only part of a network.
"""

display.autoVisualize = False
display.setShowNeuronNames(True)
display.setUseGhosts(True)

if not any(network.muscles()):
    execfile('Muscles.py')

neurons = []
muscles = []
gapJunctions = []

verticalSpacing = 0.1

# Visualize DB 1-8 neurons.
for index in range(1, 8):
    neuron = network.findNeuron('DB%02d' % index)
    display.visualizeObject(neuron, position = (0.75 / 8.0 * index - 0.375, verticalSpacing * 1.5, 0.0), positionIsFixed = True, size = (0.015, 0.015, 0.015))
    neurons.append(neuron)

# Visualize VD 1-8 neurons.
for index in range(1, 14):
    neuron = network.findNeuron('VD%02d' % index)
    display.visualizeObject(neuron, position = (0.75 / 14.0 * index - 0.375, verticalSpacing * 0.5, 0.0), positionIsFixed = True, size = (0.015, 0.015, 0.015))
    neurons.append(neuron)

# Visualize DB 1-8 neurons.
for index in range(1, 7):
    neuron = network.findNeuron('DD%02d' % index)
    display.visualizeObject(neuron, position = (0.75 / 7.0 * index - 0.375, verticalSpacing * -0.5, 0.0), positionIsFixed = True, size = (0.015, 0.015, 0.015))
    neurons.append(neuron)

# Visualize DB 1-8 neurons.
for index in range(1, 12):
    neuron = network.findNeuron('VB%02d' % index)
    display.visualizeObject(neuron, position = (0.75 / 12.0 * index - 0.375, verticalSpacing * -1.5, 0.0), positionIsFixed = True, size = (0.015, 0.015, 0.015))
    neurons.append(neuron)

ACh = library.neurotransmitter('ACh')
GABA = library.neurotransmitter('GABA')

for neuron in neurons:
    # Color the soma based on function.
    shapeColor = [0.5, 0.5, 0.5]
    labelColor = [0.0, 0.0, 0.0]
    if neuron.hasFunction(Neuron.Function.SENSORY):
        shapeColor[0] = 1.0
        labelColor[0] = 0.125
    if neuron.hasFunction(Neuron.Function.INTERNEURON):
        shapeColor[2] = 1.0
        labelColor[2] = 0.125
    if neuron.hasFunction(Neuron.Function.MOTOR):
        shapeColor[1] = 1.0
        labelColor[1] = 0.125
    display.setVisibleColor(neuron, shapeColor)
    display.setLabelColor(neuron, labelColor)
    
    # Visualize any chemical synapses that this neuron makes onto other neurons in the visualization.
    for synapse in neuron.synapses(includePost = False):
        if synapse.postSynapticNeurites[0].neuron() in neurons:
            display.visualizeObject(synapse, weight = 2.0)
            if ACh in neuron.neurotransmitters:
                display.setVisibleColor(synapse, (0.5, 0.5, 1.0))
            elif GABA in neuron.neurotransmitters:
                display.setVisibleColor(synapse, (1.0, 0.5, 0.5))
    
    # Visualize any gap junctions that this neuron makes with other neurons in the visualization.
    for gapJunction in neuron.gapJunctions():
        for neurite in gapJunction.neurites():
            if neurite.neuron() != neuron:
                otherNeuron = neurite.neuron()
        if gapJunction not in gapJunctions and otherNeuron in neurons:
            display.visualizeObject(gapJunction, weight = 2.0)
            display.setVisibleColor(gapJunction, (0.5, 0.5, 0.5))
            gapJunctions += [gapJunction]
    
    # Visualize any innervations that this neuron makes.
    for innervation in neuron.innervations():
        muscle = innervation.muscle
        if muscle not in muscles:
            muscleX = muscle.getAttribute('A-P Position').value() - 0.5
            muscleY = 0.0
            muscleSide = muscle.getAttribute('Side')
            if muscleSide is not None:
                if muscleSide.value() == 'L':
                    muscleY = verticalSpacing * -2.5
                elif muscleSide.value() == 'R':
                    muscleY = verticalSpacing * 2.5
            muscleFace = muscle.getAttribute('Face')
            if muscleFace is not None:
                if muscleFace.value() == 'D':
                    muscleY -= verticalSpacing / 4.0
                elif muscleFace.value() == 'V':
                    muscleY += verticalSpacing / 4.0
            display.visualizeObject(muscle, position = (muscleX, muscleY, 0.0), size = (0.01, 0.02, 0.01), opacity = 0.75)
            muscles += [muscle]
        display.visualizeObject(innervation, weight = 0.5, opacity = 0.75)
    
display.zoomToFit()
