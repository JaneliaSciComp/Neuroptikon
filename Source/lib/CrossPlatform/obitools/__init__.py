'''

'''

from logging import debug
from weakref import ref


from sequenceencoder import Complement
from location import Location

class WrapperSetIterator(object):
    def __init__(self,s):
        self._i = set.__iter__(s)
    def next(self):
        return self._i.next()()
    def __iter__(self):
        return self
    
class WrapperSet(set):
    def __iter__(self):
        return WrapperSetIterator(self)
 

class BioSequence(object):
    '''
    BioSequence class is the base class for biological
    sequence representation.
    
    It provides storage of :
    
        - the sequence itself, 
        - an identifier,
        - a definition an manage 
        - a set of complementary information on a key / value principle.
    
    BioSequence is an abstract class and must be instanciated
    from its subclasses
    '''
    
    def __init__(self,id,seq,definition=None,**info):
        '''
        BioSequence constructor.
        
        @param id: sequence identifier
        @type id:  str
 
        @param seq: the sequence
        @type seq:  str

        @param definition: sequence definition (optional)
        @type definition: str

        @param info: extra named parameters can be add to associate complementary
        data to the sequence
        
        '''
        
        self._seq=str(seq).lower()
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

    def getSeq(self):
        return self._seq
    
    def extractTaxon(self):
        pass
        
    def __str__(self):
        return self.seq
    
    def __getitem__(self,key):
        if isinstance(key,Location):
            return key.extractSequence(self)
        elif isinstance(key, str):
            return self._info[key]
        elif isinstance(key, int):
            return self.seq[key]
        elif isinstance(key, slice):
            subseq=self.seq[key]
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
            return self.__class__(self.id, subseq, self.definition,**info)

        raise TypeError,'key must be an integer, a str or a slice'  
        
    def __setitem__(self,key,value):
        self._info[key]=value
        
    def __delitem__(self,key):
        if isinstance(key, str):
            del self._info[key]
        else:
            raise TypeError,key
        
    def __iter__(self):
        return iter(self.seq)
    
    def __len__(self):
        return len(str(self.seq))
    
    def __contains__(self,key):
        return key in self._info
    
    
    def getTags(self):
        return self._info
    
    def getWrappers(self):
        if not hasattr(self, '_wrappers'):
            self._wrappers=WrapperSet()
        return self._wrappers
    
    def register(self,wrapper):
        self.wrappers.add(ref(wrapper,self._unregister))
        
    def _unregister(self,ref):
        self.wrappers.remove(ref)
        
    wrappers = property(getWrappers,None,None,'')

    seq = property(getSeq, None, None, "Sequence data")

    definition = property(getDefinition, setDefinition, None, "Sequence Definition")

    id = property(getId, setId, None, 'Sequence identifier')
        
class NucSequence(BioSequence):
 
    def complement(self):
        cseq = Complement.encode(self.seq)
        rep = NucSequence(self.id,cseq,self.definition,**self._info)
        rep._info['complemented']=not rep._info.get('complemented',False)
        return rep
    
    def isNucleotide(self):
        return True
    

class AASequence(BioSequence):

    def isNucleotide(self):
        return False
    
   
class WrappedBioSequence(BioSequence):

    def __init__(self,id,reference,definition=None,encoder=None,**info):
        self._encoder=encoder
        encoder.check(reference)
        self.wrapped = reference
        self._id=id
        self.definition=definition
        self._info=info
        
    def getWrapped(self):
        return self._wrapped


    def setWrapped(self, value):
        value.register(self)
        debug("coucou from WrappedBioSequence.setWrapped") 
        self._wrapped = value
        debug("coucou from WrappedBioSequence.setWrapped") 

        
    def getDefinition(self):
        d = self._definition or ("%s Wrapped" % self.wrapped.definition)
        return d

    def __getitem__(self,key):
        debug("coucou from WrappedBioSequence.__getitem__") 
        if isinstance(key, str):
            if self._encoder is not None and key in self._encoder._info:
                return self._encoder._info[key]
            elif key in self._info:
                return self._info[key]
        else:
            return self.wrapped[key]
        
    def __getattr__(self,name):
        if self._encoder is not None:
            try:
                return getattr(self._encoder,name)
            except AttributeError:
                pass
        return getattr(self.wrapped, name)


    def getSeq(self):
        debug("coucou from WrappedBioSequence.getSeq") 
        if self._encoder is None:
            return self.wrapped.seq
        else:
            return self._encoder.encode(self.wrapped.seq)
    
    seq = property(getSeq, None, None, "Sequence data")
    definition = property(getDefinition,BioSequence.setDefinition, None, "Sequence Definition")

    wrapped = property(getWrapped, setWrapped, None, "Wrapped's Docstring")
         
    
    
def _isNucSeq(text):
    acgt   = 0
    notnuc = 0
    ltot   = len(text)
    for c in text.lower():
        if c in 'acgt-':
            acgt+=1
        if c not in Complement._comp:
            notnuc+=1
    return notnuc==0 and float(acgt)/ltot > 0.8


def bioSeqGenerator(id,seq,definition=None,**info):
    if _isNucSeq(seq):
        return NucSequence(id,seq,definition,**info)
    else:
        return AASequence(id,seq,definition,**info)
    
