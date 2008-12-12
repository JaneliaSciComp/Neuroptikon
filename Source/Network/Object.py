import wx

class Object:
    def __init__(self, network, name=None):
        self.network = network
        self.name = name
        self.description = None
        self.abbreviation = None
        self.stimuli = []
    
    
    def __hash__(self):
        return id(self)
    
    
    def inputs(self):
        return self.stimuli
    
    
    def outputs(self):
        return []
    
    
    def addStimulus(self, stimulus):
        self.stimuli.append(stimulus)
    
    
    def image(self):
        imageFileName = "Network/" + self.__class__.__name__ + ".png"
        return wx.Image(imageFileName)
        
