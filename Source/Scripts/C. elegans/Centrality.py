"""
A script to demonstrate how to use the centrality algorithms built into NetworkX.
See <http://networkx.lanl.gov/reference/algorithms.centrality.html> for the full list of algorithms and their descriptions.
"""

# Load the neurons and their interconnections if needed.
if not any(network.neurons()):
    execfile('Connectivity.py')

import networkx

# Create a new graph with only a single edge between nodes weighted by the sum of the connection counts.
# This only works with the C. elegans.py network at this point.  Other networks will have constant (1.0) edge weights.
graph = networkx.XGraph()
for (node1, node2, object) in network.graph.edges():
    weight = 1.0
    if object != None:
        count = object.getAttribute('Count')
        if count:
            weight = count.value()
    # Gap junctions are undirected which is represented in the original graph by two directed edges.  Divide the weight in half so the strength of the connection is correct.
    if isinstance(object, GapJunction):
        weight /= 2.0
    if graph.has_edge(node1, node2):
        previousWeight = 1.0 / graph.get_edge(node1, node2)
    else:
        previousWeight = 0.0
    graph.add_edge(node1, node2, 1.0 / (previousWeight + weight))   # the more connections the lower the weight
    
# Compute the centrality of each node in the graph. (uncomment one of the following)
centralities = networkx.degree_centrality(graph)
#centralities = networkx.closeness_centrality(graph, weighted_edges = True)
#centralities = networkx.betweenness_centrality(graph, weighted_edges = True)
#centralities = networkx.load_centrality(graph, weighted_edges = True)
    
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
