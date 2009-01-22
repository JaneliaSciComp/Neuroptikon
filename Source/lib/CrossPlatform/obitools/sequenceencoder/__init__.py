class SequenceEncoder(object):
    def encode(seq):
        return seq
    
    encode=staticmethod(encode)  
    
    def check(wrapped):
        pass

    check = staticmethod(check)

class Complement(SequenceEncoder):
    _comp={'a': 't', 'c': 'g', 'g': 'c', 't': 'a',
           'r': 'y', 'y': 'r', 'k': 'm', 'm': 'k', 
           's': 's', 'w': 'w', 'b': 'v', 'd': 'h', 
           'h': 'd', 'v': 'b', 'n': 'n', 'u': 'a',
           '-': '-'}

    _info={'complemented':True}

    def encode(seq):
        cseq = [Complement._comp.get(x.lower(),'n') for x in seq]
        cseq.reverse()
        return ''.join(cseq)
    
    encode=staticmethod(encode)
    
    def check(wrapped):
        assert wrapped.isNucleotide()

    check = staticmethod(check)
        
    def complement(seq):
        return seq.wrapped
    
   
        