import struct

class EcoPCRDBAnnotationWriter(object):
    '''
    Class used to write Annotation description in EcoPCRDB format.
    
    EcoPCRDBAnnotationWriter is oftenly called through the EcoPCRDBSequenceWriter class
    
    @see: L{ecopcr.sequence.EcoPCRDBSequenceWriter}
    '''
    
    def __init__(self,dbname,id,fileidx=1,type=('CDS'),definition=None):
        '''
        class constructor
        
        @param dbname: name of ecoPCR database
        @type dbname: C{str}
        @param id: name of the qualifier used as feature id
        @type id: C{str}
        @param fileidx:
        @type fileidx: C{int}
        @param type:
        @type type: C{list} or C{tuple}
        @param definition: 
        @type definition: C{str}
        '''
        self._type = type
        self._definition = definition
        self._id = id
        self._filename="%s_%03d.adx" % (dbname,fileidx)
        self._file = open(self._filename,'wb')
        self._sequenceIdx=0
        

        ftname  ="%s.fdx" % (dbname)
        ft = open(ftname,'wb')
        
        self._fttypeidx=dict(map(None,type,xrange(len(type))))
        
        ft.write(struct.pack('> I',len(type)))
        
        for t in type:
            ft.write(self._ecoFtTypePacker(t))
            
        ft.close()
        
        self._annotationCount=0
        self._file.write(struct.pack('> I',self._annotationCount))
        
        
    def _ecoFtTypePacker(self,type):
        totalSize = len(type)
        packed = struct.pack('> I %ds' % totalSize,totalSize,type)

        assert len(packed) == totalSize+4, "error in feature type packing"
    
        return packed
                             
    def _ecoAnnotationPacker(self,feature,seqidx):
        begin  = feature.begin-1
        end    = feature.end
        type   = self._fttypeidx[feature.ftType]
        strand = feature.isDirect()
        id     = feature[self._id][0]
        if self._definition in feature:
            definition = feature[self._definition][0]
        else:
            definition = ''
        
        assert strand is not None,"Only strand defined features can be stored"

        deflength = len(definition)
        
        totalSize = 4 + 4 + 4 + 4 + 4 + 20 + 4 + deflength
        
        packed = struct.pack('> I I I I I 20s I %ds' % (deflength),
                             totalSize,
                             seqidx,
                             begin,
                             end,
                             type,
                             int(strand),
                             id,
                             deflength,
                             definition)
        
        assert len(packed) == totalSize+4, "error in annotation packing"
    
        return packed

        
    def put(self,sequence,seqidx=None):
        if seqidx is None:
            seqidx = self._sequenceIdx
            self._sequenceIdx+=1
        for feature in sequence.getFeatureTable():
            if feature.ftType in self._type:
                self._annotationCount+=1
                self._file.write(self._ecoAnnotationPacker(feature,seqidx))

    def __del__(self):
        self._file.seek(0,0)
        self._file.write(struct.pack('> I',self._annotationCount))
        self._file.close()
