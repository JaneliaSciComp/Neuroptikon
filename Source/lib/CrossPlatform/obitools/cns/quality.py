"""


"""

from obitools.fasta import fastaIterator
from obitools.cns import cnsTag
from obitools.location import Location

class QualitySequence(list):
    
    def __init__(self,id,seq,definition=None,**info):
        '''
        
        @param id:
        @param seq:
        @param definition:
        '''
        list.__init__(self,seq)
        self._info = dict(info)
        self.definition=definition
        self.id=id

    def getDefinition(self):
        '''
        Sequence definition getter
        
            @return: the sequence definition
            @rtype: str
            
        '''
        return self._definition

    def setDefinition(self, value):
        self._definition = value
        
    def getId(self):
        return self._id

    def setId(self, value):
        self._id = value
    
    def __getitem__(self,key):
        if isinstance(key,Location):
            return key.extractSequence(self)
        elif isinstance(key, str):
            return self._info[key]
        elif isinstance(key, int):
            return list.__getitem__(self,key)
        elif isinstance(key, slice):
            subseq=list.__getitem__(self,key)
            info = dict(self._info)
            if key.start is not None:
                start = key.start +1
            else:
                start = 1
            if key.stop is not None:
                stop = key.stop+1
            else:
                stop = len(self.seq)
            if key.step is not None:
                step = key.step
            else:
                step = 1
            
            info['cut']='[%d,%d,%s]' % (start,stop,step)
            return QualitySequence(self.id, subseq, self.definition,**info)

        raise TypeError,'key must be an integer, a str or a slice'  
        
    def __setitem__(self,key,value):
        self._info[key]=value
        
    def __delitem__(self,key):
        if isinstance(key, str):
            del self._info[key]
        else:
            raise TypeError,key
        
    def __iter__(self):
        return list.__iter__(self)
        
    def __contains__(self,key):
        return key in self._info
        
    def getTags(self):
        return self._info
        
    def complement(self):
        '''
        
        '''
        cseq = self[::-1]
        rep = QualitySequence(self.id,cseq,self.definition,**self._info)
        rep._info['complemented']=not rep._info.get('complemented',False)
        return rep
    
        
    definition = property(getDefinition, setDefinition, None, "Sequence Definition")

    id = property(getId, setId, None, 'Sequence identifier')


def _qualityJoinSeq(seqarray):
    text =  ' '.join([x.strip() for x in seqarray])
    return [int(x) for x in text.split()]

def qualityIterator(file):
    for q in fastaIterator(file, QualitySequence, cnsTag, _qualityJoinSeq):
        yield q
    
    
    