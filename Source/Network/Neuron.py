from Object import Object
from Neurite import Neurite as Neurite


class Neuron(Object):
    # TODO: neurites method that returns all neurites
    
    UNIPOLAR = 'UNIPOLAR'
    BIPOLAR = 'BIPOLAR'
    PSEUDOUNIPOLAR = 'PSEUDOUNIPOLAR'
    MULTIPOLAR = 'MULTIPOLAR'
    
    
    def __init__(self, network, neuronClass = None, polarity = None, neurotransmitter = None, excitatory = None, *args, **keywords):
        Object.__init__(self, network, *args, **keywords)
        self._neurites = []
        self.neuronClass = neuronClass
        if self.neuronClass is not None:
            self.polarity = self.neuronClass.polarity
            self.neurotransmitter = self.neuronClass.neurotransmitter
            self.excitatory = self.neuronClass.excitatory
        else:
            self.polarity = polarity
            self.neurotransmitter = neurotransmitter
            self.excitatory = excitatory
    
    
    def createNeurite(self):
        neurite = Neurite(self.network, self)
        self._neurites.append(neurite)
        return neurite
    
    
    def neurites(self, recurse = False):
        neurites = list(self._neurites)
        if recurse:
            for neurite in self._neurites:
                neurites.append(neurite.neurites(True))
        return neurites
    
    
    def arborize(self, region, input=True, output=True):
        """Convenience method for creating a neurite and having it arborize a region."""
        self.createNeurite().arborize(region, input, output)
    
    
    def arborizations(self):
        arborizations = []
        for neurite in self._neurites:
            if neurite.arborization is not None:
                arborizations.append(neurite.arborization)
        return arborizations
    
    
    def synapseOn(self, otherNeuron):
        """Convenience method that creates a neurite for each neuron and then creates a synapse between them."""
        neurite = self.createNeurite()
        otherNeurite = otherNeuron.createNeurite()
        return neurite.synapseOn(neurite = otherNeurite, excitatory = self.excitatory)
    
    
    def incomingSynapses(self):
        incomingSynapses = []
        for neurite in self._neurites:
            incomingSynapses.extend(neurite.incomingSynapses())
        return incomingSynapses
    
    
    def outgoingSynapses(self):
        outgoingSynapses = []
        for neurite in self._neurites:
            outgoingSynapses.extend(neurite.outgoingSynapses())
        return outgoingSynapses
    
    
    def gapJunctionWith(self, otherNeuron):
        """Convenience method that creates a neurite for each neuron and then creates a gap junction between them."""
        neurite = self.createNeurite()
        otherNeurite = otherNeuron.createNeurite()
        return neurite.gapJunctionWith(otherNeurite)
    
    
    def gapJunctions(self):
        junctions = []
        for neurite in self._neurites:
            junctions.extend(neurite.gapJunctions())
        return junctions
        
        
    def innervate(self, muscle):
        """Convenience method that creates a neurite and has it innervate the muscle."""
        neurite = self.createNeurite()
        return neurite.innervate(muscle)
    
    
    def innervations(self):
        innervations = []
        for neurite in self._neurites:
            innervations.extend(neurite.innervations())
        return innervations


    def connections(self):
        # TODO: untested
        connections = set()
        for neurite in self._neurites:
            if neurite.arborization is not None:
                connections.add(neurite.arborization.region)
            for synapse in neurite.incomingSynapses():
                connections.add(synapse.presynapticNeurite.neuron)
            for synapse in neurite.outgoingSynapses():
                connections.add(synapse.postsynapticNeurites(0).neuron)
        return connections
    
    
    def inputs(self):
        inputs = Object.inputs(self)
        for neurite in self._neurites:
            inputs.extend(neurite.inputs())
        return inputs
    
    
    def outputs(self):
        outputs = Object.outputs(self)
        for neurite in self._neurites:
            outputs.extend(neurite.outputs())
        return outputs
