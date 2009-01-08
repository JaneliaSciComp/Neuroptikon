class Neurotransmitter(object):
    
    # TODO: how to internationalize?
    
    def __init__(self, identifier, name, abbreviation = None):
        self.identifier = identifier
        self.name = name
        if abbreviation is None:
            self.abbreviation = name
        else:
            self.abbreviation = abbreviation
