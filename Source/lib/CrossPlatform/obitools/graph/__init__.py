'''
This module offert classes to manipulate graphs
'''

import sys


from obitools.utils import progressBar


class Indexer(dict):
    '''
    Allow to manage convertion between an arbitrarly hashable python
    value and an unique integer key 
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
        self.__max=0
        self.__reverse=[]
        
    def getLabel(self,index):
        '''
        Return the python value associated to an integer index.
        
        @param index: an index value
        @type index: integer
        
        @raise IndexError: if the index is not used in this 
                           Indexer instance
        '''
        return self.__reverse[index]
    
    def getIndex(self,key,strict=False):
        if dict.__contains__(self,key):
            return dict.__getitem__(self,key)
        elif strict:
            raise KeyError,key
        else:
            value = self.__max
            self[key]= value
            self.__reverse.append(key)
            self.__max+=1
            return value
            
    def __getitem__(self,key):
        '''
        Return the integer key associated to a python value.
        
        @param key: the value to index
        @type key: an hashable python value
        @return: an unique integer value associated to the key
        @rtype: int
        
        '''
        return self.getIndex(key)
        
    def __equal__(self,index):
        '''
        Implement equa operator. Two Indexer instances are
        equals if they are physically the same instance
        @param index: the seconde Indexer
        @type index: an Indexer instance
        
        @return: True is the two instances are the same
        @rtype: bool
        '''
        return id(self)==id(index)
        
        
class Graph(object):
    '''
    Class used to represent directed or undirected graph.
    
    Only one edge can connect two nodes
    '''
    def __init__(self,label='G',directed=False,indexer=None,nodes=None,edges=None):
        '''
        Graph constructor.

        @param label: Graph name, set to 'G' by default
        @type label: str
        @param directed: true for directed graph, set to False by defalt
        @type directed: boolean
        @param indexer: node label indexer
        @type indexer: Indexer instance
        @param nodes: set of nodes to add to the graph
        @type nodes: iterable value
        @param edges: set of edges to add to the graph
        @type edges: iterable value
        '''
        self._directed=directed
        if indexer is None:
            indexer = Indexer()
        self._index = indexer
        self._node = {}
        self._node_attrs = {} 
        self._edge_attrs = {}
        self._label=label
        
    def newEmpty(self):
        n = Graph(self._label+"_compact",self._directed,self._index)
        return n
        
    def addNode(self,node=None,index=None,**data):
        if index is None:
            index = self._index[node]

        if index not in self._node:
            self._node[index]=set()

        if data:
            if index in self._node_attrs:
                self._node_attrs[index].update(data)
            else:
                self._node_attrs[index]=dict(data)
        return index
            
    def getNode(self,node=None,index=None):
        if index is None:
            index = self._index.getIndex(node, True)
        return Node(index,self)
    
    def getBestNode(self,estimator):
        bestScore=0
        best=None
        for n in self:
            score = estimator(n)
            if best is None or score > bestScore:
                bestScore = score
                best=n
        return best
            
    
    def delNode(self,node=None,index=None):
        if index is None:
            index = self._index[node]
        for n in self._node:
            if n!=index:
                e = self._node[n]
                if index in e:
                    if (n,index) in self._edge_attrs:
                        del self._edge_attrs[(n,index)]
                    e.remove(index)
        e = self._node[index]
        for n in e:
            if (index,n) in self._edge_attrs:
                del self._edge_attrs[(index,n)]
        del self._node[index]
        if index in self._node_attrs:
            del self._node_attrs[index]
                
                    
    def addEdge(self,node1=None,node2=None,index1=None,index2=None,**data):
        index1=self.addNode(node1, index1)
        index2=self.addNode(node2, index2)
        
        self._node[index1].add(index2)
        
        if not self._directed:
            self._node[index2].add(index1)
        
        if data:
            if (index1,index2) not in self._edge_attrs: 
                data =dict(data) 
                self._edge_attrs[(index1,index2)]=data   
                if not self._directed:
                    self._edge_attrs[(index2,index1)]=data
            else:
                self._edge_attrs.update(data)
                
        return (index1,index2)
    
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
        return Edge(node1,node2)
    
    def delEdge(self,node1=None,node2=None,index1=None,index2=None):
        if index1 is None:
            index1 = self._index[node1]
        if index2 is None:
            index2 = self._index[node2]
        if index1 in self._node and index2 in self._node[index]:
            self._node[index1].remove(index2)
            if (index1,index2) in self._node_attrs:
                del self._node_attrs[(index1,index2)]
            if not self._directed:
                self._node[index2].remove(index1)
                if (index2,index1) in self._node_attrs:
                    del self._node_attrs[(index2,index1)]
                    
    def edgeIterator(self,predicat=None):
        for n1 in self._node:
            for n2 in self._node[n1]:
                if self._directed or n1 <= n2:
                    e = self.getEdge(index1=n1, index2=n2) 
                    if predicat is None or predicat(e):
                        yield e
                    
        
    def nodeIterator(self,predicat=None):
        for n in self._node:
            node = self.getNode(index=n)
            if predicat is None or predicat(node):
                yield node
            
    def nodeIndexIterator(self,predicat=None):
        for n in self._node:
            node = self.getNode(index=n)
            if predicat is None or predicat(node):
                yield n
            
    def neighbourIndexSet(self,node=None,index=None):
        if index is None:
            index=self.getNode(node).index
        return self._node[index]
    
    def edgeCount(self):
        n = reduce(lambda x,y:x+y, (len(z) for z in self._node.itervalues()),0)
        if not self._directed:
            n=n/2
        return n
               
    def subgraph(self,nodes,name='G'):
        sub = Graph(name,self._directed,self._index)
        if not isinstance(nodes, set):
            nodes = set(nodes)
        for n in nodes:
            sub._node[n]=nodes & self._node[n]
            if n in self._node_attrs:
                sub._node_attrs[n]=dict(self._node_attrs)
            for n2 in sub._node[n]:
                if not self._directed:
                    if n < n2:
                        if (n,n2) in self._edge_attrs:
                            data=dict(self._edge_attrs[(n,n2)])
                            sub._edge_attrs[(n,n2)]=data
                            sub._edge_attrs[(n2,n)]=data
                else:
                    if (n,n2) in self._edge_attrs:
                        data=dict(self._edge_attrs[(n,n2)])
                        sub._edge_attrs[(n,n2)]=data
        return sub
        
    def __len__(self):
        return len(self._node)
    
    def __getitem__(self,key):
        return self.getNode(node=key)
    
    def __delitem__(self,key):
        self.delNode(node=key)
    
    def __iter__(self):
        return self.nodeIterator()
    
    def __str__(self):
        if self._directed:
            kw ='digraph'
        else:
            kw='graph'
            
        nodes = "\n    ".join([str(x) for x in self])
        edges = "\n    ".join([str(x) for x in self.edgeIterator()])
        
        return "%s %s {\n    %s\n\n    %s\n}" % (kw,self._label,nodes,edges)
        
class Node(object):
    def __init__(self,index,graph):
        '''
        Constructor on Node instance. 
        
        Normaly this constructor is only used by Graph methods.
        
        @param index: Index of the node in the graph
        @type index:  int
        @param graph: graph instance owning the node
        @type graph:  obitools.graph.Graph
        '''
        self.index = index
        self.__graph = graph

    def getGraph(self):
        '''
        return graph owning this node.
        
        @rtype: L{obitools.graph.Graph}
        '''
        return self.__graph


    def getLabel(self):
        '''
        return label associated to this node.
        '''
        return self.__graph._index.getLabel(self.index)

        
    def has_key(self,key):
        '''
        test is the node instance has a property named 'key'.
        
        @param key: the name of a property
        @type key: str
        
        @return: True if the nade has a property named <key>
        @rtype: bool
        '''
        if self.index in self.__graph._node_attrs:
            return key in self.__graph._node_attrs[self.index]
        else:
            return False
        
    def neighbourIterator(self,nodePredicat=None,edgePredicat=None):
        '''
        iterate through the nodes directly connected to
        this node.
        
        @param nodePredicat: a function accepting one node as parameter
                         and returning True if this node must be
                         returned by the iterator.
        @type nodePredicat: function
        
        @param edgePredicat: a function accepting one edge as parameter
                         and returning True if the edge linking self and
                         the current must be considered.
        @type edgePredicat: function
        
        
        @rtype: iterator on Node instances
        '''
        for n in self.neighbourIndexIterator(nodePredicat, edgePredicat):
            node = self.graph.getNode(index=n)
            yield node
            
    def neighbourIndexSet(self):
        '''
        Return a set of node indexes directely connected
        to this node.
        
        @attention: do not change this set unless you know
                    exactly what you do.
                    
        @rtype: set of int
        '''
        return self.__graph._node[self.index]

    def neighbourIndexIterator(self,nodePredicat=None,edgePredicat=None):
        '''
        iterate through the node indexes directly connected to
        this node.
        
        @param nodePredicat: a function accepting one node as parameter
                         and returning True if this node must be
                         returned by the iterator.
        @type nodePredicat: function
        
        @param edgePredicat: a function accepting one edge as parameter
                         and returning True if the edge linking self and
                         the current must be considered.
        @type edgePredicat: function
        
        @rtype: iterator on int
        '''
        for n in self.neighbourIndexSet():
            if nodePredicat is None or nodePredicat(self.__graph.getNode(index=n)):
                if edgePredicat is None or edgePredicat(self.__graph.getEdge(index1=self.index,index2=n)):
                    yield n

    def degree(self,nodeIndexes=None):
        '''
        return count of edges linking this node to the
        set of nodes describes by their index in  nodeIndexes
        
        @param nodeIndexes: set of node indexes. 
                            if set to None, all nodes of the
                            graph are take into account.
                            Set to None by default.
        @type nodeIndexes:  set of int
        
        @rtype: int
        '''
        if nodeIndexes is None:
            return len(self.__graph._node[self.index])
        else:
            return len(self.__graph._node[self.index] & nodeIndexes)
        
    def componentIndexSet(self,nodePredicat=None,edgePredicat=None):
        '''
        Return the set of node index in the same connected component.
        
        @param nodePredicat: a function accepting one node as parameter
                         and returning True if this node must be
                         returned by the iterator.
        @type nodePredicat: function
        
        @param edgePredicat: a function accepting one edge as parameter
                         and returning True if the edge linking self and
                         the current must be considered.
        @type edgePredicat: function
        

        @rtype: set of int
        '''
        cc=set([self.index])
        added = set(x for x in self.neighbourIndexIterator(nodePredicat, edgePredicat))
        while added:
            cc |= added
            added = reduce(lambda x,y : x | y,
                           (set(z for z in self.graph.getNode(index=c).neighbourIndexIterator(nodePredicat, edgePredicat)) 
                                for c in added),
                           set())
            added -= cc
        return cc
        
    def componentIterator(self,nodePredicat=None,edgePredicat=None):
        '''
        Iterate through the nodes in the same connected
        component.
        
        @rtype: iterator on L{Node} instance
        '''
        for c in self.componentIndexSet(nodePredicat, edgePredicat):
            yield self.graph.getNode(c)
        
    def shortestPathIterator(self,nodes=None):
        '''
        Iterate through the shortest path sourcing
        from this node. if nodes is not None, iterates
        only path linkink this node to one node listed in
        nodes
        
        @param nodes: set of node index
        @type nodes: iterable on int
        
        @return: an iterator on list of int describing path
        @rtype: iterator on list of int
        '''
        if nodes is not None:
            nodes = set(nodes)
        
        
        Q=[(self.index,-1)]
        
        gray = set([self.index])
        paths = {}
        
        while Q and (nodes is None or nodes):
            u,p = Q.pop()
            paths[u]=p
            next = self.graph._node[u] - gray
            gray|=next
            Q.extend((x,u) for x in next)
            if nodes is None or u in nodes:
                if nodes:
                    nodes.remove(u)
                path = [u]
                while p >= 0:
                    path.append(p)
                    p = paths[p]
                path.reverse()
                yield path
            
    def shortestPathTo(self,node=None,index=None):
        '''
        return one of the shortest path linking this
        node to specified node.
        
        @param node: a node label or None
        @param index: a node index or None. the parameter index  
                     has a priority on the parameter node.
        @type index: int
        
        @return: list of node index corresponding to the path or None
                 if no path exists.
        @rtype: list of int or None 
        '''
        if index is None:
            index=self.graph.getNode(node).index
        for p in self.shortestPathIterator([index]):
            return p

        
    def __getitem__(self,key):
        '''
        return the value of the <key> property of this node
        
        @param key: the name of a property
        @type key: str
        '''
        return self.__graph._node_attrs.get(self.index,{})[key]
    
    def __setitem__(self,key,value):
        '''
        set the value of a node property. In the property doesn't
        already exist a new property is added to this node.
        
        @param key: the name of a property
        @type key: str
        @param value: the value of the property
        
        @see: L{Node.__getitem__}
        '''
        if self.index in self.__graph._node_attrs:
            data = self.__graph._node_attrs[self.index]
            data[key]=value
        else:
            self.graph._node_attrs[self.index]={key:value}
            
    def __len__(self):
        '''
        Count neighbour of this node
        
        @rtype: int
        
        @see:  L{Node.degree}
        '''
        return len(self.__graph._node[self.index])
    
    def __iter__(self):
        '''
        iterate through neighbour of this node
        
        @rtype: iterator in L{Node} instances
        
        @see: L{Node.neighbourIterator}
        '''
        return self.neighbourIterator()
        
    def __contains__(self,key):
        return self.has_key(key)
        
    def __str__(self):
        
        if self.index in self.__graph._node_attrs:
            keys = " ".join(['%s="%s"' % (x[0],str(x[1]).replace('"','\\"').replace('\n','\\n'))
                              for x in self.__graph._node_attrs[self.index].iteritems()]
                           )
        else:
            keys=''
            
        return '%d  [label="%s" %s]' % (self.index,str(self.label).replace('"','\\"').replace('\n','\\n'),keys)       

    label = property(getLabel, None, None, "Label of the node")

    graph = property(getGraph, None, None, "Graph owning this node")
            
        
    
class Edge(object):
    def __init__(self,node1,node2):
        self.node1 = node1
        self.node2 = node2

    def getGraph(self):
        return self.node1.graph

    def has_key(self,key):
        '''
        test is the edge instance has a property named 'key'.
        
        @param key: the name of a property
        @type key: str
        
        @return: True if the edge has a property named <key>
        @rtype: bool
        '''
        if (self.node1.index,self.node2.index) in self.graph._edge_attrs:
            return key in self.graph._edge_attrs[(self.node1.index,self.node2.index)]
        else:
            return False


    def getDirected(self):
        return self.node1.graph._directed

    def __getitem__(self,key):
        return self.graph._edge_attrs.get((self.node1.index,self.node2.index),{})[key]
    
    def __setitem__(self,key,value):
        e = (self.node1.index,self.node2.index)
        if e in self.graph._edge_attrs:
            data = self.graph._edge_attrs[e]
            data[key]=value
        else:
            self.graph._edge_attrs[e]={key:value}

    def __str__(self):
        e = (self.node1.index,self.node2.index)
        if e in self.graph._edge_attrs:
            keys = "[%s]" % " ".join(['%s="%s"' % (x[0],str(x[1]).replace('"','\\"'))
                                      for x in self.graph._edge_attrs[e].iteritems()]
                                    )
        else:
            keys = ""
                           
        if self.directed:
            link='->'
        else:
            link='--'
            
        return "%d %s %d %s" % (self.node1.index,link,self.node2.index,keys) 
 
    def __contains__(self,key):
        return self.has_key(key)
       

    graph = property(getGraph, None, None, "Graph owning this edge")

    directed = property(getDirected, None, None, "Directed's Docstring")
    
        
class DiGraph(Graph):
    def __init__(self,label='G',indexer=None,nodes=None,edges=None):
        '''
        Directed Graph constructor.

        @param label: Graph name, set to 'G' by default
        @type label: str
        @param indexer: node label indexer
        @type indexer: Indexer instance
        @param nodes: set of nodes to add to the graph
        @type nodes: iterable value
        @param edges: set of edges to add to the graph
        @type edges: iterable value
        '''
        
        Graph.__init__(self, label, True, indexer, nodes, edges)
        
class UndirectedGraph(Graph):
    def __init__(self,label='G',indexer=None,nodes=None,edges=None):
        '''
        Directed Graph constructor.

        @param label: Graph name, set to 'G' by default
        @type label: str
        @param indexer: node label indexer
        @type indexer: Indexer instance
        @param nodes: set of nodes to add to the graph
        @type nodes: iterable value
        @param edges: set of edges to add to the graph
        @type edges: iterable value
        '''
        
        Graph.__init__(self, label, False, indexer, nodes, edges)
        
   
        
def selectEdgeAttributeFactory(attribut,value):
    def selectEdge(e):
        return attribut in e and e[attribut]==value
    return selectEdge   
