from Object import Object


class Arborization(Object):
    
    def __init__(self, neurite, region, sendsOutput=None, receivesInput=None):
        Object.__init__(self, neurite.network)
        self.neurite = neurite
        self.region = region
        self.sendsOutput = sendsOutput      # does the neurite send output to the arbor?      None = unknown
        self.receivesInput = receivesInput  # does the neurite receive input from the arbor?  None = unknown
