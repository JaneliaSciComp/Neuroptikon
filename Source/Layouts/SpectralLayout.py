from Display.Layout import Layout
from numpy import diag, mat, sign, inner, isinf, zeros
from numpy.linalg import pinv, eigh

class SpectralLayout(Layout):
    
    @classmethod
    def name(cls):
        return gettext('Spectral')
    
    
    def __init__(self, weightFunction = None, scaling = (1.0, 1.0, 1.0), autoScale = True, *args, **keywordArgs):
        Layout.__init__(self, *args, **keywordArgs)
    
        self.weightingFunction = weightFunction
        self.scaling = scaling
        self.autoScale = autoScale
    
    
    def layoutDisplay(self, display):
        nodes = []
        edges = []
        for visibles in display.visibles.itervalues():
            for visible in visibles:
                if visible.isPath():
                    edges.append(visible)
                elif visible.parent is None:
                    nodes.append(visible)
        n=len(nodes)
        if n > 1:
            # Build the adjacency matrix
            A = zeros((n, n))
            for edge in edges:
                (pathStart, pathEnd) = edge.pathEndPoints()
                n1 = nodes.index(pathStart.rootVisible())
                n2 = nodes.index(pathEnd.rootVisible())
                if self.weightingFunction is None:
                    weight = 1.0
                else:
                    weight = self.weightingFunction(edge)
                if edge.flowTo() is None or edge.flowTo():
                    A[n1, n2] = A[n1, n2] + weight
                if edge.flowFrom() is None or edge.flowFrom():
                    A[n2, n1] = A[n2, n1] + weight
            #print A.tolist()
            
            # This is equivalent to the MATLAB code from <http://mit.edu/lrv/www/elegans/>:
            #   c=full((A+A')/2);
            #   d=diag(sum(c));
            #   l=d-c;
            #   b=sum(c.*sign(full(A-A')),2);
            #   z=pinv(l)*b;
            #   q=d^(-1/2)*l*d^(-1/2);
            #   [vx,lambda]=eig(q);
            #   x=d^(-1/2)*vx(:,2);
            #   y=d^(-1/2)*vx(:,3);
            
            A_prime = A.T
            c = (A + A_prime) / 2.0
            d = diag(c.sum(0))
            l = mat(d - c)
            if display.viewDimensions == 2:
                z = zeros((n, 1))
            else:
                b = (c * sign(A - A_prime)).sum(1).reshape(1, n)
                z = inner(pinv(l), b)
            d2 = mat(d**-0.5)
            d2[isinf(d2)] = 0
            q = d2 * l * d2
            eVec = eigh(q)[1]
            x = d2 * mat(eVec[:,1])
            y = d2 * mat(eVec[:,2])
            xMin, xMax = x.min(), x.max()
            xOff = (xMax + xMin) / 2.0
            xSize = xMax - xMin if self.autoScale else 1.0
            yMin, yMax = y.min(), y.max()
            yOff = (yMax + yMin) / 2.0
            ySize = yMax - yMin if self.autoScale else 1.0
            zMin, zMax = z.min(), z.max()
            zOff = (zMax + zMin) / 2.0
            zSize = zMax - zMin if self.autoScale and zMax != zMin else 1.0
            for i in range(n):
                nodes[i].setPosition(((x[i,0] - xOff) / xSize * self.scaling[0], (y[i,0] - yOff) / ySize * self.scaling[1], (z[i,0] - zOff) / zSize * self.scaling[2]))
