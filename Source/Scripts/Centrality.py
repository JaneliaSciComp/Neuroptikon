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
# Use a simplified graph so the calculation doesn't take as long.  Weighted betweenness centrality is nearly an n-cubed algorithm: O(n m + n^2 log n).
#centralities = networkx.degree_centrality(network.simplifiedGraph())
#centralities = networkx.closeness_centrality(network.simplifiedGraph(), weighted_edges = True, progress_callback = progressCallback)
centralities = networkx.betweenness_centrality(network.simplifiedGraph(), weighted_edges = True, progress_callback = progressCallback)
#centralities = networkx.load_centrality(network.simplifiedGraph(), weighted_edges = True, progress_callback = progressCallback)

if any(centralities):
    # Compute the maximum centrality so we can normalize.
    maxCentrality = max(centralities.itervalues())
    
    if maxCentrality > 0.0:
        # Alter the visualization of each node based on its centrality.
        for node, centrality in centralities.iteritems():
            networkObject = network.objectWithId(node)
            for visible in display.visiblesForObject(networkObject):
                if not visible.isPath():
                    size = visible.size()
                    scale = centrality / maxCentrality
                    scale = 0.05 + scale * 0.95
                    visible.setSize((size[0] * scale, size[1] * scale, size[2] * scale))
