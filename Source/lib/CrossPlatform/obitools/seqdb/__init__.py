from obitools import NucSequence,AASequence
from obitools.format.genericparser import genericEntryIteratorGenerator
from obitools.location.feature import featureIterator

from itertools import chain

class AnnotatedSequence(object):

    def __init__(self,header,featureTable,secondaryAcs):
        self._header = header
        self._featureTableText = featureTable
        self._featureTable=None
        self._secondaryAcs=secondaryAcs
        self._hasTaxid=None

    def getHeader(self):
        return self._header


    def getFeatureTable(self,skipError=False):
        if self._featureTable is None:
            self._featureTable = [x for x in featureIterator(self._featureTableText,skipError)]
        return self._featureTable


    def getSecondaryAcs(self):
        return self._secondaryAcs
    
    def extractTaxon(self):
        if self._hasTaxid is None:
            
            if self._featureTable is not None:
                s = [f for f in self._featureTable if f.ftType=='source']
            else:
                s = featureIterator(self._featureTableText).next()
                if s.ftType=='source':
                    s = [s]
                else:
                    s = [f for f in self.featureTable if f.ftType=='source']
                    
            t =set(int(v[6:]) for v in chain(*tuple(f['db_xref'] for f in s if  'db_xref' in f))
                      if  v[0:6]=='taxon:') 

            if len(t)==1:
                self['taxid']=t.pop()
                self._hasTaxid=True
            else:
                self._hasTaxid=False

            t =set(chain(*tuple(f['organism'] for f in s if  'organism' in f))) 

            if len(t)==1:
                self['organism']=t.pop()

                             
    header = property(getHeader, None, None, "Header's Docstring")

    featureTable = property(getFeatureTable, None, None, "FeatureTable's Docstring")

    secondaryAcs = property(getSecondaryAcs, None, None, "SecondaryAcs's Docstring")
    
class AnnotatedNucSequence(AnnotatedSequence,NucSequence):
    '''
    
    '''
    def __init__(self,id,seq,de,header,featureTable,secondaryAcs,**info):
        NucSequence.__init__(self, id, seq, de,**info)
        AnnotatedSequence.__init__(self, header, featureTable, secondaryAcs)


class AnnotatedAASequence(AnnotatedSequence,AASequence):
    '''
    
    '''
    def __init__(self,id,seq,de,header,featureTable,secondaryAcs,**info):
        AASequence.__init__(self, id, seq, de,**info)
        AnnotatedSequence.__init__(self, header, featureTable, secondaryAcs)

           
nucEntryIterator=genericEntryIteratorGenerator(endEntry='^//')
aaEntryIterator=genericEntryIteratorGenerator(endEntry='^//')



