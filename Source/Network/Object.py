import wx
import os, sys
from pydispatch import dispatcher
import xml.etree.ElementTree as ElementTree
from networkx import shortest_path
from Attribute import Attribute

    
class Object(object):
    
    def __init__(self, network, name = None, abbreviation = None, description = None):
        """
        The Object class is the base-class for every object in a :class:`network <Network.Network.Network>`.
        
        Any number of user-defined attributes or stimuli can be added to an object.  The connectivity of objects can also be investigated.
        """
        
        self.network = network
        self.networkId = self.network._generateUniqueId()
        
        self.name = name
        self.abbreviation = abbreviation
        self.description = description
        self._attributes = []
        
        self.stimuli = []
    
    
    @classmethod
    def _fromXMLElement(cls, network, xmlElement):
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
        
        object._attributes = []
        for element in xmlElement.findall('Attribute'):
            attribute = Attribute._fromXMLElement(object, element)
            if attribute is not None:
                object._attributes.append(attribute)
        
        object.stimuli = []
        
        # TODO: handle links
        # TODO: handle notes
        return object
    
    
    def _toXMLElement(self, parentElement):
        objectElement = ElementTree.SubElement(parentElement, self.__class__.__name__, id = str(self.networkId))
        attrNames = [('name', 'Name'), ('abbreviation', 'Abbreviation'), ('description', 'Description')]
        for attrName, elementName in attrNames:
            attrValue = getattr(self, attrName)
            if attrValue is not None:
                ElementTree.SubElement(objectElement, elementName).text = attrValue
        for attribute in self._attributes:
            attribute._toXMLElement(objectElement)
        return objectElement
    
    
    def _includeInScript(self, atTopLevel = False):
        return True
    
    
    def _needsScriptRef(self):
        if len(self._attributes) > 0 or len(self.stimuli) > 0:
            return True
        
        for display in self.network.displays:
            if len(display.visiblesForObject(self)) > 0:
                return True
        
        # No other code will need to refer to this object.
        return False
    
    
    def _createScriptRef(self, scriptRefs):
        # TODO: check if abbreviation or name is unique and create variable name from that?
        className = self.__class__.__name__
        if className in scriptRefs:
            instanceCount = scriptRefs[className]
        else:
            instanceCount = 0
        scriptRefs[className] = instanceCount + 1
        scriptRefs[self.networkId] = className.lower() + str(instanceCount + 1)
        return scriptRefs[self.networkId]
    
    
    def _creationScriptCommand(self, scriptRefs):
        return 'network.create' + self.__class__.__name__
    
    
    def _creationScriptParams(self, scriptRefs):
        args = []
        keywords = {}
        if self.name is not None:
            keywords['name'] = '\'' + self.name.replace('\\', '\\\\').replace('\'', '\\\'') + '\''
        if self.abbreviation is not None:
            keywords['abbreviation'] = '\'' + self.abbreviation.replace('\\', '\\\\').replace('\'', '\\\'') + '\''
        if self.description is not None:
            keywords['description'] = '\'' + self.description.replace('\\', '\\\\').replace('\'', '\\\'') + '\''
        return (args, keywords)
    
    
    def _creationScriptChildren(self):
        return list(self._attributes)
    
    
    def _toScriptFile(self, scriptFile, scriptRefs):
        if self._includeInScript():
            if self._needsScriptRef():
                scriptFile.write(self._createScriptRef(scriptRefs) + ' = ')
            
            scriptFile.write(self._creationScriptCommand(scriptRefs) + '(')
            args, keywords = self._creationScriptParams(scriptRefs)
            for keyword, value in keywords.iteritems():
                args.append(keyword + ' = ' + value)
            scriptFile.write(', '.join(args) + ')\n')
            
            prevPos = scriptFile.tell()
            
            for child in self._creationScriptChildren():
                child._toScriptFile(scriptFile, scriptRefs)
    
    
    @classmethod
    def displayName(cls):
        """
        Return a user readable name string for this type of object.
        """
        
        return gettext(cls.__name__)
    
    
    @classmethod
    def image(cls):
        """
        Return an image (a wx.Image) representing a generic instance of this type of object.
        
        If no image is available then None will be returned.
        """
        
        image = wx.GetApp().loadImage(cls.__name__ + ".png")
        if image != None and not image.IsOk():
            image = None
        return image
    
    
    def __hash__(self):
        return self.networkId
    
    
    def __setattr__(self, name, value):
        """
        Send out a message whenever one of this object's values changes.  This is needed, for example, to allow the GUI to update when an object is modified via the console or a script.
        """
        
        hasPreviousValue = hasattr(self, name)
        if hasPreviousValue:
            previousValue = getattr(self, name)
        
        object.__setattr__(self, name, value)
        
        if not hasPreviousValue or getattr(self, name) != previousValue:
            dispatcher.send(('set', name), self)
    
    
    def defaultName(self):
        """
        Return a programmatically generated name string for this object.
        """
        
        return None
    
    
    def connections(self, recurse = True):
        """
        Return a list of the objects that connect to this object.
        """
        
        return list(self.stimuli)
    
    
    def inputs(self, recurse = True):
        """
        Return a list of objects that send information into this object.
        """
        
        return list(self.stimuli)
    
    
    def outputs(self, recurse = True):
        """ Return a list of objects that receive information from this object.
        """
        
        return []
    
    
    def stimulate(self, modality = None, *args, **keywordArgs):
        """
        Add a :class:`stimulus <Network.Stimulus.Stimulus>` to this object with the given :class:`modality <Library.Modality.Modality>`.
        
        >>> neuron1.stimulate(library.modality('light')) 
        
        Returns the stimulus object that is created.
        """
        
        from Stimulus import Stimulus
        from Library.Modality import Modality
        
        if modality != None and not isinstance(modality, Modality):
            raise TypeError, 'The modality argument passed to stimulate() must be a value obtained from the library or None.'
        
        stimulus = Stimulus(self.network, target = self, modality = modality, *args, **keywordArgs)
        self.stimuli.append(stimulus)
        self.network.addObject(stimulus)
        return stimulus
        
    
    def shortestPathTo(self, otherObject):
        """
        Return one of the shortest paths through the :class:`network <Network.Network.Network>` from this object to the other object.
        
        The other object must be an object in the same network.
        
        Returns a list of objects in the path from this object to the other.  If there is no path from this object to the other then an empty list will be returned. 
        """
        
        if not isinstance(otherObject, Object) or otherObject.network != self.network:
            raise ValueError, 'The object passed to shortestPathTo() must be an object from the same network.'
        
        startNodeIds = []
        if self.networkId in self.network.graph:
            startNodeIds.append(self.networkId)
        else:
            for startId, endId, edgeObject in self.network.graph.edges():
                if edgeObject == self:
                    startNodeIds.append(endId)
        endNodeIds = []
        if otherObject.networkId in self.network.graph:
            endNodeIds.append(otherObject.networkId)
        else:
            for startId, endId, edgeObject in self.network.graph.edges():
                if edgeObject == otherObject:
                    endNodeIds.append(startId)
        path = []
        shortestPathLen = 1000000
        for startNodeId in startNodeIds:
            for endNodeId in endNodeIds:
                nodeList = shortest_path(self.network.graph, startNodeId, endNodeId)
                if nodeList and len(nodeList) < shortestPathLen:
                    path = []
                    for nodeID in nodeList:
                        pathObject = self.network.objectWithId(nodeID)
                        if pathObject != self:
                            path.append(pathObject)
                    shortestPathLen = len(nodeList)
        return path
    
    
    def addAttribute(self, name = None, type = None, value = None):
        """
        Add a user-defined attribute to this object.
        
        >>> neuron1.addAttribute('Confirmed', Attribute.BOOLEAN_VALUE, True)
        
        It is allowable to have multiple attributes on the same object which have the same name.  The type parameter should be one of the :class:`Attribute.*_TYPE <Network.Attribute.Attribute>` values.
        
        Returns the attribute object that is created.
        """
        
        if name is None or type is None or value is None:
            raise ValueError, gettext('The name, type and value parameters must be specified when adding an attribute.')
        if not isinstance(name, str):
            raise TypeError, 'The name parameter passed to addAttribute() must be a string.'
        if type not in Attribute.TYPES:
            raise TypeError, 'The type parameter passed to addAttribute() must be one of the Attribute.*_TYPE values.'
        # TODO: validate value based on the type?
        
        attribute = Attribute(self, name, type, value)
        self._attributes.append(attribute)
        dispatcher.send(('set', 'attributes'), self)
        return attribute
    
    
    def getAttribute(self, name):
        """
        Return the first user-defined attribute of this object with the given name or None if there is no matching attribute.
        
        >>> if neuron1.getAttribute('Confirmed').value() == True:
        ...     display.setVisibleColor(neuron1, (1, 0, 0))
        """
        
        for attribute in self._attributes:
            if attribute.name() == name:
                return attribute
        return None
    
    
    def getAttributes(self, name = None):
        """
        Return a list of all user-defined :class:`attributes <Network.Attribute.Attribute>` of this object or only those with the given name.
        
        >>> comments = [comment.value() for comment in region1.getAttributes('Comment')]
        
        If there are no attributes then an empty list will be returned.
        """
        
        attributes = []
        for attribute in self._attributes:
            if name == None or attribute.name() == name:
                attributes += [attribute]
        return attributes

    def _printConnections(self):
        print self.name or self.defaultName() or '<anonymous %s>' % self.__class__.displayName()
        print '\tConnections: ' + ', '.join([connection.name or connection.defaultName() or '<anonymous %s>' % lower(connection.__class__.displayName()) for connection in self.connections()])
        print '\tInputs: ' + ', '.join([input.name or input.defaultName() or '<anonymous %s>' % lower(input.__class__.displayName()) for input in self.inputs()])
        print '\tOutputs: ' + ', '.join([output.name or output.defaultName() or '<anonymous %s>' % lower(output.__class__.displayName()) for output in self.outputs()])
        