from Object import Object

class Innervation(Object):
    
    def __init__(self, network, neurite, muscle, name=None):
        Object.__init__(self, network, name)
        self.neurite = neurite
        self.muscle = muscle
    
