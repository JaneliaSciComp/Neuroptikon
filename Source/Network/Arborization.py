from Object import Object


class Arborization(Object):
    
    def __init__(self, neurite, region, sendsOutput=None, receivesInput=None, *args, **keywords):
        Object.__init__(self, neurite.network, *args, **keywords)
        self.neurite = neurite
        self.region = region
        self.sendsOutput = sendsOutput      # does the neurite send output to the arbor?      None = unknown
        self.receivesInput = receivesInput  # does the neurite receive input from the arbor?  None = unknown
