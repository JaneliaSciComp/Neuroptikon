class OntologyTerm(object):

    def __init__(self, identifier = None, name = None, abbreviation = None, *args, **keywordArgs):
        object.__init__(self, *args, **keywordArgs)
        self.identifier = identifier
        self.name = name
        self.abbreviation = abbreviation
        self.partOf = None
        self.parts = []
    
