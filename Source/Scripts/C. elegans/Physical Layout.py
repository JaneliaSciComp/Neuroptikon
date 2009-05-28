import os.path

# Load the base network.
execfile(os.path.join(os.path.dirname(__file__), 'C. elegans.py'))

# Load the positions of the soma.
somaPositions = {}
clusters = {}
neuronTypesFile = open(os.path.join(os.path.dirname(__file__), 'NeuronType.txt'))
try:
    for line in neuronTypesFile:
        if line[0] != '#':
            fields = line.split('\t')
            neuronName = fields[0]
            somaPosition = fields[1]
            somaPositions[neuronName] = somaPosition
            clusterKey = somaPosition + network.findNeuron(neuronName).getAttribute('Side').value
            if clusterKey in clusters:
                clusters[clusterKey].append(neuronName)
                clusters[clusterKey].sort()
            else:
                clusters[clusterKey] = [neuronName]
except:
    (exceptionType, exceptionValue, exceptionTraceback) = sys.exc_info()
    print 'Could not load soma positions (' + exceptionValue.message + ')'
neuronTypesFile.close()

# Set up the visualization

display.setViewDimensions(2)
display.setShowNeuronNames(True)
display.setUseGhosts(True)
display.setDefaultFlowSpread(0.5)

ACh = library.neurotransmitter('ACh')
GABA = library.neurotransmitter('GABA')

for neuron in display.network.neurons():
    # Color the soma based on function.
    red = green = blue = 0.5
    if neuron.hasFunction(NeuralFunction.SENSORY):
        red = 1.0
    if neuron.hasFunction(NeuralFunction.INTERNEURON):
        blue = 1.0
    if neuron.hasFunction(NeuralFunction.MOTOR):
        green = 1.0
    display.setVisibleColor(neuron, (red, green, blue))
    
    # Position the soma according to their linear distance between head and tail and their left/center/right position.
    somaX = float(somaPositions[neuron.name]) * 4.0 - 2.0
    somaY = 0.0
    somaSide = neuron.getAttribute('Side')
    if somaSide is not None:
        if somaSide.value == 'L':
            somaY = -0.15
        elif somaSide.value == 'R':
            somaY = 0.15
    # Many soma have the exact same X/Y coordinates so we distribute them evenly around the common point.
    clusterKey = str(somaPositions[neuron.name]) + neuron.getAttribute('Side').value
    cluster = clusters[clusterKey]
    somaY += (len(cluster) - 1) / 2.0 * 0.015 - cluster.index(neuron.name) * 0.015
    display.setVisiblePosition(neuron, (somaX, somaY, 0.0), fixed = True)

# Color the synapses according to excitation/inhibition and weight them according to their connection count.
for synapse in display.network.synapses():
    if ACh in synapse.preSynapticNeurite.neuron().neurotransmitters:
        display.setVisibleColor(synapse, (0.5, 0.5, 0.75))
    elif GABA in synapse.preSynapticNeurite.neuron().neurotransmitters:
        display.setVisibleColor(synapse, (0.75, 0.5, 0.5))
    else:
        display.setVisibleColor(synapse, (0.5, 0.5, 0.5))
    display.setVisibleWeight(synapse, 0.25 if synapse.getAttribute('Count').value < 5 else 0.5)

# Make all gap junctions black and weight them according to their connection count.
for gapJunction in display.network.gapJunctions():
    display.setVisibleColor(gapJunction, (0.0, 0.0, 0.0))
    display.setVisibleWeight(gapJunction, 0.25 if gapJunction.getAttribute('Count').value < 5 else 0.5)

display.centerView()
