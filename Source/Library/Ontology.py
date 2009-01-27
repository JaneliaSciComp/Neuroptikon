from LibraryItem import LibraryItem
from OntologyTerm import OntologyTerm
import obitools.obo.parser as obo

class Ontology(LibraryItem, dict):
    
    @classmethod
    def listProperty(cls):
        return 'ontologies'
    
    
    @classmethod
    def lookupProperty(cls):
        return 'ontology'
    
    
    def __init__(self, identifier = None, *args, **keywordArgs):
        LibraryItem.__init__(self, identifier, *args, **keywordArgs)
        self.rootTerms = []
    
    
    def importOBO(self, filePath):
        unresolvedRefs = []
        for entry in obo.OBOEntryIterator(open(filePath)):
            if entry.isHeader:
                pass
            elif entry.stanzaName == 'Term':
                term = OntologyTerm(self, oboStanza = entry)
                self[term.identifier] = term
                
                if term.partOf is None:
                    self.rootTerms.append(term)
                elif not isinstance(term.partOf, OntologyTerm):
                    unresolvedRefs.append(term)
        
        # Set the parent of any terms that came before their parent in the file.
        for term in unresolvedRefs:
            if term.partOf not in self:
                self.rootTerms = []
                self.clear()
                raise ValueError, _("The parent (%s) of term '%s' (%s) is not in the ontology.") % (term.partOf, term.name, term.identifier)
            parent = self[term.partOf]
            term.partOf = parent
            parent.parts.append(term)
    
    
    def findTerm(self, name = None, abbreviation = None):
        matchingTerm = None
        
        for term in self.itervalues():
            if (name is not None and name.upper() == term.name.upper()) or \
               (abbreviation is not None and term.abbreviation is not None and abbreviation.upper() == term.abbreviation.upper()):
                matchingTerm = term
                break
        
        return matchingTerm
    
    
    def findTerms(self, namePart = None, abbreviationPart = None):
        matchingTerms = []
        
        for term in self.itervalues():
            if (namePart is not None and term.name is not None and term.name.upper().find(namePart.upper()) != -1) or \
               (abbreviationPart is not None and term.abbreviation is not None and term.abbreviation.upper().find(abbreviationPart.upper()) != -1):
                matchingTerms.append(term)
        
        return matchingTerms
