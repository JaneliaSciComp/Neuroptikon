from Object import Object

class Pathway(Object):
    
    # TODO: handle input/output
    
    def __init__(self, startRegion, endRegion, name=None):
        Object.__init__(self, startRegion.network, name)
        self.neurites = []
        self.regions = set([startRegion, endRegion])

    def addNeurite(self, neurite):
        neurite.setPathway(self)
