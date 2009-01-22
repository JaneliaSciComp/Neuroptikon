_A=[0]
_C=[1]
_G=[2]
_T=[3]
_R= _A + _G
_Y= _C + _T
_M= _C + _A
_K= _T + _G
_W= _T + _A
_S= _C + _G
_B= _C + _G + _T
_D= _A + _G + _T
_H= _A + _C + _T
_V= _A + _C + _G
_N= _A + _C + _G + _T

_dnahash={'a':_A,
          'c':_C,
          'g':_G,
          't':_T,
          'r':_R,
          'y':_Y,
          'm':_M,
          'k':_K,
          'w':_W,
          's':_S,
          'b':_B,
          'd':_D,
          'h':_H,
          'v':_V,
          'n':_N,
          }

def hashCodeIterator(sequence,wsize,degeneratemax=0,offset=0):
    errors   = 0
    emask    = [0] * wsize
    epointer = 0
    size = 0
    position = offset
    hashs = set([0])
    hashmask = 0
    for i in xrange(wsize):
        hashmask <<= 2
        hashmask +=3
    
    for l in sequence:
        l = l.lower()
        hl = _dnahash[l]
        
        if emask[epointer]:
            errors-=1
            emask[epointer]=0
            
        if len(hl) > 1:
            errors +=1
            emask[epointer]=1
            
        epointer+=1
        epointer%=wsize
            
        if errors > degeneratemax:
            hl=set([hl[0]])  
            
        hashs=set((((hc<<2) | cl) & hashmask)
                  for hc in hashs
                  for cl in hl) 
        
        if size < wsize:
            size+=1
        
        if size==wsize:
            if errors <= degeneratemax:
                yield (position,hashs,errors)
            position+=1
        
def hashSequence(sequence,wsize,degeneratemax=0,offset=0,hashs=None):       
    if hashs is None:
        hashs=[[] for x in xrange(4**wsize)]
        
    for pos,keys,errors in hashCodeIterator(sequence, wsize, degeneratemax, offset):
        for k in keys:
            hashs[k].append(pos)
                    
    return hashs

def hashSequences(sequences,wsize,maxpos,degeneratemax=0):       
    hashs=None
    offsets=[]
    offset=0
    for s in sequences:
        offsets.append(offset)
        hashSequence(s,wsize,degeneratemax=degeneratemax,offset=offset,hashs=hashs)
        offset+=len(s)
        
    return hashs,offsets


    
            
         