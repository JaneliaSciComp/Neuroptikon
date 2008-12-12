from Object import Object


class Stimulus(Object):
    
    LIGHT, SMELL, TASTE, SOUND = range(4)
    
    def __init__(self, network, target=None, type=LIGHT, name=None):
        if name is None:
            if type == Stimulus.LIGHT:
                name = "Light"
            elif type == Stimulus.SMELL:
                name = "Smell"
            elif type == Stimulus.TASTE:
                name = "Taste"
            elif type == Stimulus.SOUND:
                name = "Sound"
            
        Object.__init__(self, network, name)
        self.target = target
        self.type = type
        target.addStimulus(self)
    
    
    def outputs(self):
        return [self.target]
    
    
