import re

    
class Tree(set):
    def registerNode(self,node):
        assert isinstance(node, TreeNode)
        self.add(node)
        
    def childNodeIterator(self,node):
        assert isinstance(node, TreeNode)
        return (x for x in self if x._parent==node)
    
    def subTreeSize(self,node):
        n=1
        for subnode in self.childNodeIterator(node):
            n+=self.subTreeSize(subnode)
        return n
    
    def getRoot(self):
        roots = [x for x in self if x._parent is None]
        assert len(roots)==1,'Tree cannot have several root node'
        return roots[0]

    def ancestorNodeIterator(self,node):
        assert isinstance(node, TreeNode)
        while node._parent is not None:
            yield node
            node=node._parent
        yield node
    
    def terminalNodeIterator(self):
        return (x for x in self if x._isterminal)
            
    def commonAncestor(self,node1,node2):
        anc1 = set(x for x in self.ancestorNodeIterator(node1))
        rep  = [x for x in self.ancestorNodeIterator(node2)
                  if x in anc1]
        assert len(rep)>=1
        return rep[0]
    
    def getDist(self,node1,node2):
        ca = self.commonAncestor(node1, node2)
        dist = 0
        while node1 != ca:
            dist+=node1._dist
            node1=node1._parent
        while node2 != ca:
            dist+=node2._dist
            node2=node2._parent
        return dist
    
    def farestNodes(self):
        dmax=0
        n1=None
        n2=None
        for node1 in self.terminalNodeIterator():
            for node2 in self.terminalNodeIterator():
                d = self.getDist(node1, node2)
                if d > dmax:
                    dmax = d
                    n1=node1
                    n2=node2
        return node1,node2,dmax
            
    def setRoot(self,node,dist):
        assert node in self 
        assert node._parent and node._dist > dist
        
        newroot = TreeNode(self)
        parent  = node._parent
        node._parent = newroot
        compdist = node._dist - dist
        node._dist=dist
        node = parent
        
        while node:
            parent  = node._parent
            if parent:
                dist    = node._dist
            
            node._parent = newroot
            node._dist = compdist

            newroot = node
            node    = parent
            
            if node:
                compdist=dist
                                
        for child in self.childNodeIterator(newroot):
            child._parent = newroot._parent
            child._dist  += newroot._dist
            
        self.remove(newroot)
            
    
class TreeNode(object):
    def __init__(self,tree,name=None,dist=None,bootstrap=None,**info):
        self._parent=None
        self._name=name
        self._dist=dist
        self._bootstrap=bootstrap
        self._info=info
        tree.registerNode(self)
        self._isterminal=True
        
        
    def linkToParent(self,parent):
        assert isinstance(parent, TreeNode) or parent is None
        self._parent=parent
        if parent is not None:
            parent._isterminal=False
        


    
