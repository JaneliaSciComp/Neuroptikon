"""
Base class for MultiDiGraph.

"""
__author__ = """\n""".join(['Aric Hagberg (hagberg@lanl.gov)',
                            'Pieter Swart (swart@lanl.gov)',
                            'Dan Schult(dschult@colgate.edu)'])

#    Copyright (C) 2004-2009 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
#

from networkx.classes.graph import Graph  # for doctests
from networkx.classes.digraph import DiGraph
from networkx.classes.multigraph import MultiGraph
from networkx.exception import NetworkXException, NetworkXError
import networkx.convert as convert
from copy import deepcopy


class MultiDiGraph(MultiGraph,DiGraph):
    """
    A directed graph class that can store multiedges.
    
    Multiedges are multiple edges between two nodes.  Each edge
    can hold optional data or attributes.

    A MultiDiGraph holds directed edges.  Self loops are allowed.

    Nodes can be arbitrary (hashable) Python objects with optional
    key/value attributes.

    Edges are represented as links between nodes with optional
    key/value attributes.

    Parameters
    ----------
    data : input graph
        Data to initialize graph.  If data=None (default) an empty
        graph is created.  The data can be an edge list, or any
        NetworkX graph object.  If the corresponding optional Python
        packages are installed the data can also be a NumPy matrix
        or 2d ndarray, a SciPy sparse matrix, or a PyGraphviz graph.
    name : string, optional (default='')
        An optional name for the graph.
    attr : keyword arguments, optional (default= no attributes)
        Attributes to add to graph as key=value pairs.

    See Also
    --------
    Graph
    DiGraph
    MultiGraph
    
    Examples
    --------
    Create an empty graph structure (a "null graph") with no nodes and 
    no edges.

    >>> G = nx.MultiDiGraph()

    G can be grown in several ways.

    **Nodes:**
  
    Add one node at a time:

    >>> G.add_node(1)

    Add the nodes from any container (a list, dict, set or 
    even the lines from a file or the nodes from another graph).

    >>> G.add_nodes_from([2,3])
    >>> G.add_nodes_from(range(100,110))
    >>> H=nx.path_graph(10)
    >>> G.add_nodes_from(H)

    In addition to strings and integers any hashable Python object
    (except None) can represent a node, e.g. a customized node object,
    or even another Graph.

    >>> G.add_node(H)

    **Edges:**
    
    G can also be grown by adding edges.

    Add one edge,

    >>> G.add_edge(1, 2)

    a list of edges, 

    >>> G.add_edges_from([(1,2),(1,3)])

    or a collection of edges,
    
    >>> G.add_edges_from(H.edges())

    If some edges connect nodes not yet in the graph, the nodes 
    are added automatically.  If an edge already exists, an additional
    edge is created and stored using a key to identify the edge.
    By default the key is the lowest unused integer.

    >>> G.add_edges_from([(4,5,dict(route=282)), (4,5,dict(route=37))])
    >>> G[4]
    {5: {0: {}, 1: {'route': 282}, 2: {'route': 37}}}

    **Attributes:**
    
    Each graph, node, and edge can hold key/value attribute pairs
    in an associated attribute dictionary (the keys must be hashable).
    By default these are empty, but can be added or changed using
    add_edge, add_node or direct manipulation of the attribute 
    dictionaries named graph, node and edge respectively.

    >>> G = nx.MultiDiGraph(day="Friday")
    >>> G.graph
    {'day': 'Friday'}

    Add node attributes using add_node(), add_nodes_from() or G.node

    >>> G.add_node(1, time='5pm')
    >>> G.add_nodes_from([3], time='2pm')
    >>> G.node[1]
    {'time': '5pm'}
    >>> G.node[1]['room'] = 714
    >>> G.nodes(data=True)
    [(1, {'room': 714, 'time': '5pm'}), (3, {'time': '2pm'})]

    Warning: adding a node to G.node does not add it to the graph.

    Add edge attributes using add_edge(), add_edges_from(), subscript
    notation, or G.edge.

    >>> G.add_edge(1, 2, weight=4.7 )
    >>> G.add_edges_from([(3,4),(4,5)], color='red')
    >>> G.add_edges_from([(1,2,{'color':'blue'}), (2,3,{'weight':8})])
    >>> G[1][2][0]['weight'] = 4.7
    >>> G.edge[1][2][0]['weight'] = 4

    **Shortcuts:**

    Many common graph features allow python syntax to speed reporting.

    >>> 1 in G     # check if node in graph
    True
    >>> print [n for n in G if n<3]   # iterate through nodes
    [1, 2]
    >>> print len(G)  # number of nodes in graph
    5
    >>> print G[1] # adjacency dict keyed by neighbor to edge attributes
    ...            # Note: you should not change this dict manually!
    {2: {0: {'weight': 4}, 1: {'color': 'blue'}}}

    The fastest way to traverse all edges of a graph is via 
    adjacency_iter(), but the edges() method is often more convenient.

    >>> for n,nbrsdict in G.adjacency_iter(): 
    ...     for nbr,keydict in nbrsdict.iteritems():
    ...        for key,eattr in keydict.iteritems():
    ...            if 'weight' in eattr:
    ...                print (n,nbr,eattr['weight'])
    (1, 2, 4)
    (2, 3, 8)
    >>> print [ (u,v,edata['weight']) for u,v,edata in G.edges(data=True) if 'weight' in edata ]
    [(1, 2, 4), (2, 3, 8)]

    **Reporting:**
    
    Simple graph information is obtained using methods.
    Iterator versions of many reporting methods exist for efficiency.
    Methods exist for reporting nodes(), edges(), neighbors() and degree()
    as well as the number of nodes and edges.
    
    For details on these and other miscellaneous methods, see below.
    """
    def add_edge(self, u, v, key=None, attr_dict=None, **attr):
        """Add an edge between u and v.

        The nodes u and v will be automatically added if they are 
        not already in the graph.  

        Edge attributes can be specified with keywords or by providing
        a dictionary with key/value pairs.  See examples below.

        Parameters
        ----------
        u,v : nodes
            Nodes can be, for example, strings or numbers. 
            Nodes must be hashable (and not None) Python objects.
        key : hashable identifier, optional (default=lowest unused integer)
            Used to distinguish multiedges between a pair of nodes.  
        attr_dict : dictionary, optional (default= no attributes)
            Dictionary of edge attributes.  Key/value pairs will
            update existing data associated with the edge.
        attr : keyword arguments, optional
            Edge data (or labels or objects) can be assigned using
            keyword arguments.   

        See Also
        --------
        add_edges_from : add a collection of edges

        Notes 
        -----
        To replace/update edge data, use the optional key argument
        to identify a unique edge.  Otherwise a new edge will be created.

        NetworkX algorithms designed for weighted graphs cannot use
        multigraphs directly because it is not clear how to handle
        multiedge weights.  Convert to Graph using edge attribute
        'weight' to enable weighted graph algorithms.

        Examples
        --------
        The following all add the edge e=(1,2) to graph G:
        
        >>> G = nx.MultiDiGraph()
        >>> e = (1,2)
        >>> G.add_edge(1, 2)           # explicit two-node form
        >>> G.add_edge(*e)             # single edge as tuple of two nodes
        >>> G.add_edges_from( [(1,2)] ) # add edges from iterable container

        Associate data to edges using keywords:

        >>> G.add_edge(1, 2, weight=3)
        >>> G.add_edge(1, 2, key=0, weight=4)   # update data for key=0
        >>> G.add_edge(1, 3, weight=7, capacity=15, length=342.7)
        """
        # set up attribute dict
        if attr_dict is None:
            attr_dict=attr
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                raise NetworkXError(\
                    "The attr_dict argument must be a dictionary.")
        # add nodes
        if u not in self.succ:
            self.succ[u] = {}
            self.pred[u] = {}
            self.node[u] = {}
        if v not in self.succ:
            self.succ[v] = {}
            self.pred[v] = {}
            self.node[v] = {}
        if v in self.succ[u]:
            keydict=self.adj[u][v]
            if key is None:
                # find a unique integer key
                # other methods might be better here?
                key=0
                while key in keydict:
                    key+=1
            datadict=keydict.get(key,{})
            datadict.update(attr_dict)
            keydict[key]=datadict
        else:
            # selfloops work this way without special treatment
            if key is None:
                key=0
            datadict={}
            datadict.update(attr_dict)
            keydict={key:datadict}
            self.succ[u][v] = keydict
            self.pred[v][u] = keydict

    def remove_edge(self, u, v, key=None):
        """Remove an edge between u and v.  

        Parameters
        ----------
        u,v: nodes 
            Remove an edge between nodes u and v.
        key : hashable identifier, optional (default=None)
            Used to distinguish multiple edges between a pair of nodes.  
            If None remove a single (abritrary) edge between u and v.

        Raises
        ------
        NetworkXError
            If there is not an edge between u and v, or
            if there is no edge with the specified key.

        See Also
        --------
        remove_edges_from : remove a collection of edges

        Examples
        --------
        >>> G = nx.MultiDiGraph()  
        >>> G.add_path([0,1,2,3])
        >>> G.remove_edge(0,1)
        >>> e = (1,2)
        >>> G.remove_edge(*e) # unpacks e from an edge tuple

        For multiple edges

        >>> G = nx.MultiDiGraph()  
        >>> G.add_edges_from([(1,2),(1,2),(1,2)])
        >>> G.remove_edge(1,2) # remove a single (arbitrary) edge
        
        For edges with keys

        >>> G = nx.MultiDiGraph()   
        >>> G.add_edge(1,2,key='first')
        >>> G.add_edge(1,2,key='second')
        >>> G.remove_edge(1,2,key='second')

        """
        try:
            d=self.adj[u][v]
        except (KeyError):
            raise NetworkXError(
                "The edge %s-%s is not in the graph."%(u,v))
        # remove the edge with specified data
        if key is None:
            d.popitem()
        else:
            try:
                del d[key]
            except (KeyError):
                raise NetworkXError(
                "The edge %s-%s with key %s is not in the graph."%(u,v,key))
        if len(d)==0: 
            # remove the key entries if last edge
            del self.succ[u][v]
            del self.pred[v][u]


    def edges_iter(self, nbunch=None, data=False, keys=False):
        """Return an iterator over the edges.
        
        Edges are returned as tuples with optional data and keys
        in the order (node, neighbor, key, data).

        Parameters
        ----------
        nbunch : iterable container, optional (default= all nodes)
            A container of nodes.  The container will be iterated
            through once.
        data : bool, optional (default=False)
            If True, return edge attribute dict with each edge.
        keys : bool, optional (default=False)
            If True, return edge keys with each edge.

        Returns
        -------
        edge_iter : iterator
            An iterator of (u,v), (u,v,d) or (u,v,key,d) tuples of edges.

        See Also
        --------
        edges : return a list of edges

        Notes
        -----
        Nodes in nbunch that are not in the graph will be (quietly) ignored.

        Examples
        --------
        >>> G = nx.MultiDiGraph()  
        >>> G.add_path([0,1,2,3])
        >>> [e for e in G.edges_iter()]
        [(0, 1), (1, 2), (2, 3)]
        >>> list(G.edges_iter(data=True)) # default data is {} (empty dict)
        [(0, 1, {}), (1, 2, {}), (2, 3, {})]
        >>> list(G.edges_iter([0,2]))
        [(0, 1), (2, 3)]
        >>> list(G.edges_iter(0))
        [(0, 1)]

        """
        if nbunch is None:
            nodes_nbrs = self.adj.iteritems()
        else:
            nodes_nbrs=((n,self.adj[n]) for n in self.nbunch_iter(nbunch))
        if data:
            for n,nbrs in nodes_nbrs:
                for nbr,keydict in nbrs.iteritems():
                    for key,data in keydict.iteritems():
                        if keys:
                            yield (n,nbr,key,data)
                        else:
                            yield (n,nbr,data)
        else:
            for n,nbrs in nodes_nbrs:
                for nbr,keydict in nbrs.iteritems():
                    for key,data in keydict.iteritems():
                        if keys:
                            yield (n,nbr,key)
                        else:
                            yield (n,nbr)

    # alias out_edges to edges
    out_edges_iter=edges_iter

    def in_edges_iter(self, nbunch=None, data=False, keys=False):
        """Return an iterator over the incoming edges.
        
        Parameters
        ----------
        nbunch : iterable container, optional (default= all nodes)
            A container of nodes.  The container will be iterated
            through once.
        data : bool, optional (default=False)
            If True, return edge attribute dict with each edge.
        keys : bool, optional (default=False)
            If True, return edge keys with each edge.

        Returns
        -------
        in_edge_iter : iterator
            An iterator of (u,v), (u,v,d) or (u,v,key,d) tuples of edges.

        See Also
        --------
        edges_iter : return an iterator of edges
        """
        if nbunch is None:
            nodes_nbrs=self.pred.iteritems()
        else:
            nodes_nbrs=((n,self.pred[n]) for n in self.nbunch_iter(nbunch))
        if data:
            for n,nbrs in nodes_nbrs:
                for nbr,keydict in nbrs.iteritems():
                    for key,data in keydict.iteritems():
                        if keys:
                            yield (nbr,n,key,data)
                        else:
                            yield (nbr,n,data)
        else:
            for n,nbrs in nodes_nbrs:
                for nbr,keydict in nbrs.iteritems():
                    for key,data in keydict.iteritems():
                        if keys:
                            yield (nbr,n,key)
                        else:
                            yield (nbr,n)


    def degree_iter(self, nbunch=None, weighted=False):
        """Return an iterator for (node, degree). 

        The node degree is the number of edges adjacent to the node. 

        Parameters
        ----------
        nbunch : iterable container, optional (default=all nodes)
            A container of nodes.  The container will be iterated
            through once.    
        weighted : bool, optional (default=False)
           If True return the sum of edge weights adjacent to the node.  

        Returns
        -------
        nd_iter : an iterator 
            The iterator returns two-tuples of (node, degree).
        
        See Also
        --------
        degree

        Examples
        --------
        >>> G = nx.MultiDiGraph() 
        >>> G.add_path([0,1,2,3])
        >>> list(G.degree_iter(0)) # node 0 with degree 1
        [(0, 1)]
        >>> list(G.degree_iter([0,1]))
        [(0, 1), (1, 2)]

        """
        from itertools import izip
        if nbunch is None:
            nodes_nbrs=izip(self.succ.iteritems(),self.pred.iteritems())
        else:
            nodes_nbrs=izip(
                ((n,self.succ[n]) for n in self.nbunch_iter(nbunch)),
                ((n,self.pred[n]) for n in self.nbunch_iter(nbunch)))

        if weighted:
        # edge weighted graph - degree is sum of nbr edge weights
            for (n,succ),(n2,pred) in nodes_nbrs:
                deg = sum([d.get('weight',1) 
                           for data in pred.itervalues()
                           for d in data.itervalues()])
                deg += sum([d.get('weight',1) 
                           for data in succ.itervalues()
                           for d in data.itervalues()])
#                if n in succ:
                    # double counted selfloop so subtract
#                    deg -= sum([d.get('weight',1) 
#                           for key,d in succ[n].iteritems()])
                yield (n, deg)
        else:
            for (n,succ),(n2,pred) in nodes_nbrs:
                indeg = sum([len(data) for data in pred.itervalues()])
                outdeg = sum([len(data) for data in succ.itervalues()])
                yield (n, indeg + outdeg)  
# double counted selfloop so subtract
#                      - (n in succ and len(succ[n])))


    def in_degree_iter(self, nbunch=None, weighted=False):
        """Return an iterator for (node, in-degree). 

        The node in-degree is the number of edges pointing in to the node.

        Parameters
        ----------
        nbunch : iterable container, optional (default=all nodes)
            A container of nodes.  The container will be iterated
            through once.    
        weighted : bool, optional (default=False)
           If True return the sum of edge weights adjacent to the node.  

        Returns
        -------
        nd_iter : an iterator 
            The iterator returns two-tuples of (node, in-degree).
        
        See Also
        --------
        degree, in_degree, out_degree, out_degree_iter

        Examples
        --------
        >>> G = nx.MultiDiGraph()  
        >>> G.add_path([0,1,2,3])
        >>> list(G.in_degree_iter(0)) # node 0 with degree 0
        [(0, 0)]
        >>> list(G.in_degree_iter([0,1]))
        [(0, 0), (1, 1)]

        """
        if nbunch is None:
            nodes_nbrs=self.pred.iteritems()
        else:
            nodes_nbrs=((n,self.pred[n]) for n in self.nbunch_iter(nbunch))

        if weighted:
            # edge weighted graph - degree is sum of nbr edge weights
            for n,pred in nodes_nbrs:
                deg = sum([d.get('weight',1) 
                           for data in pred.itervalues()
                           for d in data.itervalues()])
                yield (n, deg)
        else:
            for n,nbrs in nodes_nbrs:
                yield (n, sum([len(data) for data in nbrs.itervalues()]) )


    def out_degree_iter(self, nbunch=None, weighted=False):
        """Return an iterator for (node, out-degree). 

        The node out-degree is the number of edges pointing out of the node.

        Parameters
        ----------
        nbunch : iterable container, optional (default=all nodes)
            A container of nodes.  The container will be iterated
            through once.    
        weighted : bool, optional (default=False)
           If True return the sum of edge weights adjacent to the node.  

        Returns
        -------
        nd_iter : an iterator 
            The iterator returns two-tuples of (node, out-degree).
        
        See Also
        --------
        degree, in_degree, out_degree, in_degree_iter

        Examples
        --------
        >>> G = nx.MultiDiGraph()
        >>> G.add_path([0,1,2,3])
        >>> list(G.out_degree_iter(0)) # node 0 with degree 1
        [(0, 1)]
        >>> list(G.out_degree_iter([0,1]))
        [(0, 1), (1, 1)]

        """
        if nbunch is None:
            nodes_nbrs=self.succ.iteritems()
        else:
            nodes_nbrs=((n,self.succ[n]) for n in self.nbunch_iter(nbunch))

        if weighted:
            for n,succ in nodes_nbrs:
                deg = sum([d.get('weight',1) 
                           for data in succ.itervalues()
                           for d in data.itervalues()])
                yield (n, deg)
        else:
            for n,nbrs in nodes_nbrs:
                yield (n, sum([len(data) for data in nbrs.itervalues()]) )

    def is_multigraph(self):
        """Return True if graph is a multigraph, False otherwise."""
        return True

    def is_directed(self):
        """Return True if graph is directed, False otherwise."""
        return True

    def to_directed(self):
        """Return a directed copy of the graph.
 
        Returns
        -------
        G : MultiDiGraph
            A deepcopy of the graph.

        Notes
        -----
        If edges in both directions (u,v) and (v,u) exist in the
        graph, attributes for the new undirected edge will be a combination of
        the attributes of the directed edges.  The edge data is updated
        in the (arbitrary) order that the edges are encountered.  For
        more customized control of the edge attributes use add_edge().

        This is similar to MultiDiGraph(self) which returns a shallow copy.  
        self.to_undirected() returns a deepcopy of edge, node and
        graph attributes.

        Examples
        --------
        >>> G = nx.Graph()   # or MultiGraph, etc
        >>> G.add_path([0,1])
        >>> H = G.to_directed()
        >>> H.edges()
        [(0, 1), (1, 0)]

        If already directed, return a (deep) copy

        >>> G = nx.MultiDiGraph()   
        >>> G.add_path([0,1])
        >>> H = G.to_directed()
        >>> H.edges()
        [(0, 1)]
        """
        return deepcopy(self)

    def to_undirected(self):
        """Return an undirected representation of the digraph.
 
        Returns
        -------
        G : MultiGraph
            An undirected graph with the same name and nodes and 
            with edge (u,v,data) if either (u,v,data) or (v,u,data)
            is in the digraph.  If both edges exist in digraph and
            their edge data is different, only one edge is created
            with an arbitrary choice of which edge data to use.
            You must check and correct for this manually if desired.

        Notes
        -----
        This is similar to MultiGraph(self) which returns a shallow copy.  
        self.to_undirected() returns a deepcopy of edge, node and
        graph attributes.
        """
        H=MultiGraph()
        H.name=self.name
        H.add_nodes_from(self)
        H.add_edges_from( ((u,v,key,deepcopy(data))
                           for u,nbrs in self.adjacency_iter()
                           for v,keydict in nbrs.iteritems()
                           for key,data in keydict.items()))
        H.graph=deepcopy(self.graph)
        H.node=deepcopy(self.node)
        return H

