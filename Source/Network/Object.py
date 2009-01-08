import wx
import os
from networkx import shortest_path

class Object(object):
    
    
    def __init__(self, network, name=None):
        self.network = network
        self.name = name
        self.description = None
        self.abbreviation = None
        self.stimuli = []
    
    
    @classmethod
    def displayName(cls):
        return _(cls.__name__)
    
    
    @classmethod
    def image(cls):
        try:
            image = wx.Image("Network" + os.sep + cls.__name__ + ".png")
        except:
            pass
        if image is None or not image.IsOk():
            image = wx.EmptyImage(32, 32)
        return image
    
    
    def __hash__(self):
        return id(self)
    
    
    def inputs(self):
        return self.stimuli
    
    
    def outputs(self):
        return []
    
    
    def addStimulus(self, stimulus):
        self.stimuli.append(stimulus)
        
    
    def shortestPathTo(self, otherObject):
        path = []
        for nodeID in shortest_path(self.network.graph, id(self), id(otherObject)):
            pathObject = self.network.objectWithId(nodeID)
            if pathObject != self:
                path.append(pathObject)
        return path
        
