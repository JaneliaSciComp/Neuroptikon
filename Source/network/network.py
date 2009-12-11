from networkx import XDiGraph
import os.path, sys
from pydispatch import dispatcher
import xml.etree.ElementTree as ElementTree
from region import Region
from pathway import Pathway
from neuron import Neuron
from neurite import Neurite
from arborization import Arborization
from synapse import Synapse
from gap_junction import GapJunction
from stimulus import Stimulus
from muscle import Muscle
from innervation import Innervation
from attribute import Attribute

try:
    import pydot    # pylint: disable-msg=F0401,W0611
except ImportError:
    pydot = None


class Network:
    
    def __init__(self):
        """
        Networks are containers for all :class:`objects <Network.Object.Object>` that exist in a neural circuit. 
        """
        
        self.graph = XDiGraph(multiedges = True, )
        self.objects = []
        self.idDict = {}   # TODO: weak ref dict?
        self.displays = []
        self._nextUniqueId = -1
        self._savePath = None
        self._attributes = []
        self._displaysAreSynchronized = True
        
        self._loadingFromXML = False
        self._modified = False
    
    
    @classmethod
    def _fromXMLElement(cls, xmlElement):
        network = cls()
        
        network._loadingFromXML = True
        
        # Load the classes in such an order that any referenced objects are guaranteed to have already been created.
        for className in ['Region', 'Pathway', 'Neuron', 'Muscle', 'Arborization', 'Innervation', 'GapJunction', 'Synapse', 'Stimulus']:
            elementModule = getattr(sys.modules['Network'], className)
            elementClass = getattr(elementModule, className)
            for element in xmlElement.findall(className):
                networkObject = elementClass._fromXMLElement(network, element)
                if networkObject is not None:
                    network.addObject(networkObject)
        
        for element in xmlElement.findall('Attribute'):
            attribute = Attribute._fromXMLElement(network, element)
            if attribute is not None:
                network._attributes.append(attribute)
        
        network._loadingFromXML = False
        
        return network
    
    
    def _toXMLElement(self, parentElement):
        networkElement = ElementTree.SubElement(parentElement, 'Network')
        for networkObject in self.objects:
            # Nested regions are handled by their parents and neurites are handled by their neurons.
            if not (isinstance(networkObject, Region) and networkObject.parentRegion is not None) and not isinstance(networkObject, Neurite):
                objectElement = networkObject._toXMLElement(networkElement)
                if objectElement is None:
                    pass    # TODO: are there any cases where this is NOT an error?
        for attribute in self._attributes:
            attribute._toXMLElement(networkElement)
        return networkElement
    
    
    def _toScriptFile(self, scriptFile, scriptRefs):
        if len(self._attributes) > 0:
            scriptFile.write(gettext('# Create the network') + '\n\n')
            for attribute in self._attributes:
                attribute._toScriptFile(scriptFile, scriptRefs)
        
        # Add each network object to the script in an order that guarantees dependent objects will already have been added.
        # Neurites will be added by their neurons, sub-regions by their root region.
        for objectClass in (Region, Pathway, Muscle, Neuron, Arborization, GapJunction, Innervation, Synapse, Stimulus):
            objects = self.objectsOfClass(objectClass)
            if len(objects) > 0:
                scriptFile.write('\n# ' + gettext('Create each %s') % (objectClass.displayName().lower()) + '\n\n')
                for networkObject in objects:
                    if networkObject._includeInScript(atTopLevel = True):
                        networkObject._toScriptFile(scriptFile, scriptRefs)
   
   
    def setSavePath(self, path):
        if path != self._savePath:
            self._savePath = path
            dispatcher.send(('set', 'savePath'), self)
    
    
    def savePath(self):
        return self._savePath
    
    
    def name(self):
        if self._savePath is None:
            return gettext('Untitled Network')
        else:
            return os.path.splitext(os.path.basename(self._savePath))[0]
    
    def _generateUniqueId(self):
        self._nextUniqueId += 1
        return self._nextUniqueId
    
    
    def findObject(self, objectClass, name = None, default = False):
        """
        Return the first object of the given class with the given name.
        
        >>> neuron = network.findObject(Neuron, 'AVAL')
        
        Returns an :class:`Object <Network.Object.Object>` or None if there are no matching objects.
        
        If default is True then each object's :meth:`defaultName() <Network.Object.Object.defaultName>` will be queried instead of its name.
        """
        
        if name is not None:
            for networkObject in self.objects:
                if isinstance(networkObject, objectClass) and ((not default and networkObject.name == name) or (default and networkObject.defaultName() == name)):
                    return networkObject
        return None
    
    
    def createRegion(self, addSubTerms = False, *args, **keywordArgs):
        """
        Create a new region optionally associated with an ontology term.
        
        >>> region = network.createRegion(name = 'Glomerulus 2')
        
        To associate the region with an ontology term pass in a term from an ontology in the library:
        
        >>> flyBrainOnt = library.ontology('flybrain')
        >>> ellipsoidBody = network.createRegion(ontologyTerm = flyBrainOnt.findTerm(name = 'Ellipsoid body'))
        
        If addSubTerms is true then sub-regions will be created for all sub-terms in the ontology.
         
        Returns the :class:`region <Network.Region.Region>` that is created.
        """
        
        region = Region(self, *args, **keywordArgs)
        self.addObject(region)
        
        if region.ontologyTerm is not None and addSubTerms:
            for term in region.ontologyTerm.parts:
                self.createRegion(ontologyTerm = term, parentRegion = region, addSubTerms = True)
        
        return region
    
    
    def findRegion(self, name = None):
        """
        Find the first region with the given name.
        
        >>> region = network.findRegion('Ellipsoid body')
         
        Returns a :class:`region <Network.Region.Region>` or None if there are no regions with the name.
        """
        
        return self.findObject(Region, name)
    
    
    def regions(self):
        """
        Return a list of all :class:`regions <Network.Region.Region>` in the network.
        
        >>> for region in network.regions():
        ...     display.setVisibleColor(region, (1.0, 0.0, 0.0))
        
        An empty list will be returned if there are no regions in the network.
        """
         
        return self.objectsOfClass(Region)
    
    
    def pathways(self):
        """
        Return a list of all :class:`pathways <Network.Pathway.Pathway>` in the network.
        
        >>> for pathway in network.pathways():
        ...     display.setVisibleColor(pathway, (1.0, 0.0, 0.0))
        
        An empty list will be returned if there are no pathways in the network.
        """
         
        return self.objectsOfClass(Pathway)
    
    
    def createNeuron(self, *args, **keywordArgs):
        """
        Create a new neuron.
        
        >>> neuron = network.createNeuron(name = 'AVAL')
         
        Returns the :class:`neuron <Network.Neuron.Neuron>` that is created.
        """
        
        neuron = Neuron(self, *args, **keywordArgs)
        self.addObject(neuron)
        return neuron
    
    
    def findNeuron(self, name = None):
        """
        Find the first neuron with the given name.
        
        >>> neuron = network.findNeuron('AVAL')
         
        Returns a :class:`neuron <Network.Neuron.Neuron>` or None if there are no neurons with the name.
        """
        
        return self.findObject(Neuron, name)
    
    
    def neurons(self):
        """
        Return a list of all :class:`neurons <Network.Neuron.Neuron>` in the network.
        
        >>> for neuron in network.neurons():
        ...     neuron.setHasFunction(Neuron.Function.SENSORY, False)
        
        An empty list will be returned if there are no neurons in the network.
        """
         
        return self.objectsOfClass(Neuron)
    
    
    def neurites(self):
        """
        Return a list of all :class:`neurites <Network.Neurite.Neurite>` in the network.
        
        >>> for neurite in network.neurites():
        ...     neurite.setPathway(None)
        
        An empty list will be returned if there are no neurites in the network.
        """
         
        return self.objectsOfClass(Neurite)
    
    
    def arborizations(self):
        """
        Return a list of all :class:`arborizations <Network.Arborization.Arborization>` in the network.
        
        >>> for arborization in network.arborizations():
        ...     display.setVisibleShape(arborization, shapes['Cone'])
        
        An empty list will be returned if there are no arborizations in the network.
        """
         
        return self.objectsOfClass(Arborization)
    
    
    def gapJunctions(self):
        """
        Return a list of all :class:`gap junctions <Network.GapJunction.GapJunction>` in the network.
        
        >>> for gapJunction in network.gapJunctions():
        ...     display.setVisibleColor(gapJunction, (0, 0, 0))
        
        An empty list will be returned if there are no gap junctions in the network.
        """
         
        return self.objectsOfClass(GapJunction)
    
    
    def innervations(self):
        """
        Return a list of all :class:`innervations <Network.Innervation.Innervation>` in the network.
        
        >>> for innervation in network.innervations():
        ...     display.setVisibleWeight(innervation, 2.0)
        
        An empty list will be returned if there are no innervations in the network.
        """
         
        return self.objectsOfClass(Innervation)
    
    
    def synapses(self):
        """
        Return a list of all :class:`chemical synapses <Network.Synapse.Synapse>` in the network.
        
        >>> for synapse in network.synapses():
        ...     synapse.activation = None
        
        An empty list will be returned if there are no chemical synapses in the network.
        """
         
        return self.objectsOfClass(Synapse)
    
    
    def createStimulus(self, *args, **keywordArgs):
        """
        Create a new stimulus.  DEPRECATED: Call :meth:`stimulate() <Network.Object.Object.stimulate>` on the desired target object instead.
        
        >>> stimulus = network.createStimulus(target = neuron1, modality = library.modality('light'))
         
        Returns the :class:`stimulus <Network.Stimulus.Stimulus>` that is created.
        """
        
        target = keywordArgs['target']
        del keywordArgs['target']
        
        return target.stimulate(*args, **keywordArgs)
    
    
    def findStimulus(self, name = None):
        """
        Find the first stimulus with the given name.
        
        >>> stimulus = network.findStimulus('Light')
         
        Returns a :class:`stimulus <Network.Stimulus.Stimulus>` or None if there are no stimuli with the name.
        """
        
        return self.findObject(Stimulus, name)
    
    
    def stimuli(self):
        """
        Return a list of all :class:`stimuli <Network.Stimulus.Stimulus>` in the network.
        
        >>> for stimulus in network.stimuli():
        ...     if stimulus.modality == library.modality('light'):
        ...         display.setVisibleColor(stimulus, (1, 1, 1))
        
        An empty list will be returned if there are no stimuli in the network.
        """
         
        return self.objectsOfClass(Stimulus)
    
    
    def createMuscle(self, *args, **keywordArgs):
        """
        Create a new muscle.
        
        >>> muscle = network.createMuscle(name = 'M1')
         
        Returns the :class:`muscle <Network.Muscle.Muscle>` that is created.
        """
        
        muscle = Muscle(self, *args, **keywordArgs)
        self.addObject(muscle)
        return muscle
    
    
    def findMuscle(self, name = None):
        """
        Find the first muscle with the given name.
        
        >>> muscle = network.findMuscle('M1')
         
        Returns a :class:`muscle <Network.Muscle.Muscle>` or None if there are no muscles with the name.
        """
        
        return self.findObject(Muscle, name)
    
    
    def muscles(self):
        """
        Return a list of all :class:`muscles <Network.Muscle.Muscle>` in the network.
        
        >>> for muscle in network.muscles():
        ...     display.setVisibleOpacity(muscle, 0.5)
        
        An empty list will be returned if there are no muscles in the network.
        """
         
        return self.objectsOfClass(Muscle)
    
    
    def _objectChanged(self):
        if not self._loadingFromXML and not self._modified:
            self._modified = True
            dispatcher.send(('set', 'modified'), self)
    
    
    def setModified(self, modified):
        """
        Set whether or not this network is dirty and needs to be saved.
        """
        
        if self._modified != modified:
            self._modified = modified
            dispatcher.send(('set', 'modified'), self)
    
    
    def isModified(self):
        """
        Return whether the network has been modified and needs to be saved.
        """
        
        return self._modified

    
    def addObject(self, objectToAdd):
        if objectToAdd.networkId in self.idDict:
            raise ValueError, gettext('All objects in a network must have unique identifiers.')
        
        self.objects.append(objectToAdd)
        self.idDict[objectToAdd.networkId] = objectToAdd
        
        if objectToAdd.networkId > self._nextUniqueId:
            self._nextUniqueId = objectToAdd.networkId
        
        # Update the NetworkX graph representation of the network.
        if isinstance(objectToAdd, Arborization):
            if objectToAdd.sendsOutput == None or objectToAdd.sendsOutput:
                self.graph.add_edge(objectToAdd.neurite.neuron().networkId, objectToAdd.region.networkId, objectToAdd)
            if objectToAdd.receivesInput == None or objectToAdd.receivesInput:
                self.graph.add_edge(objectToAdd.region.networkId, objectToAdd.neurite.neuron().networkId, objectToAdd)
        elif isinstance(objectToAdd, Synapse):
            for postSynapticNeurite in objectToAdd.postSynapticNeurites:
                self.graph.add_edge(objectToAdd.preSynapticNeurite.neuron().networkId, postSynapticNeurite.neuron().networkId, objectToAdd)
        elif isinstance(objectToAdd, GapJunction):
            neurite1, neurite2 = objectToAdd.neurites()
            self.graph.add_edge(neurite1.neuron().networkId, neurite2.neuron().networkId, objectToAdd)
            self.graph.add_edge(neurite2.neuron().networkId, neurite1.neuron().networkId, objectToAdd)
        elif isinstance(objectToAdd, Pathway):
            if objectToAdd.region1Projects == None or objectToAdd.region1Projects:
                self.graph.add_edge(objectToAdd.region1.networkId, objectToAdd.region2.networkId, objectToAdd)
            if objectToAdd.region2Projects == None or objectToAdd.region2Projects:
                self.graph.add_edge(objectToAdd.region2.networkId, objectToAdd.region1.networkId, objectToAdd)
        elif isinstance(objectToAdd, Innervation):
            self.graph.add_edge(objectToAdd.neurite.neuron().networkId, objectToAdd.muscle.networkId, objectToAdd)
        elif isinstance(objectToAdd, Stimulus):
            self.graph.add_node(objectToAdd.networkId)
            self.graph.add_edge(objectToAdd.networkId, objectToAdd.target.networkId, objectToAdd)
        elif isinstance(objectToAdd, Neurite):
            pass    # TODO: are neurites nodes or edges or either?
        elif isinstance(objectToAdd, Region) or isinstance(objectToAdd, Neuron) or isinstance(objectToAdd, Muscle):
            self.graph.add_node(objectToAdd.networkId)
        
        # Watch for any changes to the object so we can update our dirty state.
        dispatcher.connect(self._objectChanged, dispatcher.Any, objectToAdd)
        
        # Let anyone who cares know that the network was changed.
        dispatcher.send('addition', self, affectedObjects = [objectToAdd])
    
    
    def objectWithId(self, objectId):
        if (isinstance(objectId, str) or isinstance(objectId, unicode)) and objectId.isdigit():
            objectId = int(objectId)
        
        return self.idDict[objectId] if objectId in self.idDict else None
    
    
    def objectsOfClass(self, objectClass):
        objects = []
        for networkObject in self.objects:
            if isinstance(networkObject, objectClass):
                objects.append(networkObject)
        return objects
    
    
    def removeObject(self, networkObject):
        """
        Remove the indicated object and any dependent objects from the network and any displays.
        
        >>> network.removeObject(network.findNeuron('AVAL'))
        """
        
        if networkObject in self.objects:
            # Determine all of the objects that will need to be removed
            objectsToRemove = set([networkObject])
            objectsToInspect = [networkObject]
            while any(objectsToInspect):
                objectToInspect = objectsToInspect.pop(0)
                dependentObjects = set(objectToInspect.dependentObjects())
                objectsToInspect += list(dependentObjects.difference(objectsToRemove))
                objectsToRemove = objectsToRemove.union(dependentObjects)
            
            # Remove all of the objects.
            for objectToRemove in objectsToRemove:
                objectToRemove.disconnectFromNetwork()
                self.objects.remove(objectToRemove)
                del self.idDict[objectToRemove.networkId]
            
                # Keep the NetworkX graph in sync.
                if objectToRemove.networkId in self.graph:
                    self.graph.delete_node(objectToRemove.networkId)
                else:
                    for edge in self.graph.edges_iter():
                        if edge[2] == objectToRemove:
                            self.graph.delete_edge(edge[0], edge[1], edge[2])
                            break
            
            # Let anyone who cares know that the network was changed.
            dispatcher.send('deletion', self, affectedObjects = objectsToRemove)
    
    
    def removeAllObjects(self):
        """
        Remove all objects from the network and any displays.
        """
        
        for networkObject in self.objects:
            networkObject.network = None
        self.objects = []
        self.idDict = {}
        self.graph.clear()
    
    
    def addDisplay(self, display):
        self.displays.append(display)
        dispatcher.connect(self._synchronizeDisplays, ('set', 'selection'), display)
    
    
    def removeDisplay(self, display):
        self.displays.remove(display)
        dispatcher.disconnect(self._synchronizeDisplays, ('set', 'selection'), display)
    
    
    def setSynchronizeDisplays(self, synchronize):
        if synchronize != self._displaysAreSynchronized:
            self._displaysAreSynchronized = synchronize
            
            if synchronize and any(self.displays):
                self._synchronizeDisplays(None, self.displays[0])
    
    
    def _synchronizeDisplays(self, sender):
        if self._displaysAreSynchronized:
            selection = sender.selectedObjects()
            for display in self.displays:
                if display != sender:
                    display.selectObjects(selection)
    
    
    def addAttribute(self, name = None, type = None, value = None):
        """
        Add a user-defined attribute to this network.
        
        >>> network.addAttribute('Preliminary', Attribute.BOOLEAN_TYPE, True)
        
        The type parameter should be one of the :class:`Attribute.*_TYPE <Network.Attribute.Attribute>` values.
        
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
        Return the first user-defined :class:`attribute <Network.Attribute.Attribute>` of this network with the given name or None if there is no matching attribute.
        
        >>> creationDate = network.getAttribute('Creation Date').value()
        """
        
        for attribute in self._attributes:
            if attribute.name() == name:
                return attribute
        return None
    
    
    def getAttributes(self, name = None):
        """
        Return a list of all user-defined :class:`attributes <Network.Attribute.Attribute>` of this network or only those with the given name.
        
        >>> reviewers = [reviewer.value() for reviewer in network.getAttributes('Reviewed By')]
        
        If there are no attributes then an empty list will be returned.
        """
        
        attributes = []
        for attribute in self._attributes:
            if name == None or attribute.name() == name:
                attributes += [attribute]
        return attributes
    
    
    def removeAttribute(self, attribute):
        """
        Remove the given attribute from the network.
        """
        
        if not isinstance(attribute, Attribute) or not attribute in self._attributes:
            raise ValueError, 'The attribute passed to removeAttribute() must be an existing attribute of the network.'
        
        self._attributes.remove(attribute)
        dispatcher.send(('set', 'attributes'), self)
        