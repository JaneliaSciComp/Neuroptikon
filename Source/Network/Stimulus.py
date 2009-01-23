from Object import Object


class Stimulus(Object):
    
    def __init__(self, network, target = None, modality = None, *args, **keywords):
        if target is None:
            raise ValueError, 'A stimulus must have a target'
        
        if not keywords.has_key('name') or keywords['name'] is None:
            keywords['name'] = modality.name
            
        Object.__init__(self, network, *args, **keywords)
        self.target = target
        self.modality = modality
        target.addStimulus(self)
    
    
    def outputs(self):
        return [self.target]
    
    
