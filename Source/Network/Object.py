import wx
import os
from pydispatch import dispatcher
from networkx import shortest_path

class Object(object):
    
    
    def __init__(self, network, name = None, abbreviation = None):
        self.network = network
        self.name = name
        self.abbreviation = abbreviation
        self.description = None
        self.stimuli = []
    
    
    @classmethod
    def displayName(cls):
        return gettext(cls.__name__)
    
    
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
    
    
    def __setattr__(self, name, value):
        # Send out a message whenever one of this object's values changes.  This is needed, for example, to allow the GUI to update when an object is modified via the console or a script.
        hasPreviousValue = hasattr(self, name)
        if hasPreviousValue:
            previousValue = getattr(self, name)
        object.__setattr__(self, name, value)
        if not hasPreviousValue or getattr(self, name) != previousValue:
            dispatcher.send(('set', name), self)
    
    
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
        
