from Object import Object

class Muscle(Object):
    
    # TODO: stretch receptors?
    
    def __init__(self, network, name=None):
        Object.__init__(self, network, name)
        self.innervations = []
        self.stretchReceptors = []
    
    
    def inputs(self):
        return self.innervations
    
    
