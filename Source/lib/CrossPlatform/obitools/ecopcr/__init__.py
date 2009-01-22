from obitools import utils
from obitools import NucSequence
from obitools.utils import universalOpen, universalTell, fileSize, progressBar
import struct


class EcoPCRFile(utils.ColumnFile):
    def __init__(self,stream):
        utils.ColumnFile.__init__(self,
                                  stream, '|', True, 
                                  (str,int,int,
                                   str,int,str,
                                   int,str,int,
                                   str,int,str,
                                   str,str,int,
                                   str,int,int,
                                   str,str), "#")


    def next(self):
        data = utils.ColumnFile.next(self)
        seq = NucSequence(data[0],data[18],data[19])
        seq['seq_length_ori']=data[1]
        seq['taxid']=data[2]
        seq['rank']=data[3]
        seq['species']=data[4]
        seq['species_sn']=data[5]
        seq['genus']=data[6]
        seq['genus_sn']=data[7]
        seq['family']=data[8]
        seq['family_sn']=data[9]
        seq['strand']=data[12]
        seq['forward_primer']=data[13]
        seq['forward_error']=data[14]
        seq['reverse_primer']=data[15]
        seq['reverse_error']=data[16]
                 
        return seq
    
        
        
class EcoPCRDBFile(object):
    
    def _ecoRecordIterator(self,file):
        file = universalOpen(file)
        (recordCount,) = struct.unpack('> I',file.read(4))
    
        for i in xrange(recordCount):
            (recordSize,)=struct.unpack('>I',file.read(4))
            record = file.read(recordSize)
            yield record
