#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

import neuroptikon
from display.shape import PathShape, Shape
import osg
from math import sqrt
import wx
import random


class Line(PathShape):
    
    @classmethod
    def name(cls):
        return gettext('Line')
    
    
    def __init__(self, *args, **keywordArgs):
        self._pathPoints = []
        self._weight = 1.01 # so setting to 1.0 triggers a geometry update, bit of a hack
        
        PathShape.__init__(self, *args, **keywordArgs)
        print self.weight()
        if neuroptikon.config.ReadBool('Smooth Lines'):
            self.geometry().getOrCreateStateSet().setMode(osg.GL_LINE_SMOOTH, osg.StateAttribute.ON)
            #self.geometry().getStateSet().setAttributeAndModes(osg.BlendFunc(osg.BlendFunc.SRC_ALPHA, osg.BlendFunc.ONE_MINUS_SRC_ALPHA), osg.StateAttribute.ON)
            #self.geometry().getStateSet().setAttributeAndModes(osg.Hint(osg.GL_LINE_SMOOTH_HINT, osg.GL_NICEST), osg.StateAttribute.ON)
            self.geometry().getStateSet().setMode(osg.GL_POINT_SMOOTH, osg.StateAttribute.ON)
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
            pointVertices = []
            textureCoords = []
            pointCoords = []
            
            prevPoint = None
            pathLength = 0.0
            tweak = -0.0001 * random.random()
            for pathPoint in self._pathPoints:
                if prevPoint != None:
                    pathLength += sqrt((pathPoint[0] - prevPoint[0]) ** 2 + (pathPoint[1] - prevPoint[1]) ** 2 + (pathPoint[2] - prevPoint[2]) ** 2)
                vertices += [(pathPoint[0], pathPoint[1], pathPoint[2] + tweak)]
                textureCoords += [(pathLength, pathLength)]
                if pathPoint != self._pathPoints[0] and pathPoint != self._pathPoints[-1]:
                    tweak *= -1.0
                    vertices += [(pathPoint[0], pathPoint[1], pathPoint[2] + tweak)]
                    textureCoords += [(pathLength, pathLength)]
                pointVertices += [(pathPoint[0], pathPoint[1], pathPoint[2] - 0.0001)] # always beyond tweak
                pointCoords += [(pathLength, pathLength)]
                prevPoint = pathPoint
            
            self.geometry().setVertexArray(Shape.vectorArrayFromList(vertices + pointVertices))
            self.geometry().addPrimitiveSet(Shape.primitiveSetFromList(osg.PrimitiveSet.LINES, range(len(vertices))))
            self.geometry().addPrimitiveSet(Shape.primitiveSetFromList(osg.PrimitiveSet.POINTS, range(len(vertices), len(vertices) + len(self._pathPoints))))
            self.geometry().setNormalArray(Shape.vectorArrayFromList([(0.0, 0.0, 0.0)]))
            self.geometry().setNormalBinding(osg.Geometry.BIND_OVERALL)
            self.geometry().setTexCoordArray(0, Shape.vectorArrayFromList(textureCoords + pointCoords))
            
            self.geometry().dirtyDisplayList()
    
    
    def points(self):
        return list(self._pathPoints)
    
    
    def setWeight(self, weight):
        if weight != self._weight:
            self.geometry().getOrCreateStateSet().setAttributeAndModes(osg.LineWidth(weight), osg.StateAttribute.ON)
            if neuroptikon.config.ReadBool('Smooth Lines'):
                self.geometry().getStateSet().setAttributeAndModes(osg.Point(weight), osg.StateAttribute.ON)
            else:
                self.geometry().getStateSet().setAttributeAndModes(osg.Point(weight * 0.8), osg.StateAttribute.ON)
            self.geometry().dirtyDisplayList()
            self._weight = weight
    
    
    def weight(self):
        return self._weight
    
    
    def intersectionPoint(self, rayOrigin, rayDirection):
        return None
