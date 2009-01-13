from Object import Object


class Stimulus(Object):
    
    def __init__(self, network, target = None, modality = None, name = None):
        if target is None:
            raise ValueError, 'A stimulus must have a target'
        
        if name is None:
            name = modality.name
            
        Object.__init__(self, network, name)
        self.target = target
        self.modality = modality
        target.addStimulus(self)
    
    
    def outputs(self):
        return [self.target]
    
    
