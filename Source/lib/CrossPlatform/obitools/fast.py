"""
    implement fastn/fastp sililarity search algorithm for BioSequence.
"""

class Fast(object):
    
    def __init__(self,seq,kup=2):
        '''
        @param seq: sequence to hash
        @type seq: BioSequence
        @param kup: word size used for hashing process
        @type kup: int
        '''
        hash={}
        seq = str(seq)
        for word,pos in ((seq[i:i+kup].upper(),i) for i in xrange(len(seq)-kup)):
            if word in hash:
                hash[word].append(pos)
            else:
                hash[word]=[pos]
        
        self._kup = kup
        self._hash= hash
        self._seq = seq
        
    def __call__(self,seq):
        '''
        Align one sequence with the fast hash table.
        
        @param seq: the sequence to align
        @type seq: BioSequence
        
        @return: where smax is the
                 score of the largest diagonal and pmax the
                 associated shift 
        @rtype: a int tuple (smax,pmax)
        '''
        histo={}
        seq = str(seq).upper()
        hash= self._hash
        kup = self._kup
        
        for word,pos in ((seq[i:i+kup],i) for i in xrange(len(seq)-kup)):
            matchedpos = hash.get(word,[])
            for p in matchedpos:
                delta = pos - p
                histo[delta]=histo.get(delta,0) + 1
        smax = max(histo.values())
        pmax = [x for x in histo if histo[x]==smax]
        return smax,pmax
    
    def __len__(self):
        return len(self._seq)
    

    
