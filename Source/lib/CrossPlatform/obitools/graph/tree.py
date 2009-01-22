from obitools.graph import UndirectedGraph,Node
from obitools.graph.algorithms.component import componentCount


class Forest(UndirectedGraph):

 
    def getNode(self,node=None,index=None):
        if index is None:
            index = self._index.getIndex(node, True)
        return TreeNode(index,self)
   
    def addEdge(self,node1=None,node2=None,index1=None,index2=None,**data):
        index1=self.addNode(node1, index1)
        index2=self.addNode(node2, index2)
        
        cc = set(n.index for n in self.getNode(index=index2).componentIterator())
        
        assert index1 in self._node[index2] or index1 not in cc, \
               "No more than one path is alloed between two nodes in a tree"
        
        UndirectedGraph.addEdge(self, index1=index1, index2=index2,**data)
                
        return (index1,index2)
    
    def isASingleTree(self):
        return componentCount(self)==1
   
class TreeNode(Node):
    
    def componentIterator(self):
        for c in self:
            yield c
            for cc in c:
                yield cc
            
                