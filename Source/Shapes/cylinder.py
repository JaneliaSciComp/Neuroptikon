#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

from display.shape import Shape, UnitShape
import osg
from math import pi, cos, sin, sqrt


class Cylinder(UnitShape):
    
    @classmethod
    def name(cls):
        return gettext('Cylinder')
    
    
    def __init__(self, *args, **keywordArgs):
        Shape.__init__(self, *args, **keywordArgs)
        
        # TODO: use VBO's so all instances share the same data?
        
        steps = 32
        angleStep = 2.0 * pi / steps
        
        topVertices = []
        bottomVertices = []
        sideNormals = []
        for step in range(0, steps):
            angle = step * angleStep
            x, z = (sin(angle) * 0.5, cos(angle) * 0.5)
            topVertices += [(x, 0.5, z)]
            bottomVertices += [(x, -0.5, z)]
            sideNormals += [(x / 0.5, 0.0, z / 0.5)]
        vertices = [(0.0, 0.5, 0.0)] + topVertices
        vertexNormals = [(0.0, 1.0, 0.0)] * (steps + 1)
        textureCoords = [(1.0, 1.0)] + [(0.9, 0.9)] * steps
        for step in range(0, steps):
            vertices += [topVertices[step], bottomVertices[step]]
            vertexNormals += [sideNormals[step], sideNormals[step]]
            textureCoords += [(0.9, 0.9), (0.1, 0.1)]
        vertices += bottomVertices + [(0.0, -0.5, 0.0)]
        vertexNormals += [(0.0, -1.0, 0.0)] * (steps + 1)
        textureCoords += [(0.1, 0.1)] * steps + [(0.0, 0.0)]
        self.geometry().setVertexArray(Shape.vectorArrayFromList(vertices))
        
        faceSet = Shape.primitiveSetFromList(osg.PrimitiveSet.TRIANGLE_FAN, range(0, steps + 1) + [1, 0])
        self.geometry().addPrimitiveSet(faceSet)
        faceSet = Shape.primitiveSetFromList(osg.PrimitiveSet.QUAD_STRIP, range(steps + 1, 3 * steps + 1) + [steps + 1, steps + 2])
        self.geometry().addPrimitiveSet(faceSet)
        faceSet = Shape.primitiveSetFromList(osg.PrimitiveSet.TRIANGLE_FAN, [4 * steps + 1] + range(3 * steps + 1, 4 * steps + 1) + [3 * steps + 1, 4 * steps + 1])
        self.geometry().addPrimitiveSet(faceSet)
        
        self.geometry().setNormalArray(Shape.vectorArrayFromList(vertexNormals))
        self.geometry().setNormalBinding(osg.Geometry.BIND_PER_VERTEX)
        
        self.geometry().setTexCoordArray(0, Shape.vectorArrayFromList(textureCoords))
    
    
    def interiorBounds(self):
        halfSize = 0.5 / sqrt(2)
        return ((-halfSize, -0.5, -halfSize), (halfSize, 0.5, halfSize))
    
    
    def intersectionPoint(self, rayOrigin, rayDirection):
        # TODO
        return None
