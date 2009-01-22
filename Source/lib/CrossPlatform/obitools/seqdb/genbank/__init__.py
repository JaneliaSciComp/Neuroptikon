from obitools.seqdb import AnnotatedNucSequence, AnnotatedAASequence
from obitools.location import locationGenerator,extractExternalRefs



class GbSequence(AnnotatedNucSequence):
    '''
    Class used to represent a nucleic sequence issued from Genbank.
    '''
    
    
class GpepSequence(AnnotatedAASequence):
    '''
    Class used to represent a peptidic sequence issued from Genpep.   
    '''
    
    def __init__(self,id,seq,de,header,featureTable,secondaryAcs,**info):
        AnnotatedAASequence.__init__(self,id, seq, de, header, featureTable, secondaryAcs,**info)
        self.__hasNucRef=None
    
    def __getGeneRef(self):
        if self.__hasNucRef is None:
            self.__hasNucRef=False
            cds = [x for x in self.featureTable
                   if x.ftType=='CDS' 
                   and 'coded_by' in x]

            if cds:
                source = cds[0]['coded_by'][0]
                if 'transl_table' in cds[0]:
                    tt = cds[0]['transl_table'][0]
                else:
                    tt=None
                ac,loc = extractExternalRefs(source)
                
                if len(ac)==1:
                    ac = ac.pop()
                    self.__hasNucRef=True
                    self.__nucRef = (ac,loc,tt)
                    
        
    
    def geneAvailable(self):
        '''
        Predicat indicating if reference to the nucleic sequence encoding
        this protein is available in feature table.
        
        @return: True if gene description is available
        @rtype: bool
        '''
        self.__getGeneRef()
        return self.__hasNucRef is not None and self.__hasNucRef
        
    
    def getCDS(self,database):
        '''
        Return the nucleic sequence coding for this protein if
        data are available.
        
        @param database: a database object where looking for the sequence
        @type database: a C{dict} like object
        
        @return: a NucBioseq instance carreponding to the CDS
        @rtype: NucBioSeq
        
        @raise AssertionError: if no gene references are available
        @see: L{geneAvailable}
        
        '''
        
        assert self.geneAvailable(), \
            "No information available to retreive gene sequence"

        ac,loc,tt = self.__nucRef
        seq = database[ac]
        seq.extractTaxon()
        gene = seq[loc]   
        if tt is not None:
            gene['transl_table']=tt
        return gene
    
            
    

