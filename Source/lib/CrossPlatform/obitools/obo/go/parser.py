from obitools.obo.parser import OBOTerm
from obitools.obo.parser import OBOEntry
from obitools.obo.parser import stanzaIterator
from logging import debug

class GOEntry(OBOEntry):
    '''
       An entry of a GeneOntology .obo file. It can be a header (without a stanza name) or
       a stanza (with a stanza name between brackets). It inherits from the class dict.
    '''
        
   
class GOTerm(OBOTerm):
  
    '''
       A stanza named 'Term'. It inherits from the class OBOTerm.
    '''
    
    def __init__(self,stanza):
        
        ## use of the OBOEntry constructor.
        OBOTerm.__init__(self, stanza)
        
        assert 'namespace' in self and len(self['namespace'])==1, "An OBOTerm must belong to one of the cell_component, molecular_function or biological_process namespace"
    
    
def GOEntryFactory(stanza):
    '''
    Dispatcher of stanza.
    
    @param stanza: a stanza composed of several lines.
    @type stanza: text
    
    @return: an C{OBOTerm} | C{OBOEntry} instance
    
    @note: The dispatcher treats differently the stanza which are OBO "Term"
    and the others.
    '''
    
    stanzaType = OBOEntry.parseStanzaName(stanza)
    
    if stanzaType=="Term":
        return GOTerm(stanza)
    else:
        return OBOEntry(stanza)
    
    
def GOEntryIterator(file):
    entries =  stanzaIterator(file)
    for e in entries:
        debug(e)
        yield GOEntryFactory(e)
        
