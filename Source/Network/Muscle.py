from Object import Object

class Muscle(Object):
    
    # TODO: stretch receptors?
    
    def __init__(self, network, *args, **keywords):
        Object.__init__(self, network, *args, **keywords)
        self.innervations = []
        self.stretchReceptors = []
    
    
    def inputs(self):
        return self.innervations
    
    
