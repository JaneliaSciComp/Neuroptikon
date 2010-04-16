#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

from display.shape import Shape, UnitShape
import osg


class Box(UnitShape):
    
    @classmethod
    def name(cls):
        return gettext('Box')
    
    
    def __init__(self, *args, **keywordArgs):
        UnitShape.__init__(self, *args, **keywordArgs)
        
        # TODO: use VBO's so all instances share the same data?
        
        baseVertices = [(-0.5, -0.5, -0.5), (-0.5, -0.5,  0.5), (-0.5,  0.5, -0.5), (-0.5,  0.5,  0.5), ( 0.5, -0.5, -0.5), ( 0.5, -0.5,  0.5), ( 0.5,  0.5, -0.5), ( 0.5,  0.5,  0.5)]
        
        vertices = []
        faceNormals = []
        texCoords = []
        for (v0, v1, v2, v3, normal) in [(0, 1, 3, 2, (-1.0, 0.0, 0.0)), (2, 3, 7, 6, (0.0, 1.0, 0.0)), (6, 7, 5, 4, (1.0, 0.0, 0.0)), (4, 5, 1, 0, (0.0, -1.0, 0.0)), (3, 1, 5, 7, (0.0, 0.0, 1.0)), (0, 2, 6, 4, (0.0, 0.0, -1.0))]:
            vertices += [baseVertices[v0], baseVertices[v1], baseVertices[v2], baseVertices[v3]]
            faceNormals += [normal]
            texCoords += [(0, 1), (0, 0), (1, 0), (1, 1)]
            faceSet = Shape.primitiveSetFromList(osg.PrimitiveSet.QUADS, [len(vertices) - 4, len(vertices) - 3, len(vertices) - 2, len(vertices) - 1])
            self.geometry().addPrimitiveSet(faceSet)
        
        self.geometry().setVertexArray(Shape.vectorArrayFromList(vertices))
        self.geometry().setNormalArray(Shape.vectorArrayFromList(faceNormals))
        self.geometry().setNormalBinding(osg.Geometry.BIND_PER_PRIMITIVE_SET)
        self.geometry().setTexCoordArray(0, Shape.vectorArrayFromList(texCoords))
    
    
    def interiorBounds(self):
        return ((-0.5, -0.5, -0.5), (0.5, 0.5, 0.5))
    
    
    def intersectionPoint(self, rayOrigin, rayDirection):
        tmin = []
        tmax = []
        for dim in range(0, 3):
            if rayDirection[dim] > 0.0:
                tmin += [(-0.5 - rayOrigin[dim]) / rayDirection[dim]]
                tmax += [( 0.5 - rayOrigin[dim]) / rayDirection[dim]]
            elif rayDirection[dim] < 0.0:
                tmin += [( 0.5 - rayOrigin[dim]) / rayDirection[dim]]
                tmax += [(-0.5 - rayOrigin[dim]) / rayDirection[dim]]
            else:   # rayDirection[dim] == 0.0
                tmin += [1e300 if rayOrigin[dim] <= -0.5 else -1e300]
                tmax += [1e300 if rayOrigin[dim] <=  0.5 else -1e300]
        if tmin[0] > tmax[1] or tmin[1] > tmax[0]:
            return None
        if tmin[1] > tmin[0]:
            tmin[0] = tmin[1]
        if tmax[1] < tmax[0]:
            tmax[0] = tmax[1]
        if tmin[0] > tmax[2] or tmin[2] > tmax[0]:
            return None
        if tmin[2] > tmin[0]:
            tmin[0] = tmin[2]
        if tmax[2] < tmax[0]:
            tmax[0] = tmax[2]
        return (rayOrigin[0] + rayDirection[0] * tmin[0], rayOrigin[1] + rayDirection[1] * tmin[0], rayOrigin[2] + rayDirection[2] * tmin[0])
    