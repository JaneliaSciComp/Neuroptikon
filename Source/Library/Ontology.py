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
                parentId = None
                for relationship in entry.relationship or []:
                    if relationship.relationship == 'part_of':
                        parentId = relationship.value
                        if self._termDict.has_key(parentId):
                            parent = self._termDict[parentId]
                            term.partOf = parent
                            parent.parts.append(term)
                        else:
                            term.partOf = parentId
                            unresolvedRefs.append(term)
                for synonym in entry.synonyms or []:
                    if 'ABBREVIATION' in synonym.types:
                        term.abbreviation = synonym.value
                if parentId is None:
                    self.rootTerms.append(term)
            else:
                pass
        
        for term in unresolvedRefs:
            parent = self._termDict[term.partOf]
            term.partOf = parent
            parent.parts.append(term)
    
    
    def findTerm(self, identifier = None, name = None, abbreviation = None):
        matchingTerm = None
        
        if identifier is not None:
            if self._termDict.has_key(identifier):
                matchingTerm = self._termDict[identifier]
        else:
            termsToMatch = list(self.rootTerms)
            while len(termsToMatch) > 0:
                term = termsToMatch[0]
                termsToMatch[0:1] = []
                termsToMatch.extend(term.parts)
                if (name is not None and name.upper() == term.name.upper()) or \
                   (abbreviation is not None and term.abbreviation is not None and abbreviation.upper() == term.abbreviation.upper()):
                    matchingTerm = term
                    break
        
        return matchingTerm
