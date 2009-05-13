from Object import Object
from Arborization import Arborization
from Synapse import Synapse
from GapJunction import GapJunction
from Innervation import Innervation
import xml.etree.ElementTree as ElementTree

class Neurite(Object):
    
    def __init__(self, network, root, pathway = None, *args, **keywords):
        Object.__init__(self, network, *args, **keywords)
        self.root = root
        self._neurites = []
        self.arborization = None
        self.synapses = []
        self._gapJunctions = []
        self._innervations = []
        self.pathway = pathway
        if pathway is not None:
            pathway.neurites.append(self)
        #self.isStretchReceptor ???
    
    
    @classmethod
    def fromXMLElement(cls, network, xmlElement):
        object = super(Neurite, cls).fromXMLElement(network, xmlElement)
        pathwayId = xmlElement.get('pathwayId')
        object.pathway = network.objectWithId(pathwayId)
        if pathwayId is not None and object.pathway is None:
            raise ValueError, gettext('Pathway with id "%s" does not exist') % (pathwayId)
        object._neurites = []
        for neuriteElement in xmlElement.findall('Neurite'):
            neurite = Neurite.fromXMLElement(network, neuriteElement)
            if neurite is None:
                raise ValueError, gettext('Could not create neurite')
            neurite.root = object
            object._neurites.append(neurite)
            network.addObject(neurite)
        object.arborization = None
        object.synapses = []
        object._gapJunctions = []
        object._innervations = []
        return object
    
    
    def toXMLElement(self, parentElement):
        neuriteElement = Object.toXMLElement(self, parentElement)
        if self.pathway is not None:
            neuriteElement.set('pathwayId', str(self.pathway.networkId))
        for neurite in self._neurites:
            neurite.toXMLElement(neuriteElement)
        return neuriteElement
    
    
    def includeInScript(self, atTopLevel = False):
        # If this neurite is just a dummy neurite used to support a simple arborization, innervation, gap junction or synapse then it does not need to be created.
        from Neuron import Neuron
        connections = self.connections()
        if not self.needsScriptRef() and isinstance(self.root, Neuron) and len(connections) == 1:
            if isinstance(connections[0], (Arborization, Innervation, GapJunction, Synapse)):
                return False
        
        return Object.includeInScript(self)
    
    
    def needsScriptRef(self):
        return self.pathway is not None or len(self.connections()) > 1 or Object.needsScriptRef(self)
    
    
    def createScriptRef(self, scriptRefs):
        neuronRef = scriptRefs[self.neuron().networkId]
        if neuronRef in scriptRefs:
            neuriteCount = scriptRefs[neuronRef]
        else:
            neuriteCount = 0
        scriptRefs[neuronRef] = neuriteCount + 1
        scriptRefs[self.networkId] = neuronRef + '_neurite' + str(neuriteCount + 1)
        return scriptRefs[self.networkId]
    
    
    def creationScriptCommand(self, scriptRefs):
        return scriptRefs[self.root.networkId] + '.createNeurite'
    
    
    def creationScriptParams(self, scriptRefs):
        args, keywords = Object.creationScriptParams(self, scriptRefs)
        if self.pathway is not None:
            keywords['pathway'] = scriptRefs[pathway.networkId]
        return (args, keywords)
    
    
    def creationScriptChildren(self):
        children = Object.creationScriptChildren(self)
        children.extend(self._neurites)
        return children
    
    
    def neuron(self):
        parent = self.root
        while isinstance(parent, Neurite):
            parent = parent.root
        return parent
    
    
    def createNeurite(self, *args, **keywords):
        neurite = Neurite(self.network, self, *args, **keywords)
        self._neurites.append(neurite)
        return neurite
    
    
    def neurites(self, recurse = False):
        neurites = list(self._neurites)
        if recurse:
            for neurite in self._neurites:
                neurites.append(neurite.neurites(True))
        return neurites
    
    
    def arborize(self, region, sendsOutput=None, receivesInput=None, *args, **keywordArgs):
        # TODO: This will blow away any existing arborization.  Should a new sub-neurite be created?
        self.arborization = Arborization(self, region, sendsOutput, receivesInput, *args, **keywordArgs)
        region.arborizations.append(self.arborization)
        self.network.addObject(self.arborization)
        return self.arborization
    
    
    def synapseOn(self, otherObject, activation = None, *args, **keywordArgs):
        from Neuron import Neuron
        if isinstance(otherObject, Neuron):
            otherNeurite = otherObject.createNeurite()
        elif isinstance(otherObject, Neurite):
            otherNeurite = otherObject
        else:
            raise ValueError, gettext('Gap junctions can only be made with neurons or neurites')
        # TODO: handle iteratable
        synapse = Synapse(self.network, self, [otherNeurite], activation, *args, **keywordArgs)
        self.synapses.append(synapse)
        otherNeurite.synapses.append(synapse)
        self.network.addObject(synapse)
        return synapse
    
    
    def incomingSynapses(self):
        incomingSynapses = []
        for synapse in self.synapses:
            if synapse.preSynapticNeurite is not self:
                incomingSynapses.append(synapse)
        return incomingSynapses
    
    
    def outgoingSynapses(self):
        outgoingSynapses = []
        for synapse in self.synapses:
            if synapse.preSynapticNeurite is self:
                outgoingSynapses.append(synapse)
        return outgoingSynapses


    def gapJunctionWith(self, otherObject, *args, **keywordArgs):
        from Neuron import Neuron
        if isinstance(otherObject, Neuron):
            otherNeurite = otherObject.createNeurite()
        elif isinstance(otherObject, Neurite):
            otherNeurite = otherObject
        else:
            raise ValueError, gettext('Gap junctions can only be made with neurons or neurites')
        gapJunction = GapJunction(self.network, self, otherNeurite, *args, **keywordArgs)
        self._gapJunctions.append(gapJunction)
        otherNeurite._gapJunctions.append(gapJunction)
        self.network.addObject(gapJunction)
        return gapJunction
    
    
    def gapJunctions(self, recurse=False):
        junctions = []
        junctions.extend(self._gapJunctions)
        if recurse:
            for subNeurite in self._neurites:
                junctions.extend(subNeurite.gapJunctions(True))
        return junctions
    
    
    def setPathway(self, pathway):
        if self.pathway != None:
            self.pathway.neurites.remove(self)
        self.pathway = pathway
        pathway.neurites.append(self)
        
        
    def innervate(self, muscle, *args, **keywordArgs):
        innervation = Innervation(self.network, self, muscle, *args, **keywordArgs)
        self._innervations.append(innervation)
        muscle.innervations.append(innervation)
        self.network.addObject(innervation)
        return innervation
    
    
    def innervations(self, recurse=False):
        innervations = []
        innervations.extend(self._innervations)
        if recurse:
            for subNeurite in self._neurites:
                innervations.extend(subNeurite.innervations(True))
        return innervations
    
    
    def connections(self):
        connections = Object.connections(self)
        if self.arborization is not None:
            connections.append(self.arborization)
        for synapse in self.incomingSynapses():
            connections.append(synapse)
        for synapse in self.outgoingSynapses():
            connections.append(synapse)
        connections.extend(self._gapJunctions)
        connections.extend(self._innervations)
        for neurite in self._neurites:
            connections.extend(neurite.connections())
        return connections
    
    
    def inputs(self):
        inputs = Object.inputs(self)
        # TODO: handle receivesInput is None
        if self.arborization is not None and self.arborization.receivesInput:
            inputs.append(self.arborization)
        for synapse in self.incomingSynapses():
            inputs.append(synapse.preSynapticNeurite)
        inputs.extend(self._gapJunctions)
        for neurite in self._neurites:
            inputs.extend(neurite.inputs())
        return inputs
    
    
    def outputs(self):
        outputs = Object.outputs(self)
        # TODO: handle sendsOutput is None
        if self.arborization is not None and self.arborization.sendsOutput:
            outputs.append(self.arborization)
        for synapse in self.outgoingSynapses():
            outputs.extend(synapse.postSynapticNeurites)
        outputs.extend(self._gapJunctions)
        outputs.extend(self._innervations)
        for neurite in self._neurites:
            outputs.extend(neurite.outputs())
        return outputs
