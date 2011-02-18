#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

import neuroptikon
from pydispatch import dispatcher
try:
    import xml.etree.cElementTree as ElementTree
except ImportError:
    import xml.etree.ElementTree as ElementTree
from attribute import Attribute

    
class Object(object):
    
    def __init__(self, network, name = None, abbreviation = None, description = None):
        """
        The Object class is the base-class for every object in a :class:`network <Network.Network.Network>`.
        
        Any number of user-defined attributes can be added to an object.  The connectivity of objects can also be investigated.
        """
        
        self.network = network
        self.networkId = self.network._generateUniqueId()
        
        self.name = name
        self.abbreviation = abbreviation
        self.description = description
        self._attributes = []
    
    
    @classmethod
    def _fromXMLElement(cls, network, xmlElement):
        networkObject = super(Object, cls).__new__(cls)
        networkObject.network = network
        networkObject.networkId = int(xmlElement.get('id'))
        
        networkObject.name = xmlElement.findtext('Name')
        if networkObject.name is None:
            networkObject.name = xmlElement.findtext('name')
        networkObject.abbreviation = xmlElement.findtext('Abbreviation')
        if networkObject.abbreviation is None:
            networkObject.abbreviation = xmlElement.findtext('abbreviation')
        networkObject.description = xmlElement.findtext('Description')
        if networkObject.description is None:
            networkObject.description = xmlElement.findtext('description')
        
        networkObject._attributes = []
        for element in xmlElement.findall('Attribute'):
            attribute = Attribute._fromXMLElement(networkObject, element)
            if attribute is not None:
                networkObject._attributes.append(attribute)
        
        # TODO: handle links
        # TODO: handle notes
        return networkObject
    
    
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
    
    
    def _includeInScript(self, atTopLevel = False): # pylint: disable-msg=W0613
        return True
    
    
    def _needsScriptRef(self):
        if len(self._attributes) > 0:
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
    
    
    def _creationScriptMethod(self, scriptRefs):   # pylint: disable-msg=W0613
        return 'network.create' + self.__class__.__name__
    
    
    def _creationScriptParams(self, scriptRefs):    # pylint: disable-msg=W0613
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
    
    
    def _creationScriptCommand(self, scriptRefs):
        command = self._creationScriptMethod(scriptRefs) + '('
        args, keywords = self._creationScriptParams(scriptRefs)
        for keyword, value in keywords.iteritems():
            args.append(keyword + ' = ' + value)
        command += ', '.join(args) + ')'
        return command
    
    
    def _toScriptFile(self, scriptFile, scriptRefs):
        if self._includeInScript():
            if self._needsScriptRef():
                scriptFile.write(self._createScriptRef(scriptRefs) + ' = ')
            
            scriptFile.write(self._creationScriptCommand(scriptRefs) + '\n')
            
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
        
        image = neuroptikon.loadImage(cls.__name__ + ".png")
        if image != None and not image.IsOk():
            image = None
        return image
    
    
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
        Return a list of the objects that connect to this object and optionally any of the children of this object.
        """
        
        connections = []
        if recurse:
            for childObject in self.childObjects():
                connections += childObject.connections()
            while self in connections:
                connections.remove(self)
        else:
            connections += self.childObjects()
        return connections
    
    
    def inputs(self, recurse = True):
        """
        Return a list of objects that send information into this object.
        """
        
        inputs = []
        if recurse:
            for childObject in self.childObjects():
                inputs += childObject.inputs()
        else:
            inputs += self.childObjects()
        return inputs
    
    
    def outputs(self, recurse = True):
        """
        Return a list of objects that receive information from this object.
        """
        
        outputs = []
        if recurse:
            for childObject in self.childObjects():
                outputs += childObject.outputs()
        else:
            outputs += self.childObjects()
        return outputs
        
        
    def _printConnections(self):
        print self.name or self.defaultName() or '<anonymous %s>' % self.__class__.displayName()
        print '\tConnections: ' + ', '.join([connection.name or connection.defaultName() or '<anonymous %s>' % connection.__class__.displayName().lower() for connection in self.connections()])
        print '\tInputs: ' + ', '.join([input.name or input.defaultName() or '<anonymous %s>' % input.__class__.displayName().lower() for input in self.inputs()])  # pylint: disable-msg=W0622
        print '\tOutputs: ' + ', '.join([output.name or output.defaultName() or '<anonymous %s>' % output.__class__.displayName().lower() for output in self.outputs()])
    
    
    def rootObject(self):
        """
        Return the object that is the root of this object's tree of components.
        """
        
        parent = self.parentObject()
        if parent:
            return parent.rootObject()
        else:
            return self
    
    
    def ancestors(self):
        """
        Return all objects connecting this object to the root of the component tree, including the root.
        """
        
        parent = self.parentObject()
        if parent:
            return [parent] + parent.ancestors()
        else:
            return []
    
    
    def parentObject(self):
        """
        Return the object that is directly above this object in the component tree.
        """
        
        return None
    
    
    def childObjects(self):
        """
        Return the objects directly below this object in the component tree.
        """
        
        return []
    
    
    def descendants(self):
        """
        Return all objects below this object in the component tree.
        """
        
        descendants = list(self.childObjects())
        for child in list(descendants):
            descendants += child.descendants()
        return descendants
    
    
    def dependentObjects(self):
        """
        Return the list of other objects in the network that could not exist without this object.
        """
        
        return []
    
    
    def disconnectFromNetwork(self):
        """
        Perform any clean up, e.g. removing references in other objects, before being removed from the network.
        """
        
        # TODO: This may not be the best way to handle this.  Another option would be for all objects to hold weak refs to other objects in the network and do their own clean up when the objects go away.
        pass
    
    
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
    
    
    def removeAttribute(self, attribute):
        """
        Remove the given attribute from the object.
        """
        
        if not isinstance(attribute, Attribute) or not attribute in self._attributes:
            raise ValueError, 'The attribute passed to removeAttribute() must be an existing attribute of the object.'
        
        self._attributes.remove(attribute)
        dispatcher.send(('set', 'attributes'), self)
    
    
    @classmethod
    def _defaultVisualizationParams(cls):
        """
        Return a dictionary containing the default visualization parameters for this class of object.
        """
        
        # TODO: replace this with a display rule.
        params = {}
        
        params['opacity'] = 1.0
        params['weight'] = 1.0
        params['label'] = None
        params['texture'] = None
        params['shape'] = 'Box'
       
        return params
    
    
    def defaultVisualizationParams(self):
        """
        Return a dictionary containing the default visualization parameters for this object.
        """
        
        return self.__class__._defaultVisualizationParams()
        