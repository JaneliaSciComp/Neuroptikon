from Object import Object

class Pathway(Object):
    
    # TODO: handle input/output
    
    def __init__(self, startRegion, endRegion, *args, **keywords):
        Object.__init__(self, startRegion.network, *args, **keywords)
        self.neurites = []
        self.regions = set([startRegion, endRegion])

    def addNeurite(self, neurite):
        neurite.setPathway(self)
