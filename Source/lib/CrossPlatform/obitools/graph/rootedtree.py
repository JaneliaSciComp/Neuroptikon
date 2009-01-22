from obitools.graph.dag import DAG,DAGNode

class RootedTree(DAG):
    
    def addEdge(self,parent=None,node=None,indexp=None,index=None,**data):
        indexp=self.addNode(parent, indexp)
        index =self.addNode(node  , index)
        
        assert index not in self._parents,'Child node cannot have more than one parent node'
            
        return DAG.addEdge(self,indexp=indexp,index=index,**data)   

    def getNode(self,node=None,index=None):
        if index is None:
            index = self._index.getIndex(node, True)
        return RootedTreeNode(index,self)
    
class RootedTreeNode(DAGNode):

    def subTreeSize(self,node):
        n=1
        for subnode in self:
            n+=self.subTreeSize(subnode)
        return n
    