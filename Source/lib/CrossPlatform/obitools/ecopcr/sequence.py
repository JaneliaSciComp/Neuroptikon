from obitools import NucSequence
from obitools.ecopcr import EcoPCRDBFile
from obitools.ecopcr.taxonomy import Taxonomy
from obitools.ecopcr.annotation import EcoPCRDBAnnotationWriter
from glob import glob
import struct
import gzip


class EcoPCRDBSequenceIterator(EcoPCRDBFile):

    def __init__(self,path,taxonomy=None):
        self._path = path
        
        if taxonomy is not None:
            self._taxonomy=taxonomy
        else:
            self._taxonomy=Taxonomy(path)
            
        self._seqfilesFiles =  glob('%s_???.sdx' % self._path)
        self._seqfilesFiles.sort()

    def __ecoSequenceIterator(self,file):
        for record in self._ecoRecordIterator(file):
            lrecord = len(record)
            lnames  = lrecord - (4*4+20)
            (taxid,seqid,deflength,seqlength,cptseqlength,string)=struct.unpack('> I 20s I I I %ds' % lnames, record)
            de = string[:deflength]
            seq = gzip.zlib.decompress(string[deflength:])
            bioseq = NucSequence(seqid,seq,de,taxidx=taxid,taxid=self._taxonomy._taxonomy[taxid][0])
            yield  bioseq
        
    def __iter__(self):
        for seqfile in self._seqfilesFiles:
            for seq in self.__ecoSequenceIterator(seqfile):
                yield seq
                
class EcoPCRDBSequenceWriter(object):
    
    def __init__(self,dbname,fileidx=1,taxonomy=None,ftid=None,type=None,definition=None):
        self._taxonomy=taxonomy
        self._filename="%s_%03d.sdx" % (dbname,fileidx)
        self._file = open(self._filename,'wb')
        self._sequenceCount=0
        
        self._file.write(struct.pack('> I',self._sequenceCount))
        

        
        if type is not None:
            assert ftid is not None,"You must specify an id attribute for features"
            self._annotation = EcoPCRDBAnnotationWriter(dbname, ftid, fileidx, type, definition)
        else: 
            self._annotation = None
        
    def _ecoSeqPacker(self,seq):
    
        compactseq = gzip.zlib.compress(str(seq),9)
        cptseqlength  = len(compactseq)
        delength   = len(seq.definition)
        
        totalSize = 4 + 20 + 4 + 4 + 4 + cptseqlength + delength
        
        if self._taxonomy is None:
            taxon=-1
        else:
            taxon=self._taxonomy.findIndex(seq['taxid'])
        
        packed = struct.pack('> I i 20s I I I %ds %ds' % (delength,cptseqlength),
                             totalSize,
                             taxon,
                             seq.id,
                             delength,
                             len(seq),
                             cptseqlength,
                             seq.definition,
                             compactseq)
        
        assert len(packed) == totalSize+4, "error in sequence packing"
    
        return packed

        
    def put(self,sequence):
        if self._taxonomy is not None:
            self.extractTaxon()
        self._file.write(self._ecoSeqPacker(sequence))
        if self._annotation is not None:
            self._annotation.put(sequence, self._sequenceCount)
        self._sequenceCount+=1
        
    def __del__(self):
        self._file.seek(0,0)
        self._file.write(struct.pack('> I',self._sequenceCount))
        self._file.close()
        
    
