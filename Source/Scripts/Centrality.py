#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

"""
A script to demonstrate how to use the centrality algorithms built into NetworkX.
See <http://networkx.lanl.gov/reference/algorithms.centrality.html> for the full list of algorithms and their descriptions.
"""

import networkx

def progressCallback(fraction_complete = None):
    return updateProgress('Calculating centrality...', fraction_complete)

# Compute the centrality of each node in the graph. (uncomment one of the following)
#centralities = networkx.degree_centrality(network.graph)
#centralities = networkx.closeness_centrality(network.graph, weighted_edges = True)
centralities = networkx.betweenness_centrality(network.graph, weighted_edges = True, progress_callback = progressCallback)
#centralities = networkx.load_centrality(network.graph, weighted_edges = True)

if any(centralities):
    # Compute the maximum centrality so we can normalize.
    maxCentrality = max(centralities.itervalues())
    
    # Alter the visualization of each node based on its centrality.
    for node, centrality in centralities.iteritems():
        networkObject = network.objectWithId(node)
        size = display.visiblesForObject(networkObject)[0].size()
        scale = centrality / maxCentrality
        scale = 0.05 + scale * 0.95
        display.setVisibleSize(networkObject, (size[0] * scale, size[1] * scale, size[2] * scale))
