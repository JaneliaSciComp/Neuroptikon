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
    
