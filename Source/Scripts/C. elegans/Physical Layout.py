#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

"""
This script demonstrates using external data (in this case a tabbed-text file) to aid in visualizing a network.
"""

import os.path, sys
from math import pi

# Load the base network.
if not any(network.muscles()):
    execfile('Muscles.py')

updateProgress('Clustering the neurons...')

# Return the position of the soma using a default value if the attribute is not defined.
def somaPosition(neuron):
    somaPosition = neuron.getAttribute('Soma A-P Position')
    if somaPosition is not None:
        somaPosition = float(somaPosition.value())
    else:
        if neuron.name[0] == 'R':
            somaPosition = 0.9
        else:
            somaPosition = 0.5
    return somaPosition


def sortCluster(neuron1, neuron2):
    if neuron1.hasFunction(Neuron.Function.MOTOR) and neuron1.hasFunction(Neuron.Function.SENSORY):
        key1 = '1' + neuron1.name
    elif neuron1.hasFunction(Neuron.Function.MOTOR):
        key1 = '0' + neuron1.name
    elif neuron1.hasFunction(Neuron.Function.SENSORY):
        key1 = '3' + neuron1.name
    else:
        key1 = '2' + neuron1.name
    
    if neuron2.hasFunction(Neuron.Function.MOTOR) and neuron2.hasFunction(Neuron.Function.SENSORY):
        key2 = '1' + neuron2.name
    elif neuron2.hasFunction(Neuron.Function.MOTOR):
        key2 = '0' + neuron2.name
    elif neuron2.hasFunction(Neuron.Function.SENSORY):
        key2 = '3' + neuron2.name
    else:
        key2 = '2' + neuron2.name
    
    if key1 < key2:
        return -1
    elif key1 > key2:
        return 1
    else:
        return 0

# Cluster the soma based on their A-P position and side.
clusters = {}
for neuron in network.neurons():
    clusterKey = str(somaPosition(neuron)) + neuron.getAttribute('Side').value()
    if clusterKey in clusters:
        clusters[clusterKey] += [neuron]
    else:
        clusters[clusterKey] = [neuron]

for cluster in clusters.itervalues():
    cluster.sort(sortCluster)

# Set up the visualization

display.setViewDimensions(2)
display.setShowNeuronNames(True)
display.setUseGhosts(True)
display.setDefaultFlowSpread(0.5)

updateProgress('Laying out the neurons...')

for neuron in network.neurons():
    # Color the soma based on function.
    red = green = blue = 0.5
    if neuron.hasFunction(Neuron.Function.SENSORY):
        red = 1.0
    if neuron.hasFunction(Neuron.Function.INTERNEURON):
        blue = 1.0
    if neuron.hasFunction(Neuron.Function.MOTOR):
        green = 1.0
    display.setVisibleColor(neuron, (red, green, blue))
    display.setLabelColor(neuron, (0.0 if red == 0.5 else red * 0.125, 0.0 if green == 0.5 else green * 0.125, 0.0 if blue == 0.5 else blue * 0.125))
    
    # Position the soma according to their linear distance between head and tail and their left/center/right position.
    somaX = somaPosition(neuron) * 4.0 - 2.0
    somaY = 0.0
    somaSign = 1.0
    somaSide = neuron.getAttribute('Side')
    if somaSide is not None:
        if somaSide.value() == 'L':
            somaY = -0.15
            somaSign = -1.0
        elif somaSide.value() == 'R':
            somaY = 0.15
    # Many soma have the exact same X/Y coordinates so we distribute them evenly around the common point.
    clusterKey = str(somaPosition(neuron)) + neuron.getAttribute('Side').value()
    cluster = clusters[clusterKey]
    somaY += (len(cluster) - 1) / 2.0 * 0.015 * somaSign - cluster.index(neuron) * 0.015 * somaSign
    display.setVisiblePosition(neuron, (somaX, somaY, -1.0), fixed = True)

updateProgress('Coloring the synapses...')

# Color the synapses according to excitation/inhibition and weight them according to their connection count.
ACh = library.neurotransmitter('ACh')
GABA = library.neurotransmitter('GABA')
for synapse in network.synapses():
    if ACh in synapse.preSynapticNeurite.neuron().neurotransmitters:
        display.setVisibleColor(synapse, (0.5, 0.5, 0.75))
    elif GABA in synapse.preSynapticNeurite.neuron().neurotransmitters:
        display.setVisibleColor(synapse, (0.75, 0.5, 0.5))
    else:
        display.setVisibleColor(synapse, (0.5, 0.5, 0.5))
    display.setVisibleWeight(synapse, 0.5 if synapse.getAttribute('Count').value() < 5 else 2.0)

updateProgress('Coloring the gap junctions...')

# Make all gap junctions black and weight them according to their connection count.
for gapJunction in network.gapJunctions():
    display.setVisibleColor(gapJunction, (0.0, 0.75, 0.0))
    display.setVisibleWeight(gapJunction, 0.5 if gapJunction.getAttribute('Count').value() < 5 else 2.0)

updateProgress('Laying out the muscles...')

for muscle in network.muscles():
    if not any(display.visiblesForObject(muscle)):
        display.visualizeObject(muscle)
    if muscle.getAttribute('A-P Position'):
        muscleX = muscle.getAttribute('A-P Position').value() * 4.0 - 2.0
        if muscle.name in ['MANAL', 'MVULVA']:
            muscleX += 0.02 # Shift the muscles slightly so they don't obscure the neurons at the same position.
        muscleY = 0.0
        muscleSide = muscle.getAttribute('Side')
        if muscleSide is not None:
            if muscleSide.value() == 'L':
                muscleY = -0.3
            elif muscleSide.value() == 'R':
                muscleY = 0.3
        muscleFace = muscle.getAttribute('Face')
        if muscleFace is not None:
            if muscleFace.value() == 'D':
                muscleY -= 0.025
            elif muscleFace.value() == 'V':
                muscleY += 0.025
        display.setVisiblePosition(muscle, (muscleX, muscleY, -1.0), fixed = True)
        display.setVisibleSize(muscle, (0.01, 0.02, .01))

updateProgress('Coloring the innervations...')

for innervation in network.innervations():
    if not any(display.visiblesForObject(innervation)):
        display.visualizeObject(innervation)
    display.setVisibleWeight(innervation, 0.5 if innervation.getAttribute('Count').value() < 5.0 else 2.0)

display.zoomToFit()
