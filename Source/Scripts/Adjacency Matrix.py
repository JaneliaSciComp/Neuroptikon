#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html


"""
This script loads a region-level network from a user-chosen adjacency matrix.

It is assumed that the first line of the file indicates the region name for each column (and thus for each row as well) 
and that subsequent lines have the same number of tab separated columns with non-zero entries indicating adjacency.
"""

import wx

# Ask the user which adjacency file should be loaded.
dlg = wx.FileDialog(None, 'Choose an adjacency file to load', '', '', '*.txt', wx.OPEN)
try:
    if dlg.ShowModal() == wx.ID_OK:
        adjancencyFile = open(dlg.GetPath())
        regions = {}
        try:
            # Create the regions.
            regionNames = adjancencyFile.next().strip().split('\t')
            for regionName in regionNames:
                regions[regionName] = network.createRegion(name = regionName)
            
            # Create the pathways.
            for preRegion, postRegions in map(None, regionNames, adjancencyFile):
                if preRegion is not None and postRegions is not None:
                    for postRegion, adjacency in map(None, regionNames, postRegions.strip().split('\t')):
                        if postRegion is not None and adjacency is not None and adjacency.strip() != '0':
                            regions[preRegion.strip()].projectToRegion(regions[postRegion.strip()])
            
            display.performLayout()
        finally:
            adjancencyFile.close()
finally:
    dlg.Destroy()
