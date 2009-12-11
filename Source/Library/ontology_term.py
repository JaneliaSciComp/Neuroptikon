class OntologyTerm(object):

    def __init__(self, ontology, oboStanza = None, *args, **keywordArgs):
        object.__init__(self, *args, **keywordArgs)
        
        self.ontology = ontology
        self.oboStanza = oboStanza
        self.identifier = None
        self.name = None
        self.abbreviation = None
        self.partOf = None
        self.parts = []
        self.obsolete = False
        
        if self.oboStanza is not None:
            self.identifier = self.oboStanza.id.value
            self.name = self.oboStanza.name.value
            
            # If this term has 'part-of' relationship then try to set the parent term.
            for relationship in self.oboStanza.relationship or []:
                if relationship.relationship == 'part_of':
                    parentId = relationship.value
                    if parentId in self.ontology:
                        parentTerm = self.ontology[parentId]
                        self.partOf = parentTerm
                        parentTerm.parts.append(self)
                    else:
                        # The parent of this term has not been loaded yet.  Store its ID and look it up later.
                        self.partOf = parentId
            
            # Grab any abbreviation.
            for synonym in self.oboStanza.synonyms or []:
                if 'ABBREVIATION' in synonym.types:
                    self.abbreviation = synonym.value
                # TODO: grab other synonyms?
            
            if self.oboStanza.definition is not None and self.oboStanza.definition.value == 'Obsolete.':
                self.obsolete = True
    
    
    
    def browse(self):
        # Make sure the ontology is open
        self.ontology.browse()
        
        self.ontology.frame.selectTerm(self)
