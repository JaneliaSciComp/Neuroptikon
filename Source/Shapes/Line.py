from Display.Shape import PathShape, Shape
import osg
from math import sqrt


class Line(PathShape):
    
    @classmethod
    def name(cls):
        return gettext('Line')
    
    
    def __init__(self, *args, **keywordArgs):
        self._pathPoints = []
        PathShape.__init__(self, *args, **keywordArgs)
        
        self.geometry().getOrCreateStateSet().setMode(osg.GL_LINE_SMOOTH, osg.StateAttribute.ON)
        self.geometry().getStateSet().setRenderingHint(osg.StateSet.TRANSPARENT_BIN)
        self.geometry().getStateSet().setMode(osg.GL_BLEND, osg.StateAttribute.ON)
    
    
    def setPoints(self, pathPoints):
        if pathPoints != self._pathPoints:
            while self.geometry().getNumPrimitiveSets() > 0:
                self.geometry().removePrimitiveSet(0)
            
            self._pathPoints = pathPoints
    
            vertices = []
            textureCoords = []
            
            lastPoint = None
            pathLength = 0.0
            for pathPoint in self._pathPoints:
                if len(pathPoint) == 2:
                    pathPoint = (pathPoint[0], pathPoint[1], 0.0)
                if lastPoint != None:
                    pathLength += sqrt((pathPoint[0] - lastPoint[0]) ** 2 + (pathPoint[1] - lastPoint[1]) ** 2 + (pathPoint[2] - lastPoint[2]) ** 2)
                vertices.append((pathPoint[0], pathPoint[1], 0.0 if len(pathPoint) == 2 else pathPoint[2]))
                textureCoords.append([pathLength] * 2)
                lastPoint = pathPoint
            
            self.geometry().setVertexArray(Shape.vectorArrayFromList(vertices))
            self.geometry().addPrimitiveSet(Shape.primitiveSetFromList(osg.PrimitiveSet.LINE_STRIP, range(len(self._pathPoints))))
            self.geometry().setNormalArray(Shape.vectorArrayFromList([(0.0, 0.0, 0.0)]))
            self.geometry().setNormalBinding(osg.Geometry.BIND_OVERALL)
            self.geometry().setTexCoordArray(0, Shape.vectorArrayFromList(textureCoords))
            
            self.geometry().dirtyDisplayList()
    
    
    def setWeight(self, weight):
        self.geometry().getOrCreateStateSet().setAttributeAndModes(osg.LineWidth(weight), osg.StateAttribute.ON)
        self.geometry().dirtyDisplayList()