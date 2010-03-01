#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

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
            self.identifier = self.oboStanza.tags['id'][0].value
            self.name = self.oboStanza.tags['name'][0].value
            
            # If this term has 'part-of' relationship then try to set the parent term.
            if 'relationship' in self.oboStanza.tags:
                relationship = self.oboStanza.tags['relationship'][0]
                if relationship.value.startswith('part_of '):
                    parentId = relationship.value[8:]
                    if parentId in self.ontology:
                        parentTerm = self.ontology[parentId]
                        self.partOf = parentTerm
                        parentTerm.parts.append(self)
                    else:
                        # The parent of this term has not been loaded yet.  Store its ID and look it up later.
                        self.partOf = parentId
            
            # Grab any abbreviation.
            if 'synonym' in self.oboStanza.tags:
                synonym = self.oboStanza.tags['synonym'][0]
                for modifier in synonym.modifiers or ():
                    if 'ABBREVIATION' in modifier:
                        self.abbreviation = synonym.value
                        break
                # TODO: grab other synonyms?
            
            if 'def' in self.oboStanza.tags:
                if self.oboStanza.tags['def'][0].value == 'obsolete':
                    self.obsolete = True
    
    
    
    def browse(self):
        # Make sure the ontology is open
        self.ontology.browse()
        
        self.ontology.frame.selectTerm(self)
