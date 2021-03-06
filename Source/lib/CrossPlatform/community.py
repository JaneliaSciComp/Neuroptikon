#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This module implements community detection.


It uses the louvain method described in
Fast unfolding of communities in large networks,
Vincent D Blondel, Jean-Loup Guillaume, Renaud Lambiotte, Renaud Lefebvre,
Journal of Statistical Mechanics: Theory and Experiment 2008(10), P10008 (12pp)

It depends on Networkx to handle graph operations :
http://networkx.lanl.gov/

The program itself can be found at
http://perso.crans.org/aynaud/communities/community.py



Example :
=========

As a classical software :
-------------------------
#You should consider using the cpp version at http://findcommunities.googlepages.com/ !

./community.py file.bin > tree



where file.bin is a binary graph as generated by the convert utility of the cpp
version.

You can after that use the generated file with the hierarchy utility of the cpp
version.
Note that the program does not make much verifications about the arguments,
and is expecting a friendly use.

As python module :
------------------

.. python::

    import community
    import networkx as nx
    import matplotlib.pyplot as plt

    #better with karate_graph() as defined in networkx example.
    #erdos renyi don't have true community structure
    G = nx.erdos_renyi_graph(30, 0.05)

    #first compute the best partition
    dendogram = community.generate_dendogram(G)
    partition = community.best_partition(dendogram)

    #drawing
    size = float(len(set(partition.values())))
    pos = nx.spring_layout(G)
    count = 0.
    for com in set(partition.values()) :
        count = count + 1.
        list_nodes = [nodes for nodes in partition.keys()
                                    if partition[nodes] == com]
        nx.draw_networkx_nodes(G, pos, list_nodes, node_size = 20,
                                    node_color = str(count / size))


    nx.draw_networkx_edges(G,pos, alpha=0.5)
    plt.show()



Changelog :
===========
04/10/2009 : increase of the speed of the detection by caching node degrees



License :
=========

Copyright (C) 2009 by
Thomas Aynaud <thomas.aynaud@lip6.fr>
Distributed under the terms of the GNU Lesser General Public License
http://www.gnu.org/copyleft/lesser.html

"""


__author__ = """Thomas Aynaud (thomas.aynaud@lip6.fr)"""

import networkx as nx
import sys
try:
    import psyco
    psyco.full()
except ImportError:
    pass


PASS_MAX = -1
MIN = 0.0000001


def partition_at_level(dendogram, level) :
    """ Return the partition of the nodes at the given level


    level 0 is the first partition, and the best is len(dendogram) - 1

    :Parameters:
        dendogram : list of dictionnaries
            a list of partitions, ie dictionnaries where keys of the i+1 are
            the values of the i.
        level : int
            an integer which belongs to [0..len(dendogram)-1]


    :Returns:
        a dictionnary where keys are the nodes and the values are the set it
        belongs to
    """
    partition = dendogram[0].copy()
    for index in range(1, level + 1) :
        for node, community in partition.iteritems() :
            partition[node] = dendogram[index][community]
    return partition

def best_partition(dendogram) :
    """return the partition of the dendogram that maximizes modularity.

    It's always the last one...

    :Parameters:
        dendogram
            a list of partitions, ie dictionnaries where keys of the i+1 are
            the values of the i.

    :Returns:
        a dictionnary where keys are the nodes and the values are the part it
        belongs to
    """
    return partition_at_level(dendogram, len(dendogram) - 1 )


def generate_dendogram(graph) :
    """
    Find communities in the graph and return the associated dendogram

    :Parameters:
        graph
            the networkx graph which will be decomposed

    :Returns:
        a list of partitions, ie dictionnaries where keys of the i+1 are
        the values of the i. and where keys of the first are the nodes of graph
    """
    current_graph = graph.copy()
    status = Status()
    status.init(current_graph)
    mod = __modularity(status)
    status_list = list()
    one_level(current_graph, status)
    new_mod = __modularity(status)
    #print >> sys.stderr, 'modularity found : ' + str(new_mod)
    partition = renumber(status.node2com)
    status_list.append(partition)
    mod = new_mod
    current_graph = induced_graph(partition, current_graph)
    status.init(current_graph)


    while True :
        one_level(current_graph, status)
        new_mod = __modularity(status)
        #print >> sys.stderr, 'modularity found : ' + str(new_mod)
        if new_mod - mod < MIN :
            break
        partition = renumber(status.node2com)
        status_list.append(partition)
        mod = new_mod
        current_graph = induced_graph(partition, current_graph)
        status.init(current_graph)
    return status_list[:]


def modularity(partition, graph) :
    """
    Compute the modularity of a partition of a graph

    :Parameters:
        partition
            the partition of the nodes, i.e a dictionary where keys are their
            nodes and values the communities
        graph
            the networkx graph which is decomposed

    :Returns:
        The modularity
    """
    inc = dict([])
    deg = dict([])
    L = graph.size(weighted = True)
    for node in graph :
        com = partition[node]
        deg[com] = deg.get(com, 0.) + graph.degree(node, weighted = True)
        for neighbor, attrs in graph[node].iteritems() :
            if partition[neighbor] == com :
                if neighbor == node :
                    inc[com] = inc.get(com, 0.) + float(attrs['weight'])
                else :
                    inc[com] = inc.get(com, 0.) + float(attrs['weight']) / 2.

    res = 0.
    for com in set(partition.values()) :
        res = res + (inc.get(com, 0.) / L) - (deg.get(com, 0.) / (2.*L))**2
    return res

def induced_graph(partition, graph) :
    """
    Produce the graph where nodes are the communities

    there is a link of weight w between communities if the sum of the weights
    of the links between their elements is w

    :Parameters:
        partition
            a dictionnary where keys are graph nodes and
            values the part the node belongs to
        graph
            the initial graph

    :Returns:
        a networkx graph where nodes are the parts

    """
    new_graph = nx.Graph()
    new_graph.add_nodes_from(partition.values())
    for node1, node2, attrs in graph.edges_iter(data = True) :
        com1 = partition[node1]
        com2 = partition[node2]
        weight_prec = new_graph.get_edge_data(com1, com2, {})
        new_graph.add_edge(com1, com2, weight = weight_prec.get('weight', 0) + attrs.get('weight'))
    return new_graph


def one_level(graph, status) :
    """
    Compute one level of communities

    :Parameters:
        graph
            the graph we are working on
        status
            a named tuple with node2com, total_weight, internals, degrees set

    :Returns:
        nothing, the status is modified during the function
    """
    modif = True
    nb_pass_done = 0
    cur_mod = __modularity(status)
    new_mod = cur_mod

    while modif  and nb_pass_done != PASS_MAX :
        cur_mod = new_mod
        modif = False
        nb_pass_done = nb_pass_done + 1
        for node in graph.nodes() :
            com = status.node2com[node]
            degc = status.gdegrees.get(node, 0.)
            totw = status.total_weight*2.
            neigh_communities = __neighcom(node, graph, status)
            __remove(graph, node, com, neigh_communities.get(com, 0.), status)
            best_com = com
            best_increase = 0.
            for com in neigh_communities.keys() :
                dnc = neigh_communities[com]
                totc = status.degrees.get(com, 0.)
                inc = status.internals.get(com, 0.)
                incr = (((inc + 2. * dnc) / totw - ((totc + degc) / totw)**2) -
                            (inc / totw - (totc / totw)**2 - (degc / totw)**2) )
                if incr > best_increase :
                    best_increase = incr
                    best_com = com
            deg = neigh_communities.get(best_com, 0.)
            __insert(graph, node, best_com, deg, status)
            if best_com != com :
                modif = True
        new_mod = __modularity(status)
        if new_mod - cur_mod < MIN :
            break

def load_binary(data) :
    """
    Load binary graph as used by the cpp implementation of this algorithm
    """
    import types
    if type(data) == types.StringType :
        data = open(data, "rb")
    import array
    reader = array.array("I")
    reader.fromfile(data, 1)
    num_nodes = reader.pop()
    reader = array.array("I")
    reader.fromfile(data, num_nodes)
    cum_deg = reader.tolist()
    num_links = reader.pop()
    reader = array.array("I")
    reader.fromfile(data, num_links)
    links = reader.tolist()
    graph = nx.Graph()
    graph.add_nodes_from(range(num_nodes))
    prec_deg = 0
    for index in range(num_nodes) :
        last_deg = cum_deg[index]
        neighbors = links[prec_deg:last_deg]
        graph.add_edges_from([(index, int(neigh)) for neigh in neighbors])
        prec_deg = last_deg
    return graph


class Status :
    """
    To handle several data in one struct.

    Could be replaced by named tuple, but don't want to depend on python 2.6
    """
    node2com = {}
    total_weight = 0
    internals = {}
    degrees = {}
    gdegrees = {}
    def __init__(self) :
        self.node2com = dict([])
        self.total_weight = 0
        self.degrees = dict([])
        self.gdegrees = dict([])
        self.internals = dict([])
    def __str__(self) :
        return ("node2com : " + str(self.node2com) + " degrees : "
            + str(self.degrees) + " internals : " + str(self.internals)
            + " total_weight : " + str(self.total_weight))

    def copy(self) :
        """Perform a deep copy of status"""
        new_status = Status()
        new_status.node2com = self.node2com.copy()
        new_status.internals = self.internals.copy()
        new_status.degrees = self.degrees.copy()
        new_status.gdegrees = self.gdegrees.copy()
        new_status.total_weight = self.total_weight

    def init(self, graph) :
        """Initialize the status of a graph with every node in one community"""
        count = 0
        self.node2com = dict([])
        self.total_weight = 0
        self.degrees = dict([])
        self.gdegrees = dict([])
        self.internals = dict([])
        self.total_weight = graph.size(weighted = True)
        for node in graph.nodes() :
            self.node2com[node] = count
            self.internals[count] = float(graph.get_edge_data(node, node, {}).get('weight', 1.0))
            deg = float(graph.degree(node, weighted = True))
            self.degrees[count] = deg
            self.gdegrees[node] = deg
            count = count + 1


def __neighcom(node, graph, status) :
    """
    Compute the communities in the neighborood of node in the graph given
    with the decomposition node2com
    """
    weights = {}
    for neighbor, attrs in graph[node].iteritems() :
        if neighbor != node :
            neighborcom = status.node2com[neighbor]
            weights[neighborcom] = weights.get(neighborcom, 0) + attrs['weight']
    return weights

def __remove(graph, node, com, weight, status) :
    """ Remove node from community com and modify status"""
    status.degrees[com] = ( status.degrees.get(com, 0.)
                                    - status.gdegrees.get(node, 0.) )
    status.internals[com] = float( status.internals.get(com, 0.) -
                weight - graph.get_edge_data(node, node, {}).get('weight', 0.) )
    status.node2com[node] = -1

def __insert(graph, node, com, weight, status) :
    """ Insert node into community and modify status"""
    status.node2com[node] = com
    status.degrees[com] = ( status.degrees.get(com, 0.) +
                                status.gdegrees.get(node, 0.) )
    status.internals[com] = float( status.internals.get(com, 0.) +
                        weight + graph.get_edge_data(node, node, {}).get('weight', 0.) )

def __modularity(status) :
    """
    Compute the modularity of the partition of the graph

    :Parameters:
        status
            the status of the partition see class Status

    :Returns:
        modularity a float
    """
    links = float(status.total_weight)
    result = 0.
    for community in set(status.node2com.values()) :
        in_degree = status.internals.get(community, 0.)
        degree = status.degrees.get(community, 0.)
        if links > 0 :
            result = result + in_degree / links - ((degree / (2.*links))**2)
    return result

def renumber(dictionnary) :
    """Renumber the values of the dictionnary from 0 to n"""
    count = 0
    ret = dictionnary.copy()
    new_values = dict([])
    for key in dictionnary.keys() :
        value = dictionnary[key]
        new_value = new_values.get(value, -1)
        if new_value == -1 :
            new_values[value] = count
            new_value = count
            count = count + 1
        ret[key] = new_value
    return ret

def __main() :
    """Main function"""
    try :
        filename = sys.argv[1]
        graphfile = load_binary(filename)
        dendo = generate_dendogram(graphfile)
        for lvl in dendo :
            for elem, part in lvl.iteritems() :
                print str(elem) + " " + str(part)
        print str(modularity(best_partition(dendo), graphfile))
    except (IndexError, IOError):
        print "Usage : ./community filename"
        print "find the communities in graph filename and display the dendogram"
        print "Parameters:"
        print "filename is a binary file as generated by the "
        print "convert utility distributed with the C implementation"


if __name__ == "__main__" :
    __main()


