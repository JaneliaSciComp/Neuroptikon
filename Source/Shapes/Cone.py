from Display.Shape import Shape, UnitShape
import osg
from math import pi, cos, sin, sqrt


class Cone(UnitShape):
    
    @classmethod
    def name(cls):
        return gettext('Cone')
    
    
    def __init__(self, *args, **keywordArgs):
        Shape.__init__(self, *args, **keywordArgs)
        
        # TODO: use VBO's so all instances share the same data?
        # TODO: should have separate vertex per angled face so they can have face-specific normals
        
        steps = 32
        angleStep = 2.0 * pi / steps
        
        vertices = [(0.0, 0.5, 0.0)]
        vertexNormals = [(0.0, 1.0, 0.0)]
        textureCoords = [(1.0, 1.0)]
        for increment in range(0, steps):
            angle = increment * angleStep
            vertex = (sin(angle) * 0.5, -0.5, cos(angle) * 0.5)
            vertices += [vertex]
            vertexNormals += [(vertex[0] / .7071, 0.0, vertex[2] / .7071)]
            textureCoords += [(0.1, 0.1)]
        vertices += vertices[1:steps + 1]
        vertices += [(0.0, -0.5, 0.0)]
        vertexNormals += [(0.0, -1.0, 0.0)] * (steps + 1)
        textureCoords += textureCoords[1:steps + 1]
        textureCoords += [(0.0, 0.0)]
        self.geometry().setVertexArray(Shape.vectorArrayFromList(vertices))
        
        faceSet = Shape.primitiveSetFromList(osg.PrimitiveSet.TRIANGLE_FAN, range(0, steps + 1) + [1, 0])
        self.geometry().addPrimitiveSet(faceSet)
        faceSet = Shape.primitiveSetFromList(osg.PrimitiveSet.TRIANGLE_FAN, [steps * 2 + 1] + range(steps + 1, steps * 2 + 1) + [steps + 1, steps * 2 + 1])
        self.geometry().addPrimitiveSet(faceSet)
        
        self.geometry().setNormalArray(Shape.vectorArrayFromList(vertexNormals))
        self.geometry().setNormalBinding(osg.Geometry.BIND_PER_VERTEX)
        
        self.geometry().setTexCoordArray(0, Shape.vectorArrayFromList(textureCoords))
    
    
    def interiorBounds(self):
        halfSize = sqrt(0.125) / 2.0
        return ((-halfSize, -0.5, -halfSize), (halfSize, 0.0, halfSize))
