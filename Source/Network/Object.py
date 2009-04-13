import wx
import os, sys
from wx.py import dispatcher
import xml.etree.ElementTree as ElementTree
from networkx import shortest_path
    
    
class Object(object):
    
    def __init__(self, network, name = None, abbreviation = None, description = None):
        self.network = network
        self.networkId = self.network.nextUniqueId()
        
        self.name = name
        self.abbreviation = abbreviation
        self.description = description
        
        self.stimuli = []
    
    
    @classmethod
    def fromXMLElement(cls, network, xmlElement):
        object = super(Object, cls).__new__(cls)
        object.network = network
        object.networkId = int(xmlElement.get('id'))
        
        object.name = xmlElement.findtext('name')
        object.abbreviation = xmlElement.findtext('abbreviation')
        object.description = xmlElement.findtext('description')
        
        object.stimuli = []
        
        # TODO: handle custom attributes
        # TODO: handle links
        # TODO: handle notes
        return object
    
    
    def toXMLElement(self, parentElement):
        objectElement = ElementTree.SubElement(parentElement, self.__class__.__name__, id = str(self.networkId))
        attrNames = ['name', 'abbreviation', 'description']
        for attrName in attrNames:
            attrValue = getattr(self, attrName)
            if attrValue is not None:
                ElementTree.SubElement(objectElement, attrName).text = attrValue
        return objectElement
    
    
    @classmethod
    def displayName(cls):
        return gettext(cls.__name__)
    
    
    @classmethod
    def image(cls):
        try:
            rootDir = os.path.dirname(sys.modules['__main__'].__file__)
            image = wx.Image(rootDir + os.sep + 'Images' + os.sep + cls.__name__ + ".png")
        except:
            image = None
        if image is None or not image.IsOk():
            image = wx.EmptyImage(32, 32)
        return image
    
    
    def __hash__(self):
        return self.networkId
    
    
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
        for nodeID in shortest_path(self.network.graph, self.networkId, otherObject.networkId):
            pathObject = self.network.objectWithId(nodeID)
            if pathObject != self:
                path.append(pathObject)
        return path
        
