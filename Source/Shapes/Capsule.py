from Display.Shape import Shape, UnitShape
import osg
from math import cos, pi, sin


class Capsule(UnitShape):
    
    @classmethod
    def name(cls):
        return gettext('Capsule')
    
    
    def __init__(self, capiness = 0.5, *args, **keywordArgs):
        Shape.__init__(self, *args, **keywordArgs)
        
        # TODO: use VBO's so all instances share the same data?
        # TODO: fix seams caused by texture coords
        
        self.capiness = capiness
        
        steps = 32  # must be multiple of four
        angleIncrement = 2.0 * pi / steps
        capSteps = steps / 4
        azimuthIncrement = pi / 2.0 / capSteps
        
        topVertices = []
        topTexCoords = []
        bottomVertices = []
        bottomTexCoords = []
        for azimuthStep in range(0, capSteps):
            topAzimuth = pi / 2.0 - (azimuthStep + 1) * azimuthIncrement
            topY, topMag = (sin(topAzimuth) * (capiness / 2.0), cos(topAzimuth) * 0.5)
            bottomAzimuth = -azimuthStep * azimuthIncrement
            bottomY, bottomMag = (sin(bottomAzimuth) * (capiness / 2.0), cos(bottomAzimuth) * 0.5)
            for step in range(0, steps):
                angle = pi + step * angleIncrement
                topVertices += [(sin(angle) * topMag, topY + (0.5 * (1.0 - capiness)), cos(angle) * topMag)]
                topTexCoords += [(float(step) / steps, topVertices[-1][1] + 0.5)]
                bottomVertices += [(sin(angle) * bottomMag, -(0.5 * (1.0 - capiness)) + bottomY, cos(angle) * bottomMag)]
                bottomTexCoords += [(float(step) / steps, bottomVertices[-1][1] + 0.5)]

        vertices = [(0.0, 0.5, 0.0)] + topVertices + bottomVertices + [(0.0, -0.5, 0.0)]
        self.geometry().setVertexArray(Shape.vectorArrayFromList(vertices))
        
        normals = []
        for vertex in vertices:
            normals += [(vertex[0] / 2.0, vertex[1] / 2.0, vertex[2] / 2.0)]
        self.geometry().setNormalArray(Shape.vectorArrayFromList(normals))
        self.geometry().setNormalBinding(osg.Geometry.BIND_PER_VERTEX)
        
        texCoords = [(0.0, 1.0)] + topTexCoords + bottomTexCoords + [(0.0, 0.0)]
        self.geometry().setTexCoordArray(0, Shape.vectorArrayFromList(texCoords))
        
        faceSet = Shape.primitiveSetFromList(osg.PrimitiveSet.TRIANGLE_FAN, range(0, steps + 1) + [1, 0])
        self.geometry().addPrimitiveSet(faceSet)
        for stripNum in range(0, 2 * capSteps - 1):
            vertexIndices = []
            baseIndex = 1 + stripNum * steps
            for step in range(steps) + [0]:
                vertexIndices += [baseIndex + step, baseIndex + steps + step]
            faceSet = Shape.primitiveSetFromList(osg.PrimitiveSet.QUAD_STRIP, vertexIndices)
            self.geometry().addPrimitiveSet(faceSet)
        bottomFanBaseIndex = len(vertices) - steps - 1
        faceSet = Shape.primitiveSetFromList(osg.PrimitiveSet.TRIANGLE_FAN, [len(vertices) - 1] + range(bottomFanBaseIndex, bottomFanBaseIndex + steps) + [bottomFanBaseIndex, len(vertices) - 1])
        self.geometry().addPrimitiveSet(faceSet)
    
    
    def persistentProperties(self):
        return {'capiness': self.capiness}
    
