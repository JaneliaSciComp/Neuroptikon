from Object import Object
from Neurite import Neurite as Neurite
import xml.etree.ElementTree as ElementTree
import wx

class Neuron(Object):
    # TODO: neurites method that returns all neurites
    
    
    class Polarity:
        UNIPOLAR = 'UNIPOLAR'
        BIPOLAR = 'BIPOLAR'
        PSEUDOUNIPOLAR = 'PSEUDOUNIPOLAR'
        MULTIPOLAR = 'MULTIPOLAR'
    
    
    class Function:
        SENSORY = 'SENSORY'
        INTERNEURON = 'INTERNEURON'
        MOTOR = 'MOTOR'
    
    
    def __init__(self, network, neuronClass = None, *args, **keywordArgs):
        # Pull out the keyword arguments specific to this class before we call super.
        # We need to do this so we can know if the caller specified an argument or not.
        # For example, the caller might specify a neuron class and one attribute to override.  We need to know which attributes _not_ to set.
        localAttrNames = ['activation', 'function', 'neurotransmitter', 'polarity', 'region']
        localKeywordArgs = {}
        for attrName in localAttrNames:
            if attrName in keywordArgs:
                localKeywordArgs[attrName] = keywordArgs[attrName]
                del keywordArgs[attrName]
        
        Object.__init__(self, network, *args, **keywordArgs)
        
        self._neurites = []
        self.neuronClass = neuronClass
        
        for attrName in localAttrNames:
            attrValue = None
            if attrName in localKeywordArgs:
                attrValue = localKeywordArgs[attrName]  # The user has explicitly set the attribute.
            elif self.neuronClass:
                attrValue = getattr(self.neuronClass, attrName) # Inherit the value from the class
            setattr(self, attrName, attrValue)
        
        if self.region is not None:
            self.region.neurons.append(self)
    
    
    @classmethod
    def fromXMLElement(cls, network, xmlElement):
        object = super(Neuron, cls).fromXMLElement(network, xmlElement)
        classId = xmlElement.findtext('Class')
        if classId is None:
            classId = xmlElement.findtext('class')
        object.neuronClass = wx.GetApp().library.neuronClass(classId)
        if classId is not None and object.neuronClass is None:
            raise ValueError, gettext('Neuron class "%s" does not exist') % (classId)
        ntId = xmlElement.findtext('Neurotransmitter')
        if ntId is None:
            ntId = xmlElement.findtext('neurotransmitter')
        object.neurotransmitter = wx.GetApp().library.neurotransmitter(ntId)
        if ntId is not None and  object.neurotransmitter is None:
            raise ValueError, gettext('Neurotransmitter "%s" does not exist') % (ntId)
        object.activation = xmlElement.findtext('Activation')
        if object.activation is None:
            object.activation = xmlElement.findtext('activation')
        object.function = xmlElement.findtext('Function')
        if object.function is None:
            object.function = xmlElement.findtext('function')
        object.polarity = xmlElement.findtext('Polarity')
        if object.polarity is None:
            object.polarity = xmlElement.findtext('polarity')
        regionId = xmlElement.get('somaRegionId')
        object.region = network.objectWithId(regionId)
        if regionId is not None and object.region is None:
            raise ValueError, gettext('Region with id "%s" does not exist') % (regionId)
        if object.region is not None:
            object.region.neurons.append(object)
        object._neurites = []
        for neuriteElement in xmlElement.findall('Neurite'):
            neurite = Neurite.fromXMLElement(network, neuriteElement)
            if neurite is None:
                raise ValueError, gettext('Could not create neurite')
            neurite.root = object
            object._neurites.append(neurite)
            network.addObject(neurite)
        return object
    
    
    def toXMLElement(self, parentElement):
        neuronElement = Object.toXMLElement(self, parentElement)
        if self.neuronClass is not None:
            ElementTree.SubElement(neuronElement, 'Class').text = self.neuronClass.identifier
        if self.neurotransmitter is not None:
            ElementTree.SubElement(neuronElement, 'Neurotransmitter').text = self.neurotransmitter.identifier
        if self.activation is not None:
            ElementTree.SubElement(neuronElement, 'Activation').text = self.activation
        if self.function is not None:
            ElementTree.SubElement(neuronElement, 'Function').text = self.function
        if self.polarity is not None:
            ElementTree.SubElement(neuronElement, 'Polarity').text = self.polarity
        if self.region is not None:
            ElementTree.SubElement(neuronElement, 'SomaRegionId').text = str(self.region.networkId)
        for neurite in self._neurites:
            neurite.toXMLElement(neuronElement)
        return neuronElement
    
    
    def needsScriptRef(self):
        return len(self._neurites) > 0 or Object.needsScriptRef(self)
    
    
    def creationScriptParams(self, scriptRefs):
        args, keywords = Object.creationScriptParams(self, scriptRefs)
        if self.neuronClass is not None:
            keywords['neuronClass'] = 'library.neuronClass(\'' + self.neuronClass.identifier + '\')'
        if self.neurotransmitter is not None:
            keywords['neurotransmitter'] = 'library.neurotransmitter(\'' + self.neurotransmitter.identifier + '\')'
        if self.activation is not None:
            keywords['activation'] = '\'' + self.activation + '\''  # TODO: this should be 'NeuralActivation.' + self.activation
        if self.function is not None:
            keywords['function'] = 'NeuralFunction.' +  self.function
        if self.polarity is not None:
            keywords['polarity'] = 'NeuralPolarity.' +  self.polarity
        if self.region is not None:
            keywords['region'] = scriptRefs[self.region.networkId]
        return (args, keywords)
    
    
    def creationScriptChildren(self):
        children = Object.creationScriptChildren(self)
        children.extend(self._neurites)
        return children
   
    
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
    
    
    def arborize(self, region, input=True, output=True, *args, **keywordArgs):
        """Convenience method for creating a neurite and having it arborize a region."""
        self.createNeurite().arborize(region, input, output)
    
    
    def arborizations(self):
        arborizations = []
        for neurite in self._neurites:
            if neurite.arborization is not None:
                arborizations.append(neurite.arborization)
        return arborizations
    
    
    def synapseOn(self, otherObject, *args, **keywordArgs):
        """Convenience method that creates a neurite for each neuron and then creates a synapse between them."""
        neurite = self.createNeurite()
        return neurite.synapseOn(otherObject, activation = self.activation, *args, **keywordArgs)
    
    
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
    
    
    def gapJunctionWith(self, otherObject, *args, **keywordArgs):
        """Convenience method that creates a neurite for this neuron and then creates a gap junction with the other object."""
        neurite = self.createNeurite()
        return neurite.gapJunctionWith(otherObject, *args, **keywordArgs)
    
    
    def gapJunctions(self):
        junctions = []
        for neurite in self._neurites:
            junctions.extend(neurite.gapJunctions())
        return junctions
        
        
    def innervate(self, muscle, *args, **keywordArgs):
        """Convenience method that creates a neurite and has it innervate the muscle."""
        neurite = self.createNeurite()
        return neurite.innervate(muscle, *args, **keywordArgs)
    
    
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
                connections.add(synapse.preSynapticNeurite.neuron)
            for synapse in neurite.outgoingSynapses():
                connections.add(synapse.postSynapticNeurites(0).neuron)
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
