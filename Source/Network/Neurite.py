from Object import Object
from Arborization import Arborization
from Synapse import Synapse
from GapJunction import GapJunction
from Innervation import Innervation

class Neurite(Object):
    
    def __init__(self, network, root, name=None):
        Object.__init__(self, network, name)
        self.root = root
        self.subNeurites = []
        self.arborization = None
        self.synapses = []
        self._gapJunctions = []
        self._innervations = []
        self.pathway = None
        #self.isStretchReceptor ???
    
    
    def neuron(self):
        parent = self.root
        while isinstance(parent, Neurite):
            parent = parent.root
        return parent
    
    
    def arborize(self, region, input=True, output=True):
        self.arborization = Arborization(self, region, input, output)
        region.arborizations.append(self.arborization)
        self.network.addObject(self.arborization)
    
    
    def synapseOn(self, neurite):
        synapse = Synapse(self.network, self, [neurite])
        self.synapses.append(synapse)
        neurite.synapses.append(synapse)
        self.network.addObject(synapse)
        return synapse
    
    
    def incomingSynapses(self):
        incomingSynapses = []
        for synapse in self.synapses:
            if synapse.presynapticNeurite is not self:
                incomingSynapses.append(synapse)
        return incomingSynapses
    
    
    def outgoingSynapses(self):
        outgoingSynapses = []
        for synapse in self.synapses:
            if synapse.presynapticNeurite is self:
                outgoingSynapses.append(synapse)
        return outgoingSynapses


    def gapJunctionWith(self, neurite):
        gapJunction = GapJunction(self.network, self, neurite)
        self._gapJunctions.append(gapJunction)
        neurite._gapJunctions.append(gapJunction)
        self.network.addObject(gapJunction)
        return gapJunction
    
    
    def gapJunctions(self, recurse=False):
        junctions = []
        junctions.extend(self._gapJunctions)
        if recurse:
            for subNeurite in self.subNeurites:
                junctions.extend(subNeurite.gapJunctions(True))
        return junctions
    
    
    def setPathway(self, pathway):
        if self.pathway != None:
            self.pathway.neurites.remove(self)
        self.pathway = pathway
        pathway.neurites.append(self)
        
        
    def innervate(self, muscle):
        innervation = Innervation(self.network, self, muscle)
        self._innervations.append(innervation)
        muscle.innervations.append(innervation)
        self.network.addObject(innervation)
        return innervation
    
    
    def innervations(self, recurse=False):
        innervations = []
        innervations.extend(self._innervations)
        if recurse:
            for subNeurite in self.subNeurites:
                innervations.extend(subNeurite.innervations(True))
        return innervations
    
    
    def inputs(self):
        inputs = Object.inputs(self)
        if self.arborization is not None and self.arborization.receivesInput:
            inputs.append(self.arborization)
        for synapse in self.incomingSynapses():
            inputs.append(synapse.presynapticNeurite)
        inputs.extend(self._gapJunctions)
        for neurite in self.subNeurites:
            inputs.extend(neurite.inputs())
        return inputs
    
    
    def outputs(self):
        outputs = Object.outputs(self)
        if self.arborization is not None and self.arborization.sendsOutput:
            outputs.append(self.arborization)
        for synapse in self.outgoingSynapses():
            outputs.extend(synapse.postsynapticNeurites)
        outputs.extend(self._gapJunctions)
        outputs.extend(self._innervations)
        for neurite in self.subNeurites:
            outputs.extend(neurite.outputs())
        return outputs
