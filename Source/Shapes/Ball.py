from Display.Shape import Shape, UnitShape
import osg
from math import atan2, pi, sqrt


class Ball(UnitShape):
    
    @classmethod
    def name(cls):
        return gettext('Ball')
    
    # Cached values indexed by tesselation level
    _vertices = []
    _vertexArray = []
    _normalArray = []
    _texCoordArray = []
    _faces = []
    _faceSet = []
    
    @classmethod
    def _tessellate(cls):
        # Code inspired by Chapter 2 of the OpenGL Red Book.
        
        if not any(Ball._vertices):
            # Start with an icosahedron
            X = .525731112119133606 * 0.5
            Z = .850650808352039932 * 0.5
            newVertices = [(-X, 0.0, Z), (X, 0.0, Z), (-X, 0.0, -Z), (X, 0.0, -Z), (0.0, Z, X), (0.0, Z, -X), (0.0, -Z, X), (0.0, -Z, -X), (Z, X, 0.0), (-Z, X, 0.0), (Z, -X, 0.0), (-Z, -X, 0.0)]
            newFaces = [(0,4,1), (0,9,4), (9,5,4), (4,5,8), (4,8,1), (8,10,1), (8,3,10), (5,3,8), (5,2,3), (2,7,3), (7,10,3), (7,6,10), (7,11,6), (11,0,6), (0,1,6), (6,1,10), (9,0,11), (9,11,2), (9,2,5), (7,2,11)]
        else:
            # Subdivide each triangular face into four triangular sub-faces by finding the midpoint of each side.
            # New vertices will be added to a copy of the existing list and a completely new set of faces will be produced.
            newVertices = list(Ball._vertices[-1])
            newFaces = []
            for face in Ball._faces[-1]:
                index0 = face[0]
                vertex0 = newVertices[index0]
                index1 = face[1]
                vertex1 = newVertices[index1]
                index2 = face[2]
                vertex2 = newVertices[index2]
                
                # Add a new vertex between vertex 0 and vertex 1.
                vertex3 = (vertex0[0] + vertex1[0], vertex0[1] + vertex1[1], vertex0[2] + vertex1[2])
                mag = sqrt(vertex3[0] ** 2 + vertex3[1] ** 2 + vertex3[2] ** 2) * 2.0
                vertex3 = (vertex3[0] / mag, vertex3[1] / mag, vertex3[2] / mag)
                try:
                    index3 = newVertices.index(vertex3)
                except:
                    newVertices += [vertex3]
                    index3 = len(newVertices) - 1
                
                # Add a new vertex between vertex 1 and vertex 2.
                vertex4 = (vertex1[0] + vertex2[0], vertex1[1] + vertex2[1], vertex1[2] + vertex2[2])
                mag = sqrt(vertex4[0] ** 2 + vertex4[1] ** 2 + vertex4[2] ** 2) * 2.0
                vertex4 = (vertex4[0] / mag, vertex4[1] / mag, vertex4[2] / mag)
                try:
                    index4 = newVertices.index(vertex4)
                except:
                    newVertices += [vertex4]
                    index4 = len(newVertices) - 1
                
                # Add a new vertex between vertex 0 and vertex 2.
                vertex5 = (vertex0[0] + vertex2[0], vertex0[1] + vertex2[1], vertex0[2] + vertex2[2])
                mag = sqrt(vertex5[0] ** 2 + vertex5[1] ** 2 + vertex5[2] ** 2) * 2.0
                vertex5 = (vertex5[0] / mag, vertex5[1] / mag, vertex5[2] / mag)
                try:
                    index5 = newVertices.index(vertex5)
                except:
                    newVertices += [vertex5]
                    index5 = len(newVertices) - 1
                
                # Add the four new faces.
                newFaces += [(index0, index3, index5), (index3, index1, index4), (index3, index4, index5), (index5, index4, index2)]
        
        Ball._vertices += [newVertices]
        Ball._vertexArray += [Shape.vectorArrayFromList(newVertices)]
        
        normals = []
        texCoords = []
        for vertex in newVertices:
            normals += [(vertex[0] * 2.0, vertex[1] * 2.0, vertex[2] * 2.0)]
            texCoords += [(vertex[0] + 0.5, vertex[2] + 0.5)] #[(atan2(vertex[2], vertex[0]) / pi / 2.0 + 0.5, atan2(vertex[2], vertex[1]) / pi / 2.0 + 0.5)]
        Ball._normalArray += [Shape.vectorArrayFromList(normals)]
        Ball._texCoordArray += [Shape.vectorArrayFromList(texCoords)]
        
        Ball._faces += [newFaces]
        faceVertices = []
        for face in newFaces:
            faceVertices += face
        Ball._faceSet += [Shape.primitiveSetFromList(osg.PrimitiveSet.TRIANGLES, faceVertices)]
        
    
    @classmethod
    def _geometryAtTessellation(cls, tessellation):
        while len(Ball._vertices) <= tessellation:
            Ball._tessellate()
        return (Ball._vertexArray[tessellation], Ball._normalArray[tessellation], Ball._texCoordArray[tessellation], Ball._faceSet[tessellation])
    
    
    def __init__(self, tessellation = 1, *args, **keywordArgs):
        Shape.__init__(self, *args, **keywordArgs)
        
        self.tessellation = tessellation
        vertices, normals, texCoords, faceSet = Ball._geometryAtTessellation(tessellation)
        self.geometry().setVertexArray(vertices)
        self.geometry().setNormalArray(normals)
        self.geometry().setNormalBinding(osg.Geometry.BIND_PER_VERTEX)
        self.geometry().setTexCoordArray(0, texCoords)
        self.geometry().addPrimitiveSet(faceSet)
    
    
    def interiorBounds(self):
        halfSize = 0.5 / sqrt(3)
        return ((-halfSize, -halfSize, -halfSize), (halfSize, halfSize, halfSize))
