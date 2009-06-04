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
    
    
    def includeInScript(self, atTopLevel = False):
        return True
    
    
    def needsScriptRef(self):
        if len(self.attributes) > 0 or len(self.stimuli) > 0:
            return True
        
        for display in self.network.displays:
            if len(display.visiblesForObject(self)) > 0:
                return True
        
        # No other code will need to refer to this object.
        return False
    
    
    def createScriptRef(self, scriptRefs):
        # TODO: check if abbreviation or name is unique and create variable name from that?
        className = self.__class__.__name__
        if className in scriptRefs:
            instanceCount = scriptRefs[className]
        else:
            instanceCount = 0
        scriptRefs[className] = instanceCount + 1
        scriptRefs[self.networkId] = className.lower() + str(instanceCount + 1)
        return scriptRefs[self.networkId]
    
    
    def creationScriptCommand(self, scriptRefs):
        return 'network.create' + self.__class__.__name__
    
    
    def creationScriptParams(self, scriptRefs):
        args = []
        keywords = {}
        if self.name is not None:
            keywords['name'] = '\'' + self.name.replace('\\', '\\\\').replace('\'', '\\\'') + '\''
        if self.abbreviation is not None:
            keywords['abbreviation'] = '\'' + self.abbreviation.replace('\\', '\\\\').replace('\'', '\\\'') + '\''
        if self.description is not None:
            keywords['description'] = '\'' + self.description.replace('\\', '\\\\').replace('\'', '\\\'') + '\''
        return (args, keywords)
    
    
    def creationScriptChildren(self):
        return list(self.attributes)
    
    
    def toScriptFile(self, scriptFile, scriptRefs):
        if self.includeInScript():
            if self.needsScriptRef():
                scriptFile.write(self.createScriptRef(scriptRefs) + ' = ')
            
            scriptFile.write(self.creationScriptCommand(scriptRefs) + '(')
            args, keywords = self.creationScriptParams(scriptRefs)
            for keyword, value in keywords.iteritems():
                args.append(keyword + ' = ' + value)
            scriptFile.write(', '.join(args) + ')\n')
            
            prevPos = scriptFile.tell()
            
            for child in self.creationScriptChildren():
                child.toScriptFile(scriptFile, scriptRefs)
    
    
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
    
    
    def defaultName(self):
        return None
    
    
    def connections(self):
        return list(self.stimuli)
    
    
    def inputs(self):
        return list(self.stimuli)
    
    
    def outputs(self):
        return []
    
    
    def stimulate(self, modality = None, *args, **keywordArgs):
        from Stimulus import Stimulus
        stimulus = Stimulus(self.network, target = self, modality = modality, *args, **keywordArgs)
        self.stimuli.append(stimulus)
        self.network.addObject(stimulus)
        return stimulus
        
    
    def shortestPathTo(self, otherObject):
        path = []
        for nodeID in shortest_path(self.network.graph, self.networkId, otherObject.networkId):
            pathObject = self.network.objectWithId(nodeID)
            if pathObject != self:
                path.append(pathObject)
        return path
    
    
    def addAttribute(self, name = None, type = None, value = None):
        """addAttribute(name = None, type = None, value = None) -> Attribute instance
        
        The type parameter should be one of the Attribute.*_TYPE values.
        
        >>> neuron.addAttribute('Confirmed', Attribute.BOOLEAN_VALUE, True)"""
        
        if name is None or type is None or value is None:
            raise ValueError, gettext('The name, type and value parameters must be specified when adding an attribute.')
        
        attribute = Attribute(self, name, type, value)
        self.attributes.append(attribute)
        dispatcher.send(('set', 'attributes'), self)
        return attribute
    
    
    def getAttribute(self, name):
        """getAttribute(name) -> Attribute instance
        
        Return the first attribute of this object with the given name, or None if there is no matching attrbute."""
        for attribute in self.attributes:
            if attribute.name == name:
                return attribute
        return None
