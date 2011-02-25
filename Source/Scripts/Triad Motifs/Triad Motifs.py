#  Copyright (c) 2011 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

"""
A script to demonstrate counting triad motifs (patterns of connections between three objects).
"""

from networkx import DiGraph
import triadic_census
from math import sqrt

triadOrder = ['003', '012', '102', '021D', '021U', '021C', '111D', '111U', '030T', '030C', '201', '120D', '120U', '120C', '210', '300']
triadColors = {'003': (1.0, 1.0, 0.0), 
              '012': (0.0, 1.0, 0.0), 
               '102': (0.0, 0.0, 1.0), 
               '021D': (1.0, 0.0, 0.0), 
               '021U': (1.0, 0.388, 0.129), 
               '021C': (0.0, 0.0, 0.0), 
               '111D': (1.0, 1.0, 1.0), 
               '111U': (0.5, 0.5, 0.5), 
               '030T': (0.098, 0.047, 0.961), 
               '030C': (0.149, 1.0, 0.8), 
               '201': (1.0, 0.388, 0.129), 
               '120D': (1.0, 0.682, 0.478), 
               '120U': (1.0, 0.0, 1.0), 
               '120C': (0.5, 0.5, 0.5), 
               '210': (0.851, 1.0, 0.31), 
               '300': (0.0, 1.0, 1.0)}
triadEdges = {'003': [], 
              '012': [(1, 0)], 
              '102': [(0, 1), (1, 0)], 
              '021D': [(0, 1), (0, 2)], 
              '021U': [(1, 0), (2, 0)], 
              '021C': [(0, 2), (1, 0)], 
              '111D': [(0, 2), (1, 2), (2, 1)], 
              '111U': [(1, 2), (2, 0), (2, 1)], 
              '030T': [(1, 0), (1, 2), (2, 0)], 
              '030C': [(0, 1), (1, 2), (2, 0)], 
              '201': [(0, 1), (1, 0), (1, 2), (2, 1)], 
              '120D': [(0, 1), (0, 2), (1, 2), (2, 1)], 
              '120U': [(1, 0), (1, 2), (2, 0), (2, 1)], 
              '120C': [(0, 2), (1, 0), (1, 2), (2, 1)], 
              '210': [(0, 2), (1, 0), (1, 2), (2, 0), (2, 1)], 
              '300': [(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)]}

updateProgress(gettext('Creating triad motif compatible version of the network...'), forceDisplay = True)
# The triadic census code requires the nodes of the graph to be named 0, 1, 2, etc.
# We also exclude all of the neurites and target all of their connections to a single neuron object.
triadGraph = DiGraph()
nodes = {}
# Add the nodes
for neuron in network.neurons():
    if id(neuron) not in nodes:
        nodes[id(neuron)] = len(nodes)
    triadGraph.add_node(nodes[id(neuron)])
for region in network.regions():
    if id(region) not in nodes:
        nodes[id(region)] = len(nodes)
    triadGraph.add_node(nodes[id(region)])
for muscle in network.muscles():
    if id(muscle) not in nodes:
        nodes[id(muscle)] = len(nodes)
    triadGraph.add_node(nodes[id(muscle)])
for stimulus in network.stimuli():
    if id(stimulus) not in nodes:
        nodes[id(stimulus)] = len(nodes)
    triadGraph.add_node(nodes[id(stimulus)])
# Add the edges
for arborization in network.arborizations():
    if arborization.sendsOutput:
        triadGraph.add_edge(nodes[id(arborization.neurite.rootObject())], nodes[id(arborization.region)])
    if arborization.receivesInput:
        triadGraph.add_edge(nodes[id(arborization.region)], nodes[id(arborization.neurite.rootObject())])
for gapJunction in network.gapJunctions():
    (neuron1, neuron2) = [neurite.rootObject() for neurite in gapJunction.neurites()]
    triadGraph.add_edge(nodes[id(neuron1)], nodes[id(neuron2)])
    triadGraph.add_edge(nodes[id(neuron2)], nodes[id(neuron1)])
for innervation in network.innervations():
    triadGraph.add_edge(nodes[id(innervation.neurite.rootObject())], nodes[id(innervation.muscle)])
for pathway in network.pathways():
    if pathway.region1Projects:
        triadGraph.add_edge(nodes[id(pathway.region1)], nodes[id(pathway.region2)])
    if pathway.region2Projects:
        triadGraph.add_edge(nodes[id(pathway.region2)], nodes[id(pathway.region1)])
for stimulus in network.stimuli():
    triadGraph.add_edge(nodes[id(stimulus)], nodes[id(stimulus.target.rootObject())])
for synapse in network.synapses():
    for postPartner in synapse.postSynapticPartners:
        triadGraph.add_edge(nodes[id(synapse.preSynapticNeurite.rootObject())], nodes[id(postPartner.rootObject())])

updateProgress(gettext('Finding motifs...'))
counts = triadic_census.triadic_census(triadGraph)

# Report the results in the console in case the user wants to copy/paste
print('Triad motif occurences:')
print('Motif\tCount')
for triad in triadOrder:
    print(triad + '\t' + str(counts[triad]))

# Open a new display that shows the results graphically
network = createNetwork()
display = displayNetwork(network)
display.setDefaultFlowSpacing(0.15)
edgeLength = 0.5
xDiff = edgeLength / 2.0
yDiff = sqrt(edgeLength ** 2 - xDiff ** 2) / 2.0
nodeSize = edgeLength / 5.0
for triad in triadOrder:
    x = triadOrder.index(triad) % 4
    y = 4 - triadOrder.index(triad) / 4
    nodes = []
    nodes += [display.visualizeObject(None, None, shape = 'Ball', position = (x, y + yDiff, 0.0), size = (nodeSize, nodeSize, nodeSize), color = triadColors[triad])]
    nodes += [display.visualizeObject(None, None, shape = 'Ball', position = (x - xDiff, y - yDiff, 0.0), size = (nodeSize, nodeSize, nodeSize), color = triadColors[triad])]
    nodes += [display.visualizeObject(None, None, shape = 'Ball', position = (x + xDiff, y - yDiff, 0.0), size = (nodeSize, nodeSize, nodeSize), color = triadColors[triad])]
    countNode = display.visualizeObject(None, None, shape = None, position = (x, y - yDiff * 0.25, 0.0), label = str(counts[triad]))
    for edge in triadEdges[triad]:
        startNode, endNode = edge
        display.visualizeObject(None, None, shape = 'Line', pathEndPoints = (nodes[startNode], nodes[endNode]), flowTo = True, width = 2.0)
    countNode = display.visualizeObject(None, None, shape = None, position = (x, y - yDiff * 1.5, 0.0), label = triad)
display.centerView()
display.setShowFlow(True)
