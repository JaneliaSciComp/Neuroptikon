from Display.Layout import Layout
from numpy import diag, mat, sign, inner, isinf, zeros
from numpy.linalg import pinv, eigh

class SpectralLayout(Layout):
    
    @classmethod
    def name(cls):
        return gettext('Spectral')
    
    
    @classmethod
    def canLayoutDisplay(cls, display):
        return display.viewDimensions == 3
    
    
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
        if n > 0:
            # Build the adjacency matrix
            A = zeros((n, n))
            for edge in edges:
                n1 = nodes.index(edge.pathStart.rootVisible())
                n2 = nodes.index(edge.pathEnd.rootVisible())
                if edge.flowTo is None or edge.flowTo:
                    A[n1, n2] = A[n1, n2] + 1
                if edge.flowFrom is None or edge.flowFrom:
                    A[n2, n1] = A[n2, n1] + 1
            A_prime = A.T
            
            # This is equivalent to the spectral layout MATLAB code provided by Mitya:
            #   n=size(A,1);
            #   c=full((A+A')/2);
            #   d=diag(sum(c));
            #   l=d-c;
            #   b=sum(c.*sign(full(A-A')),2);
            #   z=pinv(c)*b;
            #   q=d^(-1/2)*l*d^(-1/2);
            #   [vx,lambda]=eig(q);
            #   x=d^(-1/2)*vx(:,2);
            #   y=d^(-1/2)*vx(:,3);
            
            c = (A + A_prime) / 2.0
            d = diag(c.sum(0))
            l = mat(d - c)
            b = (c * sign(A - A_prime)).sum(1).reshape(1, n)
            z = inner(pinv(c), b)
            d2 = mat(d**-0.5)
            d2[isinf(d2)] = 0
            q = d2 * l * d2
            (eVal, eVec) = eigh(q)
            x = d2 * mat(eVec[:,1])
            y = d2 * mat(eVec[:,2])
            xMin, xMax = x.min(), x.max()
            xScale = 1.0 / (xMax - xMin)
            xOff = (xMax + xMin) / 2.0
            yMin, yMax = y.min(), y.max()
            yScale = 1.0 / (yMax - yMin)
            yOff = (yMax + yMin) / 2.0
            zMin, zMax = z.min(), z.max()
            zScale = 1.0 / (zMax - zMin)
            zOff = (zMax + zMin) / 2.0
            for i in range(n):
                nodes[i].setPosition(((x[i,0] - xOff) * xScale, (y[i,0] - yOff) * yScale, (z[i,0] - zOff) * zScale))
