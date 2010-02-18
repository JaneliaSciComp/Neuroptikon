#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html


"""
This script loads a region- or neuron-level network from a user-chosen adjacency matrix.

It is assumed that the first line of the file indicates the region/neuron name for each column (and thus for each row as well) 
and that subsequent lines have the same number of tab separated columns with non-zero entries indicating adjacency.  The non-zero 
value is assumed to indicate the strength of the connection with higher values indicating higher strengths.
"""

import wx


# Set up a weighting function that uses our custom "Count" attribute
def weightByCount(networkObject):
    countAttribute = networkObject.getAttribute('Count')
    return 1.0 if not countAttribute else 1.0 / countAttribute.value()


# Ask the user which adjacency file should be loaded.
fileDlg = wx.FileDialog(None, 'Choose an adjacency file to load', '', '', '*.txt', wx.OPEN)
try:
    if fileDlg.ShowModal() == wx.ID_OK:
        # Ask the user what kind of connections are in the file.
        choiceDlg = wx.SingleChoiceDialog(None, 'What type of connections are in the file?', 'Adjacency Matrix Loader', ['Pathways', 'Chemical synapses', 'Electrical synapses'])
        try:
            if choiceDlg.ShowModal() == wx.ID_OK:
                connectionType = choiceDlg.GetStringSelection()
                if connectionType == 'Pathways':
                    regions = {}
                else:
                    neurons = {}
                
                # ...
                network.setWeightingFunction(weightByCount)
                
                
                adjancencyFile = open(fileDlg.GetPath())
                try:
                    # Create the regions/neurons.
                    names = adjancencyFile.next().strip().split('\t')
                    if connectionType == 'Pathways':
                        for regionName in names:
                            regions[regionName] = network.findRegion(name = regionName) or network.createRegion(name = regionName)
                    else:
                        for neuronName in names:
                            neurons[neuronName] = network.findNeuron(name = neuronName) or network.createNeuron(name = neuronName)
                    
                    # Create the connections.
                    for preObject, postObjects in map(None, names, adjancencyFile):
                        if preObject is not None and postObjects is not None:
                            for postObject, adjacency in map(None, names, postObjects.strip().split('\t')):
                                if postObject is not None and adjacency is not None:
                                    adjacency = adjacency.strip()
                                    if adjacency != '0':
                                        if connectionType == 'Pathways':
                                            connection = regions[preObject.strip()].projectToRegion(regions[postObject.strip()])
                                        elif connectionType == 'Chemical synapses':
                                            connection = neurons[preObject.strip()].synapseOn(neurons[postObject.strip()])
                                        elif connectionType == 'Electrical synapses':
                                            connection = neurons[preObject.strip()].gapJunctionWith(neurons[postObject.strip()])
                                        try:
                                            connection.addAttribute('Count', Attribute.INTEGER_TYPE, int(adjacency))
                                        except:
                                            pass
                    
                    display.performLayout()
                    if connectionType != 'Pathways':
                        display.showNeuronNames()
                finally:
                    adjancencyFile.close()
        finally:
            choiceDlg.Destroy()
finally:
    fileDlg.Destroy()
