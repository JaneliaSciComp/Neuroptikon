"""
Read and write NetworkX graphs.

Note that NetworkX graphs can contain any hashable Python object as
node (not just integers and strings).  So writing a NetworkX graph
as a text file may not always be what you want: see write_gpickle
and gread_gpickle for that case.

This module provides the following :

Adjacency list with single line per node:
Useful for connected or unconnected graphs without edge data.

    write_adjlist(G, path)
    G=read_adjlist(path)

Adjacency list with multiple lines per node:
Useful for connected or unconnected graphs with or without edge data.

    write_multiline_adjlist(G, path)
    read_multiline_adjlist(path)

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nDan Schult (dschult@colgate.edu)"""
__date__ = """"""
__credits__ = """"""
__revision__ = ""
#    Copyright (C) 2004-2007 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

import cPickle 
import codecs
import locale
import string
import sys
import time

from networkx.utils import is_string_like,_get_fh
import networkx

def write_multiline_adjlist(G, path, delimiter=' ', comments='#'):
    """
    Write the graph G in multiline adjacency list format to the file
    or file handle path.

    See read_multiline_adjlist for file format details.

    >>> write_multiline_adjlist(G,"file.adjlist")

    path can be a filehandle or a string with the name of the file.

    >>> fh=open("file.adjlist")
    >>> write_multiline_adjlist(G,fh)

    Filenames ending in .gz or .bz2 will be compressed.

    >>> write_multiline_adjlist(G,"file.adjlist.gz")

    The file will use the default text encoding on your system.
    It is possible to write files in other encodings by opening
    the file with the codecs module.  See doc/examples/unicode.py
    for hints.

    >>> import codecs
    >>> fh=codecs.open("file.adjlist",encoding='utf=8') # use utf-8 encoding
    >>> write_multiline_adjlist(G,fh)

    """
    fh=_get_fh(path,mode='w')        
    pargs=comments+" "+string.join(sys.argv,' ')
    fh.write("%s\n" % (pargs))
    fh.write(comments+" GMT %s\n" % (time.asctime(time.gmtime())))
    fh.write(comments+" %s\n" % (G.name))

    # directed
    directed=G.is_directed()

    seen={}  # helper dict used to avoid duplicate edges
    for s in G.nodes():
        edges=[ edge for edge in G.edges_iter(s) if edge[1] not in seen ]
        deg=len(edges)
        if is_string_like(s):
            fh.write(s+delimiter)
        else:
            fh.write(str(s)+delimiter)                         
        fh.write("%i\n"%(deg))
        for edge in edges:
            t=edge[1]
            if len(edge)==2: # Graph or DiGraph
                d=None
            else:            # XGraph or XDiGraph
                d=edge[2]   # Note: could still be None
            if d is None:    
                if is_string_like(t):
                    fh.write(t+'\n')
                else:
                    fh.write(str(t)+'\n')                         
            else:   
                if is_string_like(t):
                    fh.write(t+delimiter)
                else:
                    fh.write(str(t)+delimiter)                         
                if is_string_like(d):
                    fh.write(d+"\n")
                else:
                    fh.write(str(d)+"\n")                         
        if not directed: 
            seen[s]=1
            
def read_multiline_adjlist(path, comments="#", delimiter=' ',
                           create_using=None,
                           nodetype=None, edgetype=None):
    """Read graph in multi-line adjacency list format from path.

    >>> G=read_multiline_adjlist("file.adjlist")

    path can be a filehandle or a string with the name of the file.

    >>> fh=open("file.adjlist")
    >>> G=read_multiline_adjlist(fh)

    Filenames ending in .gz or .bz2 will be compressed.

    >>> G=read_multiline_adjlist("file.adjlist.gz")

    nodetype is an optional function to convert node strings to nodetype

    For example

    >>> G=read_multiline_adjlist("file.adjlist", nodetype=int)

    will attempt to convert all nodes to integer type

    Since nodes must be hashable, the function nodetype must return hashable
    types (e.g. int, float, str, frozenset - or tuples of those, etc.) 

    edgetype is a function to convert edge data strings to edgetype

    >>> G=read_multiline_adjlist("file.adjlist", edgetype=int)

    create_using is an optional networkx graph type, the default is
    Graph(), a simple undirected graph 

    >>> G=read_multiline_adjlist("file.adjlist", create_using=DiGraph())

    The comments character (default='#') at the beginning of a
    line indicates a comment line.

    The entries are separated by delimiter (default=' ').
    If whitespace is significant in node or edge labels you should use
    some other delimiter such as a tab or other symbol.  
    

    Example multiline adjlist file format:: 

     # source target for Graph or DiGraph
     a 2
     b
     c
     d 1
     e

    or

     # source target for XGraph or XDiGraph with edge data
     a 2
     b edge-ab-data
     c edge-ac-data
     d 1
     e edge-de-data

    Reading the file will use the default text encoding on your system.
    It is possible to read files with other encodings by opening
    the file with the codecs module.  See doc/examples/unicode.py
    for hints.

    >>> import codecs
    >>> fh=codecs.open("file.adjlist", encoding='utf=8') # use utf-8 encoding
    >>> G=read_multiline_adjlist(fh)
    """
    if create_using is None:
        G=networkx.Graph()
    else:
        try:
            G=create_using
            G.clear()
        except:
            raise TypeError("Input graph is not a networkx graph type")

    # is this a XGraph or XDiGraph?
    if hasattr(G,'allow_multiedges')==True:
        xgraph=True
    else:
        xgraph=False

    inp=_get_fh(path)        

    for line in inp:
#        if line.startswith("#") or line.startswith("\n"):
#            continue
#        line=line.strip() #remove trailing \n 
        line = line[:line.find(comments)].strip()
        if not len(line): continue
        try:
            (u,deg)=line.split(delimiter)
            deg=int(deg)
        except:
            raise TypeError("Failed to read node and degree on line (%s)"%line)
        try:
            if nodetype is not None:
                u=nodetype(u)
        except:
            raise TypeError("Failed to convert node (%s) to type %s"\
                  %(u,nodetype))
        G.add_node(u)
        for i in range(deg):
            line=inp.next().strip()
            vlist=line.split(delimiter)
            if len(vlist)==1:
                v=vlist[0]
                d=None
            elif len(vlist)==2:
                (v,d)=vlist
            else:
                raise TypeError("Failed to read line: %s"%vlist)
            try:
                if nodetype is not None:
                    v=nodetype(v)
            except:
                raise TypeError("Failed to convert node (%s) to type %s"\
                                %(v,nodetype))
            if xgraph:
                if d is not None:
                    try:
                        if edgetype is not None:
                            d=edgetype(d)
                    except:
                        raise TypeError\
                              ("Failed to convert edge data (%s) to type %s"\
                                %(d, edgetype))
                G.add_edge(u,v,d)
            else:
                G.add_edge(u,v)
                
    return G


def write_adjlist(G, path, comments="#", delimiter=' '):
    """Write graph G in single-line adjacency-list format to path.

    See read_adjlist for file format details.

    >>> write_adjlist(G, "file.adjlist")

    path can be a filehandle or a string with the name of the file.

    >>> fh=open("file.adjlist")
    >>> write_adjlist(G, fh)

    Filenames ending in .gz or .bz2 will be compressed.

    >>> write_adjlist(G, "file.adjlist.gz")

    The file will use the default text encoding on your system.
    It is possible to write files in other encodings by opening
    the file with the codecs module.  See doc/examples/unicode.py
    for hints.

    >>> import codecs
    >>> fh=codecs.open("file.adjlist",encoding='utf=8') # use utf-8 encoding
    >>> write_adjlist(G,fh)

    Does not handle data in XGraph or XDiGraph, use 'write_edgelist'
    or 'write_multiline_adjlist'
    """
    fh=_get_fh(path,mode='w')        
    pargs=comments+" "+string.join(sys.argv,' ')
    fh.write("%s\n" % (pargs))
    fh.write(comments+" GMT %s\n" % (time.asctime(time.gmtime())))
    fh.write(comments+" %s\n" % (G.name))
    e={}  # helper dict used to avoid duplicate edges
    try:
        multiedges=G.multiedges
    except:
        multiedges=False

    # directed
    directed=G.is_directed()

    for s in G.nodes():
        if is_string_like(s):
            fh.write(s+delimiter)
        else:
            fh.write(str(s)+delimiter)
        for t in G.neighbors(s):
            if not directed:
                if e.has_key((t,s)):
                    continue
                e.setdefault((s,t),1)
            if multiedges:
                for d in G.get_edge(s,t):
                    if is_string_like(t):
                        fh.write(t+delimiter)
                    else:
                        fh.write(str(t)+delimiter)
            else:
                if is_string_like(t):
                    fh.write(t+delimiter)
                else:
                    fh.write(str(t)+delimiter)
        fh.write("\n")            


def read_adjlist(path, comments="#", delimiter=' ',
                 create_using=None, nodetype=None):
    """Read graph in single line adjacency list format from path.

    >>> G=read_adjlist("file.adjlist")

    path can be a filehandle or a string with the name of the file.

    >>> fh=open("file.adjlist")
    >>> G=read_adjlist(fh)

    Filenames ending in .gz or .bz2 will be compressed.

    >>> G=read_adjlist("file.adjlist.gz")

    nodetype is an optional function to convert node strings to nodetype

    For example

    >>> G=read_adjlist("file.adjlist", nodetype=int)

    will attempt to convert all nodes to integer type

    Since nodes must be hashable, the function nodetype must return hashable
    types (e.g. int, float, str, frozenset - or tuples of those, etc.) 

    create_using is an optional networkx graph type, the default is
    Graph(), a simple undirected graph 

    >>> G=read_adjlist("file.adjlist", create_using=DiGraph())

    Does not handle edge data: use 'read_edgelist' or 'read_multiline_adjlist'

    The comments character (default='#') at the beginning of a
    line indicates a comment line.

    The entries are separated by delimiter (default=' ').
    If whitespace is significant in node or edge labels you should use
    some other delimiter such as a tab or other symbol.  

     # source target
     a b c
     d e

    """
    if create_using is None:
        G=networkx.Graph()
    else:
        try:
            G=create_using
            G.clear()
        except:
            raise TypeError("Input graph is not a networkx graph type")

    fh=_get_fh(path)        

    for line in fh.readlines():
        line = line[:line.find(comments)].strip()
        if not len(line): continue
#        if line.startswith("#") or line.startswith("\n"):
#            continue
#        line=line.strip() #remove trailing \n 
        vlist=line.split(delimiter)
        u=vlist.pop(0)
        # convert types
        if nodetype is not None:
            try:
                u=nodetype(u)
            except:
                raise TypeError("Failed to convert node (%s) to type %s"\
                                %(u,nodetype))
        G.add_node(u)
        try:
            vlist=map(nodetype,vlist)
        except:
            raise TypeError("Failed to convert nodes (%s) to type %s"\
                            %(','.join(vlist),nodetype))
        for v in vlist:
            G.add_edge(u,v)
    return G



def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('tests/readwrite/adjlist.txt',package='networkx')
    return suite


if __name__ == "__main__":
    import os 
    import sys
    import unittest
    if sys.version_info[:2] < (2, 4):
        print "Python version 2.4 or later required for tests (%d.%d detected)." %  sys.version_info[:2]
        sys.exit(-1)
    # directory of networkx package (relative to this)
    nxbase=sys.path[0]+os.sep+os.pardir
    sys.path.insert(0,nxbase) # prepend to search path
    unittest.TextTestRunner().run(_test_suite())
    
