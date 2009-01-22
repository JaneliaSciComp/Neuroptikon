from obitools.tree.layout import TreeLayout
import math

def subtreeLayout(tree,node,layout,start,end,x,y,default):
    nbotu = tree.subTreeSize(node)
    delta = (end-start)/(nbotu+1)

    layout.addNode(node)
    layout.setAttribute(node,'x',x)
    layout.setAttribute(node,'y',y)
    layout.setAttribute(node,'color',(255,0,0))
    layout.setAttribute(node,'shape','circle')
    
    for subnode in tree.childNodeIterator(node):
        snbotu = tree.subTreeSize(subnode)
        end = start + snbotu * delta
        med = start + snbotu * delta /2
        r = subnode._dist
        if r is None or r <=0:
            r=default
        subx=math.cos(med) * r + x
        suby=math.sin(med) * r + y
        subtreeLayout(tree, subnode, layout, start, end, subx, suby, default)
        start=end
        
    return layout

def treeLayout(tree):
    layout = TreeLayout()
    root   = tree.getRoot()
    dmin = min(n._dist for n in tree if n._dist is not None and n._dist > 0)
    return subtreeLayout(tree,root,layout,0,2*math.pi,0,0,dmin / 100)
    