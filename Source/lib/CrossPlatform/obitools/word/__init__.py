from itertools import imap


_dna='acgt'

def wordCount(liste):
    count = {}
    
    for e in liste:
        count[e]=count.get(e,0) + 1
    
    return count


def wordIterator(sequence,lword,step=1,endIncluded=False,circular=False):
    assert not (endIncluded and circular), \
      "endIncluded and circular cannot not be set to True at the same time"
      
    L = len(sequence)
    sequence = str(sequence)
    if circular:
        sequence += sequence[0:lword]
        pmax=L
    elif endIncluded:
       pmax=L
    else:
       pmax = L - lword + 1
    
    pos = xrange(0,pmax,step)
    
    for x in pos:
        yield sequence[x:x+lword]


def allWordIterator(size,_prefix=''):
    '''
    Iterate thought the list of all DNA word of
    size `size`.
    
    @param size: size of the DNA word
    @type size: int
    @param _prefix: internal parameter used for recursion purpose
    @type _prefix: string
    
    @return: an iterator on DNA word (str)
    @rtype: iterator
    '''
    if size:
        for l in _dna:
            for w in allWordIterator(size-1,_prefix+l):
                yield w
    else:
        yield _prefix
    
def wordSelector(words,accept=None,reject=None):
    '''
    Filter over a DNA word iterator.
    
    @param words: an iterable object other a list of DNA words
    @type words: an iterator
    @param accept: a list of predicat. Eeach predicat is a function
                   accepting one str parametter and returning a boolean
                   value.
    @type accept: list
    @param reject: a list of predicat. Eeach predicat is a function
                   accepting one str parametter and returning a boolean
                   value.
    @type reject: list
    
    @return: an iterator on DNA word (str)
    @rtype: iterator
    '''
    if accept is None:
        accept=[]
    if reject is None:
        reject=[]
    for w in words:
        accepted = reduce(lambda x,y: bool(x) and bool(y),
                          (p(w) for p in accept),
                          True)
        rejected = reduce(lambda x,y:bool(x) or bool(y),
                          (p(w) for p in reject),
                          False)
        if accepted and not rejected:
            yield w

def wordDist(w1,w2):
    '''
    estimate Hamming distance between two words of the same size.
    
    @param w1: the first word
    @type w1:  str
    @param w2: the second word
    @type w2:  str
    
    @return: the count of difference between the two words
    @rtype: int
    '''
    dist = reduce(lambda x,y:x+y,
                  (int(i[0]!=i[1]) 
                   for i in imap(None,w1,w2)))
    return dist
