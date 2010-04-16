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

def progressCallback(fraction_complete = None):
    return updateProgress('Calculating centrality...', fraction_complete)

# Compute the centrality of each node in the graph. (uncomment one of the following)
#centralities = networkx.degree_centrality(network.simplifiedGraph())
#centralities = networkx.closeness_centrality(network.simplifiedGraph(), weighted_edges = True, progress_callback = progressCallback)
centralities = networkx.betweenness_centrality(network.simplifiedGraph(), weighted_edges = True, progress_callback = progressCallback)
#centralities = networkx.load_centrality(network.simplifiedGraph(), weighted_edges = True, progress_callback = progressCallback)

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
        for partner in synapse.postSynapticPartners:
            centrality += objectCentralities[partner if instance(partner, Neuron) else partner.neuron()]
        centrality /= 1 + len(synapse.postSynapticPartners)
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
