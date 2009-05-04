import wx
import os, sys
from wx.py import dispatcher
import xml.etree.ElementTree as ElementTree
from networkx import shortest_path
from Attribute import Attribute

    
class Object(object):
    
    def __init__(self, network, name = None, abbreviation = None, description = None):
        self.network = network
        self.networkId = self.network.nextUniqueId()
        
        self.name = name
        self.abbreviation = abbreviation
        self.description = description
        self.attributes = []
        
        self.stimuli = []
    
    
    @classmethod
    def fromXMLElement(cls, network, xmlElement):
        object = super(Object, cls).__new__(cls)
        object.network = network
        object.networkId = int(xmlElement.get('id'))
        
        object.name = xmlElement.findtext('Name')
        if object.name is None:
            object.name = xmlElement.findtext('name')
        object.abbreviation = xmlElement.findtext('Abbreviation')
        if object.abbreviation is None:
            object.abbreviation = xmlElement.findtext('abbreviation')
        object.description = xmlElement.findtext('Description')
        if object.description is None:
            object.description = xmlElement.findtext('description')
        
        object.attributes = []
        for element in xmlElement.findall('Attribute'):
            attribute = Attribute.fromXMLElement(object, element)
            if attribute is not None:
                object.attributes.append(attribute)
        
        object.stimuli = []
        
        # TODO: handle links
        # TODO: handle notes
        return object
    
    
    def toXMLElement(self, parentElement):
        objectElement = ElementTree.SubElement(parentElement, self.__class__.__name__, id = str(self.networkId))
        attrNames = [('name', 'Name'), ('abbreviation', 'Abbreviation'), ('description', 'Description')]
        for attrName, elementName in attrNames:
            attrValue = getattr(self, attrName)
            if attrValue is not None:
                ElementTree.SubElement(objectElement, elementName).text = attrValue
        for attribute in self.attributes:
            attribute.toXMLElement(objectElement)
        return objectElement
    
    
    @classmethod
    def displayName(cls):
        return gettext(cls.__name__)
    
    
    @classmethod
    def image(cls):
        image =wx.GetApp().loadImage(cls.__name__ + ".png")
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
        
