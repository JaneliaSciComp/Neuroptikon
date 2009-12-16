#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

"""
This script demonstrates creating a simple visualization without anything in the biological layer.
"""

# Create some nodes
nodes = {}
for i in range(10):
    nodes[i] = display.visualizeObject(None, label = str(i))

# Create a bunch of edges
for i in range(10):
    for j in range(10):
        if i != j:
            display.visualizeObject(None, shape = shapes['Line'], pathEndPoints = (nodes[i], nodes[j]), flowTo = True)

# Try to lay them out nicely.
display.performLayout()
