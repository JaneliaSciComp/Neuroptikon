#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

from display.shape import PathShape, Shape
import osg
from math import sqrt
import wx


class Line(PathShape):
    
    @classmethod
    def name(cls):
        return gettext('Line')
    
    
    def __init__(self, *args, **keywordArgs):
        self._pathPoints = []
        self._weight = 1.0
        
        PathShape.__init__(self, *args, **keywordArgs)
        
        if wx.Config('Neuroptikon').ReadBool('Smooth Lines'):
            self.geometry().getOrCreateStateSet().setMode(osg.GL_LINE_SMOOTH, osg.StateAttribute.ON)
            self.geometry().getStateSet().setRenderingHint(osg.StateSet.TRANSPARENT_BIN)
            self.geometry().getStateSet().setMode(osg.GL_BLEND, osg.StateAttribute.ON)
    
    
    def setPoints(self, pathPoints):
        threeDPathPoints = []
        for pathPoint in pathPoints:
            if len(pathPoint) == 2:
                threeDPathPoints += [(pathPoint[0], pathPoint[1], 0.0)]
            else:
                threeDPathPoints += [pathPoint]
        pathPoints = threeDPathPoints
        
        if pathPoints != self._pathPoints:
            while self.geometry().getNumPrimitiveSets() > 0:
                self.geometry().removePrimitiveSet(0)
            
            self._pathPoints = pathPoints
    
            vertices = []
            textureCoords = []
            
            lastPoint = None
            pathLength = 0.0
            for pathPoint in self._pathPoints:
                if lastPoint != None:
                    pathLength += sqrt((pathPoint[0] - lastPoint[0]) ** 2 + (pathPoint[1] - lastPoint[1]) ** 2 + (pathPoint[2] - lastPoint[2]) ** 2)
                vertices += [pathPoint]
                textureCoords += [(pathLength, pathLength)]
                lastPoint = pathPoint
            
            self.geometry().setVertexArray(Shape.vectorArrayFromList(vertices))
            self.geometry().addPrimitiveSet(Shape.primitiveSetFromList(osg.PrimitiveSet.LINE_STRIP, range(len(self._pathPoints))))
            self.geometry().setNormalArray(Shape.vectorArrayFromList([(0.0, 0.0, 0.0)]))
            self.geometry().setNormalBinding(osg.Geometry.BIND_OVERALL)
            self.geometry().setTexCoordArray(0, Shape.vectorArrayFromList(textureCoords))
            
            self.geometry().dirtyDisplayList()
    
    
    def points(self):
        return list(self._pathPoints)
    
    
    def setWeight(self, weight):
        if weight != self._weight:
            self.geometry().getOrCreateStateSet().setAttributeAndModes(osg.LineWidth(weight), osg.StateAttribute.ON)
            self.geometry().dirtyDisplayList()
            self._weight = weight
    
    
    def weight(self):
        return self._weight
    
    
    def intersectionPoint(self, rayOrigin, rayDirection):
        return None
