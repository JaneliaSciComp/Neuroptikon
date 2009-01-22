import math

from obitools.svg import Scene,Circle,Line,Rectangle,Text
from obitools.tree import Tree

def displayTreeLayout(layout,width=400,height=400,radius=3,scale=1.0):
    '''
    Convert a tree layout object in an svg file.
    
    @param layout: the tree layout object
    @type layout: obitools.tree.layout.TreeLayout
    @param width: svg document width
    @type width:  int
    @param height: svg document height
    @type height: int
    @param radius: default radius of node in svg unit (default 3)
    @type radius: int 
    @param scale: scale factor applied to the svg coordinates (default 1.0)
    @type scale: float
    
    @return: str containing svg code
    '''
    xmin = min(layout.getAttribute(n,'x') for n in layout)
    xmax = max(layout.getAttribute(n,'x') for n in layout)
    ymin = min(layout.getAttribute(n,'y') for n in layout)
    ymax = max(layout.getAttribute(n,'y') for n in layout)

    dx = xmax - xmin
    dy = ymax - ymin
    
    xscale = width * 0.95 / dx * scale
    yscale = height * 0.95 / dy * scale
    
    def X(x):
        return (x - xmin ) * xscale + width * 0.025
    
    def Y(y):
        return (y - ymin ) * yscale + height * 0.025
    
    scene = Scene('unrooted', height, width)
    
    for n in layout:
        if n._parent is not None:
            parent = n._parent
            xf = layout.getAttribute(n,'x')
            yf = layout.getAttribute(n,'y')
            xp = layout.getAttribute(parent,'x')
            yp = layout.getAttribute(parent,'y')
            scene.add(Line((X(xf),Y(yf)),(X(xp),Y(yp))))
            
    for n in layout:
        xf = layout.getAttribute(n,'x')
        yf = layout.getAttribute(n,'y')
        cf = layout.getAttribute(n,'color')
        sf = layout.getAttribute(n,'shape')
        if layout.hasAttribute(n,'radius'):
            rf=layout.getAttribute(n,'radius')
        else:
            rf=radius
            
        if sf=='circle':
            scene.add(Circle((X(xf),Y(yf)),rf,cf))
        else:
            scene.add(Rectangle((X(xf)-rf,Y(yf)-rf),2*rf,2*rf,cf))
            
        
    return ''.join(scene.strarray())

    
  