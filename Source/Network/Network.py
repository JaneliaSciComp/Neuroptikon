from networkx import *
import os.path, sys
from wx.py import dispatcher
import xml.etree.ElementTree as ElementTree
from Region import Region
from Pathway import Pathway
from Neuron import Neuron
from Neurite import Neurite
from Arborization import Arborization
from Synapse import Synapse
from GapJunction import GapJunction
from Stimulus import Stimulus
from Muscle import Muscle
from Innervation import Innervation
from Attribute import Attribute

try:
    import pydot
except:
    pydot = None


class Network:
    
    def __init__(self):
        self.graph = XGraph()
        self.objects = []
        self.idDict = {}   # TODO: weak ref dict?
        self.displays = []
        self._nextUniqueId = -1
        self._savePath = None
        self.attributes = []
        self._displaysAreSynchronized = True
    
    
    @classmethod
    def fromXMLElement(cls, xmlElement):
        network = cls()
        # Load the classes in such an order that any referenced objects are guaranteed to have already been created.
        for className in ['Region', 'Pathway', 'Neuron', 'Muscle', 'Arborization', 'Innervation', 'GapJunction', 'Synapse', 'Stimulus']:
            elementModule = getattr(sys.modules['Network'], className)
            elementClass = getattr(elementModule, className)
            for element in xmlElement.findall(className):
                object = elementClass.fromXMLElement(network, element)
                if object is not None:
                    network.addObject(object)
        
        for element in xmlElement.findall('Attribute'):
            attribute = Attribute.fromXMLElement(network, element)
            if attribute is not None:
                network.attributes.append(attribute)
        
        return network
    
    
    def toXMLElement(self, parentElement):
        networkElement = ElementTree.SubElement(parentElement, 'Network')
        for object in self.objects:
            # Nested regions are handled by their parents and neurites are handled by their neurons.
            if not (isinstance(object, Region) and object.parentRegion is not None) and not isinstance(object, Neurite):
                objectElement = object.toXMLElement(networkElement)
                if objectElement is None:
                    pass    # TODO: are there any cases where this is NOT an error?
        for attribute in self.attributes:
            attribute.toXMLElement(networkElement)
        return networkElement
    
    
    def toScriptFile(self, scriptFile, scriptRefs):
        if len(self.attributes) > 0:
            scriptFile.write(gettext('# Create the network') + '\n\n')
            for attribute in self.attributes:
                attribute.toScriptFile(scriptFile, scriptRefs)
        
        # Add each network object to the script in an order that guarantees dependent objects will already have been added.
        # Neurites will be added by their neurons, sub-regions by their root region.
        for objectClass in (Region, Pathway, Muscle, Neuron, Arborization, GapJunction, Innervation, Synapse, Stimulus):
            objects = self.objectsOfClass(objectClass)
            if len(objects) > 0:
                scriptFile.write('\n# ' + gettext('Create each %s') % (objectClass.displayName().lower()) + '\n\n')
                for object in objects:
                    if object.includeInScript(atTopLevel = True):
                        object.toScriptFile(scriptFile, scriptRefs)
   
   
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
    
    def nextUniqueId(self):
        self._nextUniqueId += 1
        return self._nextUniqueId
    
    
    def findObject(self, objectClass, name = None, default = False):
        if name is not None:
            for object in self.objects:
                if isinstance(object, objectClass) and ((not default and object.name == name) or (default and object.defaultName() == name)):
                    return object
        return None
    
    
    def createRegion(self, addSubTerms = False, *args, **keywordArgs):
        region = Region(self, *args, **keywordArgs)
        self.addObject(region)
        
        if region.ontologyTerm is not None and addSubTerms:
            for term in region.ontologyTerm.parts:
                self.createRegion(ontologyTerm = term, parentRegion = region, addSubTerms = True)
        
        return region
    
    
    def findRegion(self, name = None):
        return self.findObject(Region, name)
    
    
    def regions(self):
        return self.objectsOfClass(Region)
    
    
    def pathways(self):
        return self.objectsOfClass(Pathway)
    
    
    def createNeuron(self, *args, **keywordArgs):
        neuron = Neuron(self, *args, **keywordArgs)
        self.addObject(neuron)
        return neuron
    
    
    def findNeuron(self, name = None):
        return self.findObject(Neuron, name)
    
    
    def neurons(self):
        return self.objectsOfClass(Neuron)
    
    
    def neurites(self):
        return self.objectsOfClass(Neurite)
    
    
    def arborizations(self):
        return self.objectsOfClass(Arborization)
    
    
    def gapJunctions(self):
        return self.objectsOfClass(GapJunction)
    
    
    def innervations(self):
        return self.objectsOfClass(Innervation)
    
    
    def synapses(self):
        return self.objectsOfClass(Synapse)
    
    
    def createStimulus(self, *args, **keywordArgs):
        target = keywordArgs['target']
        del keywordArgs['target']
        
        return target.stimulate(*args, **keywordArgs)
    
    
    def findStimulus(self, name = None):
        return self.findObject(Stimulus, name)
    
    
    def stimuli(self):
        return self.objectsOfClass(Stimulus)
    
    
    def createMuscle(self, *args, **keywordArgs):
        muscle = Muscle(self, *args, **keywordArgs)
        self.addObject(muscle)
        return muscle
    
    
    def findMuscle(self, name = None):
        return self.findObject(Muscle, name)
    
    
    def muscles(self):
        return self.objectsOfClass(Muscle)
    
    
    def addObject(self, object):
        if object.networkId in self.idDict:
            raise ValueError, gettext('All objects in a network must have unique identifiers.')
        
        self.objects.append(object)
        self.idDict[object.networkId] = object
        
        if object.networkId > self._nextUniqueId:
            self._nextUniqueId = object.networkId
        
        if isinstance(object, Arborization):
            self.graph.add_edge(object.neurite.neuron().networkId, object.region.networkId, object)
        elif isinstance(object, Synapse):
            self.graph.add_edge(object.preSynapticNeurite.neuron().networkId, object.postSynapticNeurites[0].neuron().networkId, object) # TODO: need to handle hyper-edges?
        elif isinstance(object, GapJunction):
            neurites = list(object.neurites)
            self.graph.add_edge(neurites[0].neuron().networkId, neurites[1].neuron().networkId, object)
        elif isinstance(object, Pathway):
            self.graph.add_edge(object.terminus1.region.networkId, object.terminus2.region.networkId, object)
        elif isinstance(object, Innervation):
            self.graph.add_edge(object.neurite.neuron().networkId, object.muscle.networkId, object)
        elif isinstance(object, Stimulus):
            self.graph.add_node(object.networkId)
            self.graph.add_edge(object.networkId, object.target.networkId, object)
        elif isinstance(object, Region) or isinstance(object, Neuron) or isinstance(object, Muscle):
            self.graph.add_node(object.networkId)
        dispatcher.send('addition', self, affectedObjects = [object])
    
    
    def objectWithId(self, objectId):
        if (isinstance(objectId, str) or isinstance(objectId, unicode)) and objectId.isdigit():
            objectId = int(objectId)
        
        return self.idDict[objectId] if objectId in self.idDict else None
    
    
    def objectsOfClass(self, objectClass):
        objects = []
        for object in self.objects:
            if isinstance(object, objectClass):
                objects.append(object)
        return objects
    
    
    def addDisplay(self, display):
        self.displays.append(display)
        dispatcher.connect(self.synchronizeDisplays, ('set', 'selection'), display)
    
    
    def removeDisplay(self, display):
        self.displays.remove(display)
        dispatcher.disconnect(self.synchronizeDisplays, ('set', 'selection'), display)
    
    
    def synchronizeDisplays(self, signal, sender):
        if self._displaysAreSynchronized:
            selection = sender.selectedObjects()
            for display in self.displays:
                if display != sender:
                    display.selectObjects(selection)
    

    def to_pydot(self, graph_attr=None, node_attr=None, edge_attr=None):
        # This is a custom version of networkx.drawing.nx_pydot.to_pydot() that works around a bug in pydot 1.0.2.
        
        if pydot is None:
            return None
        
        if graph_attr is not None:
            graph_attributes = graph_attr
        else:
            graph_attributes = {}

        try:
            node_a = self.graph.node_attr
        except:
            node_a = {}
        if node_attr is not None:        
            node_a.update(node_attr)

        P = pydot.Dot(graph_type='graph', strict=False)

        for n in self.graph.nodes_iter():
            if n in node_a:
                attr=node_a[n]
            else:
                attr={}
            p=pydot.Node(str(n),**attr)
            P.add_node(p)
        
        # This is the workaround for the pydot bug.  As long as every edge has some attribute then it works.
        for (u, v, x) in self.graph.edges_iter():
            attr = {'label': ''}
            edge = pydot.Edge(str(u), str(v), **attr)
            P.add_edge(edge)

        try:
            P.obj_dict['attributes'].update(graph_attributes['graph'])
        except:
            pass
        try:
            P.obj_dict['nodes']['node'][0]['attributes'].update(graph_attributes['node'])
        except:
            pass
        try:
            P.obj_dict['nodes']['edge'][0]['attributes'].update(graph_attributes['edge'])
        except:
            pass

        return P
    
    
    def addAttribute(self, name = None, type = None, value = None):
        """addAttribute(name = None, type = None, value = None) -> Attribute instance
        
        The type parameter should be one of the Attribute.*_TYPE values.
        
        >>> network.addAttribute('Complete', Attribute.BOOLEAN_VALUE, True)"""
        
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
