from logging import debug
import time
import sys



_maxsize=0
_solution=0
_notbound=0
_sizebound=0

def cliqueIterator(graph,minsize=1,node=None):
    global _maxsize,_solution,_notbound,_sizebound
    _maxsize=0
    _solution=0
    _notbound=0
    _sizebound=0
    starttime = time.time()  
    
    if node:
        node = graph.getNode(node)
        index = node.index
        clique= set([index])
        candidates= set(graph.neighbourIndexSet(index=index))
    else:
        clique=set()
        candidates = set(x.index for x in graph)
        
    
#    candidates = set(x for x in candidates
#                     if len(graph.neighbourIndexSet(index=x) & candidates) >= (minsize - 1))
            
      
    for c in _cliqueIterator(graph,clique,candidates,set(),minsize,start=starttime):
        yield c




        
def _cliqueIterator(graph,clique,candidates,notlist,minsize=0,start=None):
    global _maxsize,_solution,_notbound,_sizebound

                            # Speed indicator
    lclique     = len(clique)
    lcandidates = len(candidates)
    notmin = lcandidates
    notfix = None
    
    for n in notlist:
        nnc = candidates - graph.neighbourIndexSet(index=n) 
        nc = len(nnc)
        if nc < notmin:
            notmin=nc
            notfix=n
            notfixneib = nnc
                
    if lclique > _maxsize or not _solution % 1000 :   
        if start is not None:
            top   = time.time()
            delta = top - start
            speed = _solution / delta
            start = top
        else:
            speed = 0
        print >>sys.stderr,"\rCandidates : %-5d Maximum clique size : %-5d Solutions explored : %10d   speed = %5.2f solutions/sec  sizebound=%10d notbound=%10d          " % (lcandidates,_maxsize,_solution,speed,_sizebound,_notbound),
        sys.stderr.flush()
        if lclique > _maxsize:
            _maxsize=lclique

 #   print >>sys.stderr,'koukou'        

    if not candidates and not notlist:
        yield set(clique)
    else:                        
        while notmin and candidates and (lclique + len(candidates)) >= minsize:
                    # count explored solution
            _solution+=1
            
            if notfix is None:
                nextcandidate = candidates.pop()
            else:
                nextcandidate = notfixneib.pop()
                candidates.remove(nextcandidate)
                
            clique.add(nextcandidate)     

            neighbours = graph.neighbourIndexSet(index=nextcandidate)   

            nextcandidates = candidates & neighbours
            nextnot        = notlist    & neighbours
            
            nnc = candidates - neighbours
            lnnc=len(nnc)
            
            for c in _cliqueIterator(graph, 
                                     set(clique), 
                                     nextcandidates,
                                     nextnot,
                                     minsize,
                                     start):
                yield c
    
                        
            clique.remove(nextcandidate)
            
            notmin-=1
            
            if lnnc < notmin:
                notmin = lnnc
                notfix = nextcandidate
                notfixneib = nnc
                            
            if notmin==0:
                _notbound+=1
                
            notlist.add(nextcandidate)
        else:
            if (lclique + len(candidates)) < minsize:
                _sizebound+=1

