import wx
from networkx import shortest_path

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
        
    
    def shortestPathTo(self, otherObject):
        path = []
        for nodeID in shortest_path(self.network.graph, id(self), id(otherObject)):
            pathObject = self.network.objectWithId(nodeID)
            if pathObject != self:
                path.append(pathObject)
        return path
        
