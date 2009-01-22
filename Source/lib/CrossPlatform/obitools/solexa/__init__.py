from obitools import utils
from obitools import NucSequence
from obitools.dnahash import hashCodeIterator


class SolexaSequence(NucSequence):
    def __init__(self,id,seq,definition=None,quality=None,**info):
        NucSequence.__init__(self, id, seq, definition,**info)
        self._quality=quality
        self._hash=None
        
    def getQuality(self):
        if isinstance(self._quality, str):
            self._quality=[int(x) for x in self._quality.split()]
        return self._quality
    
    
    def __hash__(self):
        if self._hash is None:
            self._hash = hashCodeIterator(self.seq, len(self.seq), 16, 0).next()[1].pop()
        return self._hash

class SolexaFile(utils.ColumnFile):
    def __init__(self,stream):
        utils.ColumnFile.__init__(self,
                                  stream, ':', True, 
                                  (str,
                                   int,int,int,int,
                                   str,
                                   str), "#")


    def next(self):
        data = utils.ColumnFile.next(self)
        seq = SolexaSequence('%d_%d_%d_%d'%(data[1],data[2],data[3],data[4]),
                             data[5],
                             quality=data[6])
        seq['machine']=data[0]
        seq['channel']=data[1]
        seq['tile']=data[2]
        seq['pos_x']=data[3]
        seq['pos_y']=data[4]

        #assert len(seq['quality'])==len(seq),"Error in file format"
        return seq
