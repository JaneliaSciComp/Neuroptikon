
from obitools.graph.tree import Forest,TreeNode
from obitools.graph import Edge



class PhylogenicTree(Forest):
    
    def __init__(self,label='G',indexer=None,nodes=None,edges=None):
        Forest.__init__(self, label, indexer, nodes, edges)
        self.root=None
        self.comment=None
        
    def addNode(self,node=None,index=None,**data):
        if node is None and index is None:
            node = '__%d' % (len(self._node)+1)
            
        return Forest.addNode(self, node, index, **data)

    def getNode(self,node=None,index=None):
        if index is None:
            index = self._index.getIndex(node, True)
        return PhylogenicNode(index,self)
    
    def getEdge(self,node1=None,node2=None,index1=None,index2=None):
        '''
        
        @param node1:
        @type node1:
        @param node2:
        @type node2:
        @param index1:
        @type index1:
        @param index2:
        @type index2:
        '''
        node1=self.getNode(node1, index1)
        node2=self.getNode(node2, index2)
        return PhylogenicEdge(node1,node2)

    

class PhylogenicNode(TreeNode):
    
    def getLabel(self):
        label = TreeNode.getLabel(self)
        if label[0:2]=='__':
            return None
        else:
            return label

    def __str__(self):
        
        if self.index in self.graph._node_attrs:
            keys = " ".join(['%s="%s"' % (x[0],str(x[1]).replace('"','\\"'))
                              for x in self.graph._node_attrs[self.index].iteritems()]
                           )
        else:
            keys=''
            
        if self.label is None:
            label=''
            shape='point'
        else:
            label=self.label
            shape='box'
            
        return '%d  [label="%s" shape="%s" %s]' % (self.index,str(label).replace('"','\\"'),shape,keys)   
    
    def distanceTo(self,node=None,index=None):  
        '''
        compute branch length between the two nodes.
        If distances are not secified for this tree, None is returned.
        
        @param node: a node label or None
        @param index: a node index or None. the parameter index  
                     has a priority on the parameter node.
        @type index: int
        
        @return: the evolutive distance between the two nodes
        @rtype: int, float or None
        '''
        path = self.shortestPathTo(node, index)
        
        start = path.pop(0)
        dist=0
        for dest in path:
            edge = self.graph.getEdge(index1=start,index2=dest)
            if 'distance' in edge:
                dist+=edge['distance']
            else:
                return None
            start=dest
            
        return dist

    label = property(getLabel, None, None, "Label of the node")

class PhylogenicEdge(Edge):
    
    def __str__(self):
        e = (self.node1.index,self.node2.index)
        if e in self.graph._edge_attrs:
            keys = "[%s]" % " ".join(['%s="%s"' % (x[0],str(x[1]).replace('"','\\"'))
                                      for x in self.graph._edge_attrs[e].iteritems()
                                      if x[0] not in ('distance','bootstrap')]
                                    )
        else:
            keys = ""
            
        
                           
        if self.directed:
            link='->'
        else:
            link='--'
            
        return "%d %s %d %s" % (self.node1.index,link,self.node2.index,keys) 
        
