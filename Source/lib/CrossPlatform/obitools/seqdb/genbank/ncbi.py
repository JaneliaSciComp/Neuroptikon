from urllib2 import urlopen
import sys
import re

import cStringIO

from obitools.eutils import EFetch
from parser import genbankParser,genpepParser
from parser import genbankIterator,genpepIterator

from obitools.utils import CachedDB


class NCBIGenbank(EFetch):
    def __init__(self):
        EFetch.__init__(self,db='nucleotide',
                        rettype='gbwithparts')
        
    def __getitem__(self,ac):
        if isinstance(ac,str):
            text = self.get(id=ac)
            seq = genbankParser(text)
            return seq
        else:
            query = ','.join([x for x in ac])
            data = cStringIO.StringIO(self.get(id=query))
            return genbankIterator(data)
    
    
      
      
class NCBIGenpep(EFetch):
    def __init__(self):
        EFetch.__init__(self,db='protein',
                        rettype='gbwithparts')
        
    def __getitem__(self,ac):
        if isinstance(ac,str):
            text = self.get(id=ac)
            seq = genpepParser(text)
            return seq
        else:
            query = ','.join([x for x in ac])
            data = cStringIO.StringIO(self.get(id=query))
            return genpepIterator(data)
            
class NCBIAccession(EFetch):
    
    _matchACS = re.compile(' +accession +"([^"]+)"')

    def __init__(self):
        EFetch.__init__(self,db='nucleotide',
                        rettype='seqid')

    def __getitem__(self,ac):
        if isinstance(ac,str):
            text = self.get(id=ac)
            rep = NCBIAccession._matchACS.search(text).group(1)
            return rep
        else:
            query = ','.join([x for x in ac])
            text = self.get(id=query)
            rep = (ac.group(1) for ac in NCBIAccession._matchACS.finditer(text))
            return rep

def Genbank(cache=None):
    gb = NCBIGenbank()
    if cache is not None:
        gb = CachedDB(cache, gb)
    return gb


def Genpep(cache=None):
    gp = NCBIGenpep()
    if cache is not None:
        gp = CachedDB(cache, gp)
    return gp


