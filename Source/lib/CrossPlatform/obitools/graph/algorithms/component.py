import sys

def componentIterator(graph,nodePredicat=None,edgePredicat=None):
    seen = set()
    for n in graph:
        if n.index not in seen:
            cc=n.componentIndexSet(nodePredicat, edgePredicat)
            yield cc
            seen |= cc
            
def componentCount(graph):
    n=0
    for c in componentIterator(graph):
        n+=1
    return n

 
        