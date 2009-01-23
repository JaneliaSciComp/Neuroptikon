from LibraryItem import LibraryItem
from OntologyTerm import OntologyTerm
import obitools.obo.parser as obo

class Ontology(LibraryItem):
    
    @classmethod
    def listProperty(cls):
        return 'ontologies'
    
    
    @classmethod
    def lookupProperty(cls):
        return 'ontology'
    
    
    def __init__(self, identifier = None, *args, **keywordArgs):
        LibraryItem.__init__(self, identifier, *args, **keywordArgs)
        self.rootTerms = []
        self._termDict = {}
    
    
    def importOBO(self, filePath):
        unresolvedRefs = []
        for entry in obo.OBOEntryIterator(open(filePath)):
            if entry.isHeader:
                pass
            elif entry.stanzaName == 'Term':
                term = OntologyTerm(identifier = entry.id.value, name = entry.name.value)
                self._termDict[term.identifier] = term
                
                # If the term has 'part-of' relationship then try to set the parent term.
                parentId = None
                for relationship in entry.relationship or []:
                    if relationship.relationship == 'part_of':
                        parentId = relationship.value
                        if self._termDict.has_key(parentId):
                            parent = self._termDict[parentId]
                            term.partOf = parent
                            parent.parts.append(term)
                        else:
                            # The parent of this term has not been loaded yet.  Store its ID and look it up later.
                            term.partOf = parentId
                            unresolvedRefs.append(term)
                if parentId is None:
                    self.rootTerms.append(term)
                
                # Grab the abbreviation if there is one.
                for synonym in entry.synonyms or []:
                    if 'ABBREVIATION' in synonym.types:
                        term.abbreviation = synonym.value
            else:
                pass
        
        # Set the parent of any terms that came before their parent in the file.
        for term in unresolvedRefs:
            if term.partOf not in self._termDict:
                self.rootTerms = []
                self._termDict = {}
                raise ValueError, _("The parent (%s) of term '%s' (%s) is not in the ontology.") % (term.partOf, term.name, term.identifier)
            parent = self._termDict[term.partOf]
            term.partOf = parent
            parent.parts.append(term)
    
    
    def findTerm(self, identifier = None, name = None, abbreviation = None):
        matchingTerm = None
        
        if identifier is not None:
            if self._termDict.has_key(identifier):
                matchingTerm = self._termDict[identifier]
        else:
            for term in self._termDict.itervalues():
                if (name is not None and name.upper() == term.name.upper()) or \
                   (abbreviation is not None and term.abbreviation is not None and abbreviation.upper() == term.abbreviation.upper()):
                    matchingTerm = term
                    break
        
        return matchingTerm
    
    
    def findTerms(self, namePart = None, abbreviationPart = None):
        matchingTerms = []
        
        for term in self._termDict.itervalues():
            if (namePart is not None and term.name is not None and term.name.upper().find(namePart.upper()) != -1) or \
               (abbreviationPart is not None and term.abbreviation is not None and term.abbreviation.upper().find(abbreviationPart.upper()) != -1):
                matchingTerms.append(term)
        
        return matchingTerms
