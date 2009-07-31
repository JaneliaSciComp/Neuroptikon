from Display.Shape import Shape, UnitShape
import osg
from math import atan2, cos, pi, sin, sqrt


class Ring(UnitShape):
    
    @classmethod
    def name(cls):
        return gettext('Ring')
    
    
    def __init__(self, holeSize = 1.0 / 3.0, *args, **keywordArgs):
        Shape.__init__(self, *args, **keywordArgs)
        
        # TODO: use VBO's so all instances share the same data?
        
        self.holeSize = holeSize
        
        steps = 32
        angleIncrement = 2.0 * pi / steps
        
        # Duplicate vertices are created at the seams to avoid texture problems so steps + 1 segments and steps + 1 vertices per segment are created.
        
        segmentRadius = (1.0 - holeSize) / 4.0
        ringRadius = 0.5 - segmentRadius
        
        vertices = []
        normals = []
        texCoords = []
        for ringStep in range(0, steps + 1):
            ringAngle = ringStep * angleIncrement
            segmentCenter = (cos(ringAngle) * ringRadius, sin(ringAngle) * ringRadius, 0.0)
            for segmentStep in range(0, steps + 1):
                segmentAngle = segmentStep * angleIncrement
                segmentMag = cos(segmentAngle) * segmentRadius
                x, y, z, zNormal = (cos(ringAngle) * (ringRadius + segmentMag), sin(ringAngle) * (ringRadius + segmentMag), sin(segmentAngle) * 0.5, sin(segmentAngle) * segmentRadius)
                vertices += [(x, y, z)]
                normal = (x - segmentCenter[0], y - segmentCenter[1], zNormal - segmentCenter[2])
                normalMag = sqrt(normal[0] ** 2 + normal[1] ** 2 + normal[2] ** 2)
                normals += [(normal[0] / normalMag, normal[1] / normalMag, normal[2] / normalMag)]
                texCoords += [(float(ringStep) / steps, float(segmentStep) / steps)]
        
        self.geometry().setVertexArray(Shape.vectorArrayFromList(vertices))
        
        self.geometry().setNormalArray(Shape.vectorArrayFromList(normals))
        self.geometry().setNormalBinding(osg.Geometry.BIND_PER_VERTEX)
        
        self.geometry().setTexCoordArray(0, Shape.vectorArrayFromList(texCoords))
        
        for ringStep in range(0, steps):
            baseIndex = ringStep * (steps + 1)
            vertexIndices = []
            for segmentStep in range(0, steps + 1):
                vertexIndices += [baseIndex + segmentStep, baseIndex + steps + 1 + segmentStep]
            faceSet = Shape.primitiveSetFromList(osg.PrimitiveSet.QUAD_STRIP, vertexIndices)
            self.geometry().addPrimitiveSet(faceSet)
    
    
    def persistentAttributes(self):
        return {'holeSize': self.holeSize}
    

    def intersectionPoint(self, rayOrigin, rayDirection):
        # TODO: Do a real line/torus intersection: <http://tog.acm.org/resources/GraphicsGems/gemsii/intersect/inttor.c>
        
        # In the mean time use line/circle intersection code from <http://mathworld.wolfram.com/Circle-LineIntersection.html>
        if abs(rayOrigin[2]) < 1e-12 and abs(rayDirection[2]) < 1e-12:
            dr = sqrt(rayDirection[0] ** 2 + rayDirection[1] ** 2)
            dr2 = dr ** 2
            D = rayOrigin[0] * (rayOrigin[1] + rayDirection[1]) - (rayOrigin[0] + rayDirection[0]) * rayOrigin[1]
            sgn_dy = -1.0 if rayDirection[1] < 0.0 else 1.0
            bigPiece = sqrt(0.5 ** 2 * dr2 - D ** 2)
            intersections = []
            intersections += [((D * rayDirection[1] + sgn_dy * rayDirection[0] * bigPiece) / dr2, (-D * rayDirection[0] + abs(rayDirection[1]) * bigPiece) / dr2, 0.0)]
            intersections += [((D * rayDirection[1] + sgn_dy * rayDirection[0] * bigPiece) / dr2, (-D * rayDirection[0] - abs(rayDirection[1]) * bigPiece) / dr2, 0.0)]
            intersections += [((D * rayDirection[1] - sgn_dy * rayDirection[0] * bigPiece) / dr2, (-D * rayDirection[0] + abs(rayDirection[1]) * bigPiece) / dr2, 0.0)]
            intersections += [((D * rayDirection[1] - sgn_dy * rayDirection[0] * bigPiece) / dr2, (-D * rayDirection[0] - abs(rayDirection[1]) * bigPiece) / dr2, 0.0)]
            minDist = 1e300
            closestIntersection = None
            for intersection in intersections:
                distToOrigin = (intersection[0] - rayOrigin[0]) ** 2 + (intersection[1] - rayOrigin[1]) ** 2
                if distToOrigin < minDist:
                    closestIntersection = intersection
                    minDist = distToOrigin
            return closestIntersection
        else:
            return None