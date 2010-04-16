#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

"""
A script to demonstrate community detection.
Uses the community module bundled with Neuroptikon and written by Thomas Aynaud <http://perso.crans.org/aynaud/communities/>.
"""

import community

updateProgress(gettext('Finding communities...'), forceDisplay = True)
dendogram = community.generate_dendogram(network.simplifiedGraph())
updateProgress(gettext('Finding communities...'))
partition = community.best_partition(dendogram)

if any(partition):
    updateProgress(gettext('Isolating communities...'))
    for visibles in list(display.visibles.itervalues()):
        for visible in visibles:
            if visible.isPath() and not isinstance(visible.client, Stimulus):
                startCommunity, endCommunity = [partition[node.client.networkId] for node in visible.pathEndPoints()]
                if startCommunity != endCommunity:
                    display.removeVisible(visible)
    
    updateProgress(gettext('Visually separating communities...'))
    display.setViewDimensions(2)
    for obj in network.objects:
        display.setVisiblePosition(obj, fixed = False)
    try:
        display.performLayout(layouts['Graphviz'])
    except:
        display.performLayout(layouts['Force Directed'])
