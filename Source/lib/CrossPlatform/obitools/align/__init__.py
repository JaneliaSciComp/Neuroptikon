from obitools import BioSequence

class Alignement(list):

    def _assertData(self,data):
        assert isinstance(data, BioSequence),'You must only add bioseq to an alignement'
        if hasattr(self, '_alignlen'):
            assert self._alignlen==len(data),'All aligned sequences must have the same length'
        else:
            self._alignlen=len(data)  
        return data  
            
    def append(self,data):
        data = self._assertData(data)
        list.append(self,data)
        
    def __setitem__(self,index,data):
        
        data = self._assertData(data)
        list.__setitem__(self,index,data)
        
    def getSite(self,key):
        if isinstance(key,int):
            return [x[key] for x in self]
        
    def isFullGapSite(self,key):
        return reduce(lambda x,y: x and y,(z=='-' for z in self.getSite(key)),True)
    
    def isGappedSite(self,key):
        return reduce(lambda x,y: x or y,(z=='-' for z in self.getSite(key)),False)

def alignmentReader(file,sequenceIterator):
    seqs = sequenceIterator(file)
    alignement = Alignement()
    for seq in seqs:
        alignement.append(seq)
    return alignement
        
        
