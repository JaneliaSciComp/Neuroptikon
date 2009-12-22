#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

"""
A custom centrality script for the C. elegans network.
"""

# Load the neurons and their interconnections if needed.
if not any(network.objects):
    execfile('Connectivity.py')

# Create a simplified graph so the calculation doesn't take as long.  Weighted betweenness centrality is nearly an n-cubed algorithm: O(n m + n^2 log n).
import networkx
def addEdge(graph, object1, object2, weight):
    node1 = object1.networkId
    node2 = object2.networkId
    if node1 in graph and node2 in graph[node1]:
        if weight < graph[node1][node2]['weight']:
            # Use a smaller weight for an existing edge.
            graph[node1][node2]['weight'] = weight
    else:
        # Create a new edge.
        graph.add_edge(node1, node2, weight = weight)
simplifiedGraph = networkx.DiGraph()
for synapse in network.synapses():
    for neurite in synapse.postSynapticNeurites:
        addEdge(simplifiedGraph, synapse.preSynapticNeurite.neuron(), neurite.neuron(), network.weightOfObject(synapse))
for gapJunction in network.gapJunctions():
    neurites = gapJunction.neurites()
    addEdge(simplifiedGraph, neurites[0].neuron(), neurites[1].neuron(), network.weightOfObject(gapJunction))
    addEdge(simplifiedGraph, neurites[1].neuron(), neurites[0].neuron(), network.weightOfObject(gapJunction))
for innervation in network.innervations():
    addEdge(simplifiedGraph, innervation.neurite.neuron(), innervation.muscle, network.weightOfObject(innervation))

def progressCallback(fraction_complete = None):
    return updateProgress('Calculating centrality...', fraction_complete)

# Compute the centrality of each node in the graph. (uncomment one of the following)
#centralities = networkx.degree_centrality(simplifiedGraph)
#centralities = networkx.closeness_centrality(simplifiedGraph, weighted_edges = True)
centralities = networkx.betweenness_centrality(simplifiedGraph, weighted_edges = True, progress_callback = progressCallback)
#centralities = networkx.load_centrality(simplifiedGraph, weighted_edges = True)

if any(centralities):
    # Compute the maximum centrality so we can normalize.
    maxCentrality = max(centralities.itervalues())
    
    # Alter the visualization of each node based on its centrality.
    objectCentralities = {}
    for node, centrality in centralities.iteritems():
        object = network.objectWithId(node)
        objectCentralities[object] = centrality / maxCentrality
        diameter = 0.001 + objectCentralities[object] * 0.029
        display.setVisibleSize(object, [diameter] * 3)
    
    for synapse in network.synapses():
        centrality = objectCentralities[synapse.preSynapticNeurite.neuron()]
        for neurite in synapse.postSynapticNeurites:
            centrality += objectCentralities[neurite.neuron()]
        centrality /= 1 + len(synapse.postSynapticNeurites)
        display.setVisibleOpacity(synapse, centrality)
    
    for gapJunction in network.gapJunctions():
        centrality = 0.0
        for neurite in gapJunction.neurites():
            centrality += objectCentralities[neurite.neuron()]
        centrality /= 2.0
        display.setVisibleOpacity(gapJunction, centrality)
    
    for innervation in network.innervations():
        centrality = (objectCentralities[innervation.neurite.neuron()] + objectCentralities[innervation.muscle]) / 2.0
        display.setVisibleOpacity(innervation, centrality)
