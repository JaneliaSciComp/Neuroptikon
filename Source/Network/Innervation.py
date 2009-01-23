from Object import Object

class Innervation(Object):
    
    def __init__(self, network, neurite, muscle, *args, **keywords):
        Object.__init__(self, network, *args, **keywords)
        self.neurite = neurite
        self.muscle = muscle
    
