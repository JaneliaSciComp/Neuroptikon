
from obitools.utils import universalOpen
from obitools.tree import Tree,TreeNode

def nodeWriter(tree,node,nodes):
    data=[]
    if node._parent:
       data.append('%d -> %d ' % (nodes[node],nodes[node._parent]))
    return "\n".join(data)


def treeWriter(tree):
    nodes=dict(map(None,tree,xrange(len(tree))))
    code=[]
    for node in tree:
        code.append(nodeWriter(tree,node,nodes)) 
    code = "\n".join(code)
    return 'digraph tree { node [shape=point]\n%s\n};' % code