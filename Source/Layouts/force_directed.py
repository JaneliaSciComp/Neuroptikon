#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

from display.layout import Layout
from math import sqrt
import numpy as N

class ForceDirectedLayout(Layout):
    
    @classmethod
    def name(cls):
        return gettext('Force Directed')
    
    
    def __init__(self, maxIterations = 50, spacing = .005, fill = False, *args, **keywordArgs):
        """ForceDirectedLayout(maxIterations = 50, spacing = .005, fill = False)
        
        """
        Layout.__init__(self, *args, **keywordArgs)
        
        self.maxIterations = maxIterations
        self.spacing = spacing
        self.fill = fill
    
    
    def layoutDisplay(self, display):
        positions = {}
        minPositions = {}
        maxPositions = {}
        edges = []
        for visibles in display.visibles.itervalues():
            for visible in visibles:
                if visible.isPath():
                    edges.append(visible)
                else:
                    position = visible.worldPosition()
                    if display.viewDimensions == 2:
                        position = N.array((position[0], position[1]))
                    else:
                        position = N.array(position)
                    positions[visible] = position
                    
                    size = visible.worldSize()
                    if display.viewDimensions == 2:
                        size = N.array((size[0] / 2.0 + self.spacing, size[1] / 2.0 + self.spacing))
                    else:
                        size = N.array((size[0] / 2.0 + self.spacing, size[1] / 2.0 + self.spacing, size[2] / 2.0 + self.spacing))
                    minPositions[visible] = position - size
                    maxPositions[visible] = position + size
        
        nodeCount = len(positions)
        optimalNodeSep = 1.0 if nodeCount == 0 else sqrt(1.0 / nodeCount)
        
        for i in range(self.maxIterations, 0, -1):
            temperature = 0.1 * i / self.maxIterations
            
            # calculate the displacement for each node
            displacements = {}
            for node in positions:
                displacements[node] = N.zeros(display.viewDimensions)
            
            # Avoid overlapping nodes.
            nodePositions = positions.keys()
            for index1 in range(0, nodeCount - 1):
                node1 = nodePositions[index1]
                ancestors1 = node1.ancestors() + [node1]
                min1 = minPositions[node1]
                max1 = maxPositions[node1]
                
                for index2 in range(index1 + 1, nodeCount):
                    node2 = nodePositions[index2]
                    ancestors2 = node2.ancestors() + [node2]
                    min2 = minPositions[node2]
                    max2 = maxPositions[node2]
                    
                    if self.fill:
                        centerDelta = positions[node1] - positions[node2]
                        centerDeltaMag2 = max(N.dot(centerDelta, centerDelta), 0.0001)
                        delta = centerDelta / centerDeltaMag2 * optimalNodeSep ** 2
                        if not ancestors1[0].positionIsFixed():
                            displacements[ancestors1[0]] = displacements[ancestors1[0]] + delta
                        if not ancestors2[0].positionIsFixed():
                            displacements[ancestors2[0]] = displacements[ancestors2[0]] - delta
                        
                    if node1 not in ancestors2 and node2 not in ancestors1 and (max1 > min2).all() and (min1 < max2).all():
                        # The nodes overlap so apply a force pushing them apart.
                        
                        centerDelta = positions[node1] - positions[node2]
                        if True:
                            centerDeltaMag2 = max(N.dot(centerDelta, centerDelta), 0.0001)
                            delta = centerDelta / centerDeltaMag2 #* self.spacing ** 2
                        else:
                            overlapMin = N.zeros(display.viewDimensions)
                            overlapMax = N.zeros(display.viewDimensions)
                            for dim in range(0, display.viewDimensions):
                                overlapMin[dim] = max(min1[dim], min2[dim])
                                overlapMax[dim] = min(max1[dim], max2[dim])
                            overlapDelta = overlapMax - overlapMin
                            overlapMag2 = N.dot(overlapDelta, overlapDelta)
                            centerDeltaMag = sqrt(N.dot(centerDelta, centerDelta))
                            delta = centerDelta / centerDeltaMag / overlapMag2
                        
                        if not ancestors1[0].positionIsFixed():
                            displacements[ancestors1[0]] = displacements[ancestors1[0]] + delta
                        if not ancestors2[0].positionIsFixed():
                            displacements[ancestors2[0]] = displacements[ancestors2[0]] - delta
            
            # Make the edges as short as possible
            for edge in edges:
                (pathStart, pathEnd) = edge.pathEndPoints()
                delta = positions[pathStart] - positions[pathEnd]
                deltaMag = max(sqrt(N.dot(delta, delta)), 0.01)
                force = delta * deltaMag ** 2 / (optimalNodeSep * deltaMag)
                startRoot = pathStart.rootVisible()
                if not startRoot.positionIsFixed():
                    displacements[startRoot] = displacements[startRoot] - force
                endRoot = pathEnd.rootVisible()
                if not endRoot.positionIsFixed():
                    displacements[endRoot] = displacements[endRoot] + force

            # Displace each node
            totalDisplacement = 0.0
            for node, displacement in displacements.iteritems():
                displacementMag = sqrt(N.dot(displacement, displacement))
                if  displacementMag > 0.0:
                    temperedDisplacement = displacement / displacementMag * temperature
                    positions[node] = positions[node] + temperedDisplacement
                    minPositions[node] = minPositions[node] + temperedDisplacement
                    maxPositions[node] = maxPositions[node] + temperedDisplacement
                    totalDisplacement += displacementMag
            
            #print str(totalDisplacement / nodeCount)
        
        for node, position in positions.iteritems():
            if node.parent == None and not node.positionIsFixed():
                if display.viewDimensions == 2:
                    position = (position[0], position[1], 0.0)
                else:
                    position = (position[0], position[1], position[2])
                node.setPosition(position)
        for edge in edges:
            edge.setPathMidPoints([])
    
