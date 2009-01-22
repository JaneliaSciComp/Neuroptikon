from obitools import NucSequence
from obitools.location import locationGenerator,extractExternalRefs



class TagMatcherSequence(NucSequence):
    '''
    Class used to represent a nucleic sequence issued mapped
    on a genome by the tagMatcher software.
    '''
    
    def __init__(self,seq,cd,locs,dm,rm):
        NucSequence.__init__(self, seq, seq)
        self['locations']=locs
        self['conditions']=cd
        self['dm']=dm
        self['rm']=rm
        self['tm']=dm+rm
        
    def eminEmaxFilter(self,emin=None,emax=None):
        result = [x for x in self['locations'] 
                  if (emin is None or x['error'] >=emin)
                  and (emax is None or x['error'] <=emax)]
        self['locations']=result
        dm=0
        rm=0
        for x in result:
            if x.isDirect():
                dm+=1
            else:
                rm+=1
        self['dm']=dm
        self['rm']=rm
        self['tm']=dm+rm
        return self
