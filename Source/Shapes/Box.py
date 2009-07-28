from Display.Shape import Shape, UnitShape
import osg


class Box(UnitShape):
    
    @classmethod
    def name(cls):
        return gettext('Box')
    
    
    def __init__(self, *args, **keywordArgs):
        Shape.__init__(self, *args, **keywordArgs)
        
        # TODO: use VBO's so all instances share the same data?
        # TODO: texture coordinates
        
        vertices = [(-0.5, -0.5, -0.5), (-0.5, -0.5,  0.5), (-0.5,  0.5, -0.5), (-0.5,  0.5,  0.5), ( 0.5, -0.5, -0.5), ( 0.5, -0.5,  0.5), ( 0.5,  0.5, -0.5), ( 0.5,  0.5,  0.5)]
        self.geometry().setVertexArray(Shape.vectorArrayFromList(vertices))
        
        faceNormals = [(-1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (1.0, 0.0, 0.0), (0.0, -1.0, 0.0), (0.0, 0.0, 1.0), (0.0, 0.0, -1.0)]
        self.geometry().setNormalArray(Shape.vectorArrayFromList(faceNormals))
        self.geometry().setNormalBinding(osg.Geometry.BIND_PER_PRIMITIVE_SET)
        
        facesVertices = [(0, 1, 3, 2), (2, 3, 7, 6), (6, 7, 5, 4), (4, 5, 1, 0), (3, 1, 5, 7), (0, 2, 6, 4)]
        for faceVertices in facesVertices:
            faceSet = Shape.primitiveSetFromList(osg.PrimitiveSet.QUADS, faceVertices)
            self.geometry().addPrimitiveSet(faceSet)
    
    
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
                tmin += [1e1000 if rayOrigin[dim] <= -0.5 else -1e1000]
                tmax += [1e1000 if rayOrigin[dim] <=  0.5 else -1e1000]
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
    
