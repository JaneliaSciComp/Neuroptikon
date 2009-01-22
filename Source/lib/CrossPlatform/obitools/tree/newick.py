import re
import sys

from obitools.utils import universalOpen
from obitools.tree import Tree,TreeNode

def subNodeIterator(data):
    level=0
    start = 1
    if data[0]=='(':
        for i in xrange(1,len(data)):
            c=data[i]
            if c=='(':
                level+=1
            elif c==')':
                level-=1
            if c==',' and not level:
                yield data[start:i]
                start = i+1
        yield data[start:i]
    else:
        yield data
            
    
_nodeParser=re.compile('\s*(?P<subnodes>\(.*\))?(?P<name>[^ :]+)? *(?P<bootstrap>[0-9.]+)?(:(?P<distance>-?[0-9.]+))?')

def nodeParser(data):
    parsedNode = _nodeParser.match(data).groupdict(0)
    if not parsedNode['name']:
        parsedNode['name']=None

    if not parsedNode['bootstrap']:
        parsedNode['bootstrap']=None
    else:
        parsedNode['bootstrap']=float(parsedNode['bootstrap'])
    
    if not parsedNode['distance']:
        parsedNode['distance']=None
    else:
        parsedNode['distance']=float(parsedNode['distance'])
            
    if not parsedNode['subnodes']:
        parsedNode['subnodes']=None

    return parsedNode

_cleanTreeData=re.compile('\s+')
    
def treeParser(data,tree=None,parent=None):
    if tree is None:
        tree = Tree()
        data = _cleanTreeData.sub(' ',data).strip()
        
    parsedNode = nodeParser(data)
    node = TreeNode(tree,
                    parsedNode['name'],
                    parsedNode['distance'],
                    parsedNode['bootstrap'])
    
    node.linkToParent(parent)
    
    if parsedNode['subnodes']:
        for subnode in subNodeIterator(parsedNode['subnodes']):
            treeParser(subnode,tree,node)
    return tree

_treecomment=re.compile('\[.*\]')

def treeIterator(file):
    file = universalOpen(file)
    data = file.read()
    
    comment = _treecomment.findall(data)
    data=_treecomment.sub('',data).strip()
    
    if comment:
        comment=comment[0]
    else:
        comment=None
    for tree in data.split(';'):
        t = treeParser(tree)
        if comment:
            t.comment=comment
        yield t

def nodeWriter(tree,node,deep=0):
    name = node._name
    if name is None: 
        name=''
    
    distance=node._dist
    if distance is None:
        distance=''
    else:
        distance = ':%6.5f' % distance
        
    bootstrap=node._bootstrap
    if bootstrap is None:
        bootstrap=''
    else:
        bootstrap=' %d' % int(bootstrap)
        
    nodeseparator = ',\n' + ' ' * (deep+1)     
        
    subnodes = nodeseparator.join([nodeWriter(tree, x, deep+1) 
                        for x in tree.childNodeIterator(node)])
    if subnodes:
        subnodes='(\n' + ' ' * (deep+1) + subnodes + '\n' + ' ' * deep + ')'
        
    return '%s%s%s%s' % (subnodes,name,bootstrap,distance)

def treeWriter(tree,startnode=None):
    if startnode is not None:
        root=startnode
    else:
        root = tree.getRoot()
    return nodeWriter(tree,root)+';'
