#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

from networkx import DiGraph, dijkstra_path
import os.path, sys
from pydispatch import dispatcher
try:
    import xml.etree.cElementTree as ElementTree
except ImportError:
    import xml.etree.ElementTree as ElementTree
import inspect, marshal, types

from object import Object
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
    import pydot    # pylint: disable=F0401,W0611
except ImportError:
    pydot = None


class Network:
    
    def __init__(self):
        """
        Networks are containers for all :class:`objects <Network.Object.Object>` that exist in a neural circuit. 
        """
        
        self.graph = DiGraph()
        self.objects = []
        self.idDict = {}   # TODO: weak ref dict?
        self.displays = []
        self._nextUniqueId = -1
        self._savePath = None
        self._attributes = []
        self._displaysAreSynchronized = True
        self._weightingFunction = None
        
        self._bulkLoading = False
        self._bulkAddObjects = []
        
        self._modified = False
    
    
    @classmethod
    def _fromXMLElement(cls, xmlElement):
        network = cls()
        
        network.setBulkLoading(True)
        
        # Load the classes in such an order that any referenced objects are guaranteed to have already been created.
        for moduleName, className in [('region', 'Region'), ('pathway', 'Pathway'), ('neuron', 'Neuron'), ('muscle', 'Muscle'), ('arborization', 'Arborization'), ('innervation', 'Innervation'), ('gap_junction', 'GapJunction'), ('synapse', 'Synapse'), ('stimulus', 'Stimulus')]:
            elementModule = getattr(sys.modules['network'], moduleName)
            elementClass = getattr(elementModule, className)
            for element in xmlElement.findall(className):
                networkObject = elementClass._fromXMLElement(network, element)
                if networkObject is not None:
                    network.addObject(networkObject)
        
        weightingFunctionElement = xmlElement.find('WeightingFunction')
        if weightingFunctionElement is not None:
            funcType = weightingFunctionElement.get('type')
            funcName = weightingFunctionElement.get('name')
            if funcType == 'source':
                exec(weightingFunctionElement.text)
                network._weightingFunction = eval(funcName)
            elif funcType == 'marshal':
                code = marshal.loads(eval(weightingFunctionElement.text))
                network._weightingFunction = types.FunctionType(code, globals(), funcName or 'weightingFunction')
            else:
                raise ValueError, gettext('Unknown weighting function type: %s') % (funcType)
        
        for element in xmlElement.findall('Attribute'):
            attribute = Attribute._fromXMLElement(network, element)
            if attribute is not None:
                network._attributes.append(attribute)
        
        network.setBulkLoading(False)
        
        return network
    
    
    def _toXMLElement(self, parentElement):
        networkElement = ElementTree.SubElement(parentElement, 'Network')
        
        for networkObject in self.objects:
            # Nested regions are handled by their parents and neurites are handled by their neurons.
            if not (isinstance(networkObject, Region) and networkObject.parentRegion is not None) and not isinstance(networkObject, Neurite):
                objectElement = networkObject._toXMLElement(networkElement)
                if objectElement is None:
                    pass    # TODO: are there any cases where this is NOT an error?
        
        if self._weightingFunction:
            weightingFunctionElement = ElementTree.SubElement(networkElement, 'WeightingFunction')
            weightingFunctionElement.set('name', self._weightingFunction.func_name)
            # First try to get the function source and if that fails then marshal the byte code.
            try:
                source = inspect.getsource(self._weightingFunction)
                weightingFunctionElement.text = source 
                weightingFunctionElement.set('type', 'source')
            except IOError:
                weightingFunctionElement.text = repr(marshal.dumps(self._weightingFunction.func_code))
                weightingFunctionElement.set('type', 'marshal')
            
        for attribute in self._attributes:
            attribute._toXMLElement(networkElement)
        
        return networkElement
    
    
    def _toScriptFile(self, scriptFile, scriptRefs):
        if len(self._attributes) > 0:
            scriptFile.write(gettext('# Create the network') + '\n\n')
            for attribute in self._attributes:
                attribute._toScriptFile(scriptFile, scriptRefs)
        
        if self._weightingFunction:
            # First try to get the function source and if that fails then marshal the byte code.
            scriptFile.write(gettext('# Add the weighting function') + '\n\n')
            funcName = self._weightingFunction.func_name
            try:
                source = inspect.getsource(self._weightingFunction)
                scriptFile.write(source + '\n\nnetwork.setWeightingFunction(' + funcName + ')\n\n')
            except IOError:
                scriptFile.write('import marshal, types\n')
                scriptFile.write('code = marshal.loads(' + repr(marshal.dumps(self._weightingFunction.func_code)) + ')\n')
                scriptFile.write('network.setWeightingFunction(types.FunctionType(code, globals(), \'' + funcName + '\'))\n\n')
        
        # Add each network object to the script in an order that guarantees dependent objects will already have been added.
        # Neurites will be added by their neurons, sub-regions by their root region.
        for objectClass in (Region, Pathway, Muscle, Neuron, Arborization, GapJunction, Innervation, Synapse, Stimulus):
            objects = self.objectsOfClass(objectClass)
            if len(objects) > 0:
                scriptFile.write('\n# ' + gettext('Create each %s') % (objectClass.displayName().lower()) + '\n\n')
                for networkObject in objects:
                    if networkObject._includeInScript(atTopLevel = True):
                        networkObject._toScriptFile(scriptFile, scriptRefs)
   
   
    def setBulkLoading(self, bulkLoading):
        """
        Indicate whether or not a large quantity of objects are being added to the network.
        
        >>> network.setBulkLoading(True)
        >>> # ... add lots of objects ...
        >>> network.setBulkLoading(False)
        
        If bulk loading is enabled then various actions are delayed to make loading faster.
        """
        
        if bulkLoading != self._bulkLoading:
            self._bulkLoading = bulkLoading
            if self._bulkLoading == False:
                self._updateGraph()
                if any(self._bulkAddObjects):
                    dispatcher.send('addition', self, affectedObjects = self._bulkAddObjects)
                    self._bulkAddObjects = []
            dispatcher.send(('set', 'bulkLoading'), self)
            
   
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

    def findObjects(self, objectClass, name = None, default = False):
        """
        Return all objects of the given class with the given name.
        
        >>> neuron = network.findObject(Neuron, 'AVAL')
        
        Returns a list of :class:`Object <Network.Object.Object>` or None if there are no matching objects.
        
        If default is True then each object's :meth:`defaultName() <Network.Object.Object.defaultName>` will be queried instead of its name.
        """
        
        objects = []
        if name is not None:
            for networkObject in self.objects:
                if isinstance(networkObject, objectClass) and ((not default and networkObject.name == name) or (default and networkObject.defaultName() == name)):
                    objects.append(networkObject)
        return objects if objects else None

    
    def findObjectsRegex(self, objectClass, nameRegex = None, default = False):
        """
        Return all objects of the given class whos name matches the regular expression
        
        >>> neuron = network.findObject(Neuron, 'AVAL')
        
        Returns a list of :class:`Object <Network.Object.Object>` or None if there are no matching objects.
        
        """
        from re import search
        matchingObjects = []
        
        if nameRegex is not None:
            for networkObject in self.objects:
                if isinstance(networkObject, objectClass) and ((not default and search(nameRegex, networkObject.name)) or (default and search(nameRegex, networkObject.defaultName()))):
                    matchingObjects.append(networkObject)
        return matchingObjects if matchingObjects else None

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
    
    
    def _updateGraph(self, objectToUpdate = None):
        if objectToUpdate is None:
            # Rebuild the entire graph.
            objectsToUpdate = self.objects
            self.graph.clear()
        else:
            # Just rebuild the connections to the one object.
            objectsToUpdate = [objectToUpdate]
            # Remove the object if it was there before.  This will also delete any edges from the node.
            objectId = objectToUpdate.networkId
            if objectId in self.graph:
                self.graph.remove_node(objectId)
        
        # Maintain a temporary cache of weights so that rebuilding the whole graph doesn't take so long.
        objectWeights = {}
        def weightOfObject(weightedObject):
            if weightedObject.networkId in objectWeights:
                objectWeight = objectWeights[weightedObject.networkId]
            else:
                objectWeight = self.weightOfObject(weightedObject)
                objectWeights[weightedObject.networkId] = objectWeight
            return objectWeight
        
        for objectToUpdate in objectsToUpdate:
            objectId = objectToUpdate.networkId
            
            # (Re-)Add the object to the graph.
            self.graph.add_node(objectId)
            
            # Get the weight of this object.
            objectWeight = weightOfObject(objectToUpdate)
            
            # Add the connections to other objects already in the graph.
            # (Each connection to an object not in the graph will be added when that object is added.)
            # The weight of each edge is the average of the weights of the two objects it connects. 
            inputIds = set([objectInput.networkId for objectInput in objectToUpdate.inputs(recurse = False)])
            outputIds = set([objectOutput.networkId for objectOutput in objectToUpdate.outputs(recurse = False)])
            unknownIds = set([objectInput.networkId for objectInput in objectToUpdate.connections(recurse = False)]).difference(inputIds).difference(outputIds)
            for inputId in inputIds.union(unknownIds):
                if inputId in self.graph:
                    otherWeight = weightOfObject(objectToUpdate)
                    self.graph.add_edge(inputId, objectId, weight = (objectWeight + otherWeight) / 2.0)
            for outputId in outputIds.union(unknownIds):
                if outputId in self.graph:
                    otherWeight = weightOfObject(objectToUpdate)
                    self.graph.add_edge(objectId, outputId, weight = (objectWeight + otherWeight) / 2.0)
        
    
    def _objectChanged(self, sender):
        if not self._bulkLoading:
            self._updateGraph(sender)
            if not self._modified:
                self._modified = True
                dispatcher.send(('set', 'modified'), self)
    
    
    def simplifiedGraph(self):
        """
        Return a simplified version of the NetworkX representation of the network.
        
        This version of the network will have far fewer nodes but will not accurately model edges with more than two end points (hyperedges).  This speeds processing when using NetworkX's algorithms.
        """
        
        def addEdge(graph, object1, object2, weight):
            node1 = object1.networkId
            node2 = object2.networkId
            if node1 in graph and node2 in graph[node1]:
                if weight < graph[node1][node2]['weight']:
                    # Use a smaller weight for an existing edge.
                    graph[node1][node2]['weight'] = weight
            else:
                # Create a new edge.
                graph.add_edge(node1, node2, weight = weight)
        
        simplifiedGraph = DiGraph()
        
        # In self.graph edges are actually nodes to support hyperedges.  Convert these to standard edges in the simplified graph.
        # TODO: make this object type independent
        for arborization in self.arborizations():
            if arborization.sendsOutput:
                addEdge(simplifiedGraph, arborization.neurite.neuron(), arborization.region, self.weightOfObject(arborization))
            if arborization.receivesInput:
                addEdge(simplifiedGraph, arborization.region, arborization.neurite.neuron(), self.weightOfObject(arborization))
        for synapse in self.synapses():
            for postPartner in synapse.postSynapticPartners:
                if isinstance(postPartner, Neurite):
                    postPartner = postPartner.neuron()
                addEdge(simplifiedGraph, synapse.preSynapticNeurite.neuron(), postPartner, self.weightOfObject(synapse))
        for gapJunction in self.gapJunctions():
            neurites = gapJunction.neurites()
            addEdge(simplifiedGraph, neurites[0].neuron(), neurites[1].neuron(), self.weightOfObject(gapJunction))
            addEdge(simplifiedGraph, neurites[1].neuron(), neurites[0].neuron(), self.weightOfObject(gapJunction))
        for innervation in self.innervations():
            addEdge(simplifiedGraph, innervation.neurite.neuron(), innervation.muscle, self.weightOfObject(innervation))
        for pathway in self.pathways():
            region1, region2 = pathway.regions()
            weight = self.weightOfObject(pathway)
            if pathway.region1Projects:
                addEdge(simplifiedGraph, region1, region2, weight)
            if pathway.region2Projects:
                addEdge(simplifiedGraph, region2, region1, weight)
        for stimulus in self.stimuli():
            addEdge(simplifiedGraph, stimulus, stimulus.target.rootObject(), self.weightOfObject(stimulus))
        
        return simplifiedGraph
    
    
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
        
        # Update the NetworkX graph representation of the object and its connections.
        if not self._bulkLoading:
            self._updateGraph(objectToAdd)
        
        # Watch for any changes to the object so we can update our dirty state and the graph.
        dispatcher.connect(self._objectChanged, dispatcher.Any, objectToAdd)
        
        # Let anyone who cares know that the network was changed.
        if self._bulkLoading:
            self._bulkAddObjects += [objectToAdd]
        else:
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
    
    
    def setWeightingFunction(self, weightingFunction = None):
        """
        Set a function to be used to calculate the weight of objects in the network.
        
        The function should accept a single argument (an :class:`object <network.object.Object>` in the network) and return a floating point value indicating the weight of the object.  An object with a higher weight is considered more expensive to traverse.
        """
        
        if weightingFunction is not None and not callable(weightingFunction):
            raise ValueError, gettext('The function passed to setWeightingFunction must be callable.')
        
        if weightingFunction != self._weightingFunction:
            self._weightingFunction = weightingFunction
            self._updateGraph()
            dispatcher.send(('set', 'weightingFunction'), self)
    
    
    def weightingFunction(self):
        """
        Return the function being used to calculate the weights of objects in the network.
        
        If no function has been set then None will be returned.
        """
        
        return self._weightingFunction
    
    
    def weightOfObject(self, weightedObject):
        """
        Return the weight of the indicated object or 1.0 if no weighting function has been set.
        """
        
        return 1.0 if not self._weightingFunction else self._weightingFunction(weightedObject)
        
    
    def shortestPath(self, startObject, endObject):
        """
        Return one of the shortest paths through the :class:`network <Network.Network.Network>` from the first object to the second.
        
        Returns a list of objects in the path from the first object to the second.  If the second object cannot be reached from the first then an empty list will be returned. 
        """
        
        if not isinstance(startObject, Object) or startObject.network != self or not isinstance(endObject, Object) or endObject.network != self:
            raise ValueError, 'The objects passed to shortestPath() must be from the same network.'
        
        path = []
        try:
            nodeList = dijkstra_path(self.graph, startObject.networkId, endObject.networkId)
        except:
            nodeList = []
        for nodeID in nodeList:
            pathObject = self.objectWithId(nodeID)
            if pathObject is not startObject:
                path.append(pathObject)
        
        return path
    
    
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
                    self.graph.remove_node(objectToRemove.networkId)
            
            # Let anyone who cares know that the network was changed.
            dispatcher.send('deletion', self, affectedObjects = objectsToRemove)
    
    
    def removeAllObjects(self):
        """
        Remove all objects from the network and any displays.
        """
        
        removedObjects = list(self.objects)
        for networkObject in self.objects:
            networkObject.network = None
        self.objects = []
        self.idDict = {}
        self.graph.clear()
        
        # Let anyone who cares know that the network was changed.
        dispatcher.send('deletion', self, affectedObjects = removedObjects)
    
    
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
    
    
    def addAttribute(self, name = None, type = None, value = None): # pylint: disable=W0622
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
        