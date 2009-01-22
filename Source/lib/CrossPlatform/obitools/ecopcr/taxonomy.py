import struct
import sys
import os
import gzip

from itertools import count,imap



from obitools.ecopcr import EcoPCRDBFile
from obitools.utils import universalOpen, universalTell, fileSize, progressBar


class Taxonomy(EcoPCRDBFile):
    
    
    def __init__(self,path):
        self._path = path
        self._taxonFile =  "%s.tdx" % self._path
        self._ranksFile =  "%s.rdx" % self._path
        self._namesFile =  "%s.ndx" % self._path
        self._taxonomy, self._index, self._ranks, self._name = self.__readNodeTable()
        
        self._speciesidx = self._ranks.index('species')
        self._genusidx   = self._ranks.index('genus')
        self._familyidx   = self._ranks.index('family')
        self._orderidx   = self._ranks.index('order')

    #####
    #
    # Iterator functions
    #
    #####
    
    
    
    
               
    def __ecoNameIterator(self):
        for record in self._ecoRecordIterator(self._namesFile):
            lrecord = len(record)
            lnames  = lrecord - 16
            (isScientificName,namelength,classLength,indextaxid,names)=struct.unpack('> I I I I %ds' % lnames, record)
            name=names[:namelength]
            classname=names[namelength:]
            yield (name,classname,indextaxid)
    
    
    def __ecoTaxonomicIterator(self):
        for record in self._ecoRecordIterator(self._taxonFile):
            lrecord = len(record)
            lnames  = lrecord - 16
            (taxid,rankid,parentidx,nameLength,name)=struct.unpack('> I I I I %ds' % lnames, record)
            yield  (taxid,rankid,parentidx,name)
                
    def __ecoRankIterator(self):
        for record in self._ecoRecordIterator(self._ranksFile):
            yield  record
    
    
    #####
    #
    # Indexes
    #
    #####
    
    def __ecoNameIndex(self):
        indexName = [x for x in self.__ecoNameIterator()]
        return indexName

    def __ecoRankIndex(self):
        rank = [r for r in self.__ecoRankIterator()]
        return rank

    def __ecoTaxonomyIndex(self):
        taxonomy = []
        index = {}
        i = 0;
        for x in self.__ecoTaxonomicIterator():
            taxonomy.append(x)
            index[x[0]] = i 
            i = i + 1
        return taxonomy, index

    def __readNodeTable(self):
        taxonomy, index = self.__ecoTaxonomyIndex()
        ranks = self.__ecoRankIndex()
        name = self.__ecoNameIndex()
        return taxonomy,index,ranks,name


    def findTaxonByTaxid(self,taxid):
        return self._taxonomy[self._index[taxid]]
    
    def findRankByName(self,rank):
        try:
            return self._ranks.index(rank)
        except ValueError:
            return None
        
    def findIndex(self,taxid):
        return self._index[taxid]


    #####
    #
    # PUBLIC METHODS
    #
    #####


    def subTreeIterator(self, taxid):
        "return subtree for given taxonomic id "
        idx = self._index[taxid]
        yield self._taxonomy[idx]
        for t in self._taxonomy:
            if t[2] == idx:
                for subt in self.subTreeIterator(t[0]):
                    yield subt
    
    def parentalTreeIterator(self, taxid):
        """
           return parental tree for given taxonomic id starting from
           first ancester to the root.
        """
        taxon=self.findTaxonByTaxid(taxid)
        while taxon[2]!= 0: 
            yield taxon
            taxon = self._taxonomy[taxon[2]]
        yield self._taxonomy[0]
    
    def lastCommonTaxon(self,*taxids):
        if not taxids:
            return None
        if len(taxids)==1:
            return taxids[0]
         
        if len(taxids)==2:
            t1 = [x[0] for x in self.parentalTreeIterator(taxids[0])]
            t2 = [x[0] for x in self.parentalTreeIterator(taxids[1])]
            t1.reverse()
            t2.reverse()
            
            count = min(len(t1),len(t2))
            i=0
            while(i < count and t1[i]==t2[i]):
                i+=1
            i-=1
            
            return t1[i]
        
        ancetre = taxids[0]
        for taxon in taxids[1:]:
            ancetre = self.lastCommonTaxon(ancetre,taxon)
            
        return ancetre
    
    def getScientificName(self,taxid):
        return self.findTaxonByTaxid(taxid)[3]
    
    def getRankId(self,taxid):
        return self.findTaxonByTaxid(taxid)[1]
    
    def getRank(self,taxid):
        return self._ranks[self.getRankId(taxid)]
    
    def getTaxonAtRank(self,taxid,rankid):
        if isinstance(rankid, str):
            rankid=self._ranks.index(rankid)
        try:
            return [x[0] for x in self.parentalTreeIterator(taxid)
                    if self.getRankId(x[0])==rankid][0]
        except IndexError:
            return None
        
    def getSpecies(self,taxid):
        return self.getTaxonAtRank(taxid, self._speciesidx)
    
    def getGenus(self,taxid):
        return self.getTaxonAtRank(taxid, self._genusidx)
    
    def getFamily(self,taxid):
        return self.getTaxonAtRank(taxid, self._familyidx)
    
    def getOrder(self,taxid):
        return self.getTaxonAtRank(taxid, self._orderidx)
    
    def rankIterator(self):
        for x in imap(None,self._ranks,xrange(len(self._ranks))):
            yield x
        
    
