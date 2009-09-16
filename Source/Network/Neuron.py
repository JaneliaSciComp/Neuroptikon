from Object import Object
from Neurite import Neurite as Neurite
import xml.etree.ElementTree as ElementTree
import wx
from pydispatch import dispatcher


class Neuron(Object):
    
    
    class Polarity:
        UNIPOLAR = 'UNIPOLAR'
        BIPOLAR = 'BIPOLAR'
        PSEUDOUNIPOLAR = 'PSEUDOUNIPOLAR'
        MULTIPOLAR = 'MULTIPOLAR'
    
    
    class Function:
        SENSORY = 'SENSORY'
        INTERNEURON = 'INTERNEURON'
        MOTOR = 'MOTOR'
    
    Functions = [Function.SENSORY, Function.INTERNEURON, Function.MOTOR]
    
    
    def __init__(self, network, neuronClass = None, *args, **keywordArgs):
        """
        Neurons represent individual neural cells in the network.
        
        You create a neuron by messaging the network:
        
        >>> neuron1 = network.createNeuron(...)
        """
        
        # Upconvert old 'function' singleton param to list expected by new 'functions' param.
        if 'function' in keywordArgs:
            keywordArgs['functions'] = set([keywordArgs['function']])
            del keywordArgs['function']
        # Upconvert old 'neurotransmitter' singleton param to list expected by new 'neurotransmitters' param.
        if 'neurotransmitter' in keywordArgs:
            keywordArgs['neurotransmitters'] = [keywordArgs['neurotransmitter']]
            del keywordArgs['neurotransmitter']
        
        # Pull out the keyword arguments specific to this class before we call super.
        # We need to do this so we can know if the caller specified an argument or not.
        # For example, the caller might specify a neuron class and one attribute to override.  We need to know which attributes _not_ to set.
        localAttrNames = ['activation', 'functions', 'neurotransmitters', 'polarity', 'region']
        localKeywordArgs = {}
        for attrName in localAttrNames:
            if attrName in keywordArgs:
                localKeywordArgs[attrName] = keywordArgs[attrName]
                del keywordArgs[attrName]
        
        Object.__init__(self, network, *args, **keywordArgs)
        
        self._neurites = []
        self.neuronClass = neuronClass
        self._functions = set()
        
        for attrName in localAttrNames:
            if attrName == 'functions':
                attrValue = set()
            elif attrName == 'neurotransmitters':
                attrValue = []
            else:
                attrValue = None
            if attrName in localKeywordArgs:
                # The user has explicitly set the attribute.
                if attrName == 'functions':
                    attrValue = set(localKeywordArgs[attrName])
                else:
                    attrValue = localKeywordArgs[attrName]  
            elif self.neuronClass:
                attrValue = getattr(self.neuronClass, attrName) # Inherit the value from the class
            if attrName == 'functions':
                attrName = '_functions'
            setattr(self, attrName, attrValue)
        
        if self.region is not None:
            self.region.neurons.append(self)
    
    
    @classmethod
    def _fromXMLElement(cls, network, xmlElement):
        object = super(Neuron, cls)._fromXMLElement(network, xmlElement)
        classId = xmlElement.findtext('Class')
        if classId is None:
            classId = xmlElement.findtext('class')
        object.neuronClass = wx.GetApp().library.neuronClass(classId)
        if classId is not None and object.neuronClass is None:
            raise ValueError, gettext('Neuron class "%s" does not exist') % (classId)
        object.neurotransmitters = []
        for ntName in ['Neurotransmitter', 'neurotransmitter']:
            for ntElement in xmlElement.findall(ntName):
                ntId = ntElement.text
                if ntId is not None:
                    nt = wx.GetApp().library.neurotransmitter(ntId)
                    if nt is None:
                        raise ValueError, gettext('Neurotransmitter "%s" does not exist') % (ntId)
                    else:
                        object.neurotransmitters.append(nt)
        object.activation = xmlElement.findtext('Activation')
        if object.activation is None:
            object.activation = xmlElement.findtext('activation')
        object._functions = set()
        for functionName in ['Function', 'function']:
            for functionElement in xmlElement.findall(functionName):
                if functionElement.text in Neuron.Functions:
                    object.setHasFunction(functionElement.text, True)
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
            neurite = Neurite._fromXMLElement(network, neuriteElement)
            if neurite is None:
                raise ValueError, gettext('Could not create neurite')
            neurite.root = object
            object._neurites.append(neurite)
            network.addObject(neurite)
        return object
    
    
    def _toXMLElement(self, parentElement):
        neuronElement = Object._toXMLElement(self, parentElement)
        if self.neuronClass is not None:
            ElementTree.SubElement(neuronElement, 'Class').text = self.neuronClass.identifier
        for neurotransmitter in self.neurotransmitters:
            ElementTree.SubElement(neuronElement, 'Neurotransmitter').text = neurotransmitter.identifier
        if self.activation is not None:
            ElementTree.SubElement(neuronElement, 'Activation').text = self.activation
        for function in self._functions:
            ElementTree.SubElement(neuronElement, 'Function').text = function
        if self.polarity is not None:
            ElementTree.SubElement(neuronElement, 'Polarity').text = self.polarity
        if self.region is not None:
            ElementTree.SubElement(neuronElement, 'SomaRegionId').text = str(self.region.networkId)
        for neurite in self._neurites:
            neurite._toXMLElement(neuronElement)
        return neuronElement
    
    
    def _needsScriptRef(self):
        return len(self._neurites) > 0 or Object._needsScriptRef(self)
    
    
    def _creationScriptParams(self, scriptRefs):
        args, keywords = Object._creationScriptParams(self, scriptRefs)
        if self.neuronClass is not None:
            keywords['neuronClass'] = 'library.neuronClass(\'' + self.neuronClass.identifier + '\')'
        if len(self.neurotransmitters) > 0:
            ntCalls = []
            for neurotransmitter in self.neurotransmitters:
                ntCalls.append('library.neurotransmitter(\'' + neurotransmitter.identifier + '\')')
            keywords['neurotransmitters'] = '[' + ', '.join(ntCalls) + ']'
        if self.activation is not None:
            keywords['activation'] = '\'' + self.activation + '\''  # TODO: this should be 'NeuralActivation.' + self.activation
        if len(self._functions) > 0:
            keywords['functions'] = '[Neuron.Function.' + ', Neuron.Function.'.join(self._functions) + ']'
        if self.polarity is not None:
            keywords['polarity'] = 'Neuron.Polarity.' +  self.polarity
        if self.region is not None:
            keywords['region'] = scriptRefs[self.region.networkId]
        return (args, keywords)
    
    
    def _creationScriptChildren(self):
        children = Object._creationScriptChildren(self)
        children.extend(self._neurites)
        return children
   
    
    def createNeurite(self, *args, **keywords):
        """
        Create and return a :class:`neurite <Network.Neurite.Neurite>` object that projects from the soma of this neuron.
        """
        
        neurite = Neurite(self.network, self, *args, **keywords)
        self._neurites.append(neurite)
        self.network.addObject(neurite)
        return neurite
    
    
    def neurites(self, recurse = True):
        """
        Return a list of all :class:`neurite <Network.Neurite.Neurite>` projecting from this neuron.
        
        If recurse is True then all subsequently projecting neurites will be included with the neurites that project from the soma.
        
        If no neurites project from the soma of this neuron then an empty list will be returned.
        """
        
        neurites = list(self._neurites)
        if recurse:
            for neurite in self._neurites:
                neurites += neurite.neurites()
        return neurites
    
    
    def arborize(self, region, sendsOutput = True, receivesInput = True, *args, **keywordArgs):
        """
        Convenience method for creating a :class:`neurite <Network.Neurite.Neurite>` and having it :class:`arborize <Network.Neurite.Neurite.arborize>` a :class:`region <Network.Region.Region>`.
        
        Returns the arborization object that is created.
        """
        
        return self.createNeurite().arborize(region, sendsOutput, receivesInput, *args, **keywordArgs)
    
    
    def arborizations(self):
        """
        Return a list of all :class:`arborizations <Network.Arborization.Arborization>` extending from this neuron.
        
        If this neuron does not arborize any regions then an empty list will be returned.
        """
        
        arborizations = []
        for neurite in self._neurites:
            arborizations += neurite.arborizations()
        return arborizations
    
    
    def synapseOn(self, otherObject, *args, **keywordArgs):
        """
        Convenience method that creates a :class:`neurite <Network.Neurite.Neurite>` for this neuron and then creates a :class:`synapse <Network.Synapse.Synapse>` with the other object.
        
        Returns the synapse object that is created.
        """
        
        neurite = self.createNeurite()
        return neurite.synapseOn(otherObject, activation = self.activation, *args, **keywordArgs)
    
    
    def synapses(self, includePre = True, includePost = True):
        """
        Return a list of all :class:`synapses <Network.Synapse.Synapse>` in which the :class:`neurite's <Network.Neurite.Neurite>` of this neuron are pre- or post-synaptic.
        
        If includePre is False then synapses where this neuron is pre-synaptic will be excluded.  If includePost is False then synapses where this neuron is post-synaptic will be excluded.
        
        If this neuron does not form a synapse with any other neurons then an empty list will be returned.
        """
        
        synapses = []
        for neurite in self._neurites:
            synapses += neurite.synapses(includePre = includePre, includePost = includePost)
        return synapses
    
    
    def gapJunctionWith(self, otherObject, *args, **keywordArgs):
        """
        Convenience method that creates a :class:`neurite <Network.Neurite.Neurite>` for this neuron and then creates a :class:`gap junction <Network.GapJunction.GapJunction>` with the other object.
        
        Returns the gap junction object that is created.
        """
        
        neurite = self.createNeurite()
        return neurite.gapJunctionWith(otherObject, *args, **keywordArgs)
    
    
    def gapJunctions(self):
        """
        Return a list of all :class:`gap junctions <Network.GapJunction.GapJunction>` in which the :class:`neurite's <Network.Neurite.Neurite>` of this neuron are involved.
        
        If this neuron does not form a gap junction with any other neurons then an empty list will be returned.
        """
        
        junctions = []
        for neurite in self._neurites:
            junctions += neurite.gapJunctions()
        return junctions
        
        
    def innervate(self, muscle, *args, **keywordArgs):
        """
        Convenience method that creates a :class:`neurite <Network.Neurite.Neurite>` and has it innervate the :class:`muscle <Network.Muscle.Muscle>`.
        
        Returns the :class:`innervation <Network.Innervation.Innervation>` object that is created.
        """
        
        neurite = self.createNeurite()
        return neurite.innervate(muscle, *args, **keywordArgs)
    
    
    def innervations(self):
        """
        Return a list of all :class:`innervations <Network.Innervation.Innervation>` involving this neuron's :class:`neurite's <Network.Neurite.Neurite>`.
        
        If this neuron does not innervate any :class:`muscles <Network.Muscle.Muscle>` then an empty list will be returned.
        """
        
        innervations = []
        for neurite in self._neurites:
            innervations += neurite.innervations()
        return innervations


    def connections(self, recurse = True):
        """
        Return a list of all objects that connect to this neuron and optionally any projecting :class:`neurites <Network.Neurite.Neurite>`.
        
        The list may contain any number of :class:`arborizations <Network.Arborization.Arborization>`, :class:`gap junctions <Network.GapJunction.GapJunction>`, :class:`innervations <Network.Innervation.Innervation>`, :class:`stimuli <Network.Stimulus.Stimulus>` or :class:`synapses <Network.Synapse.Synapse>`.
        """
        
        connections = Object.connections(self, recurse)
        if recurse:
            for neurite in self._neurites:
                connections += neurite.connections()
        return connections
    
    
    def inputs(self, recurse = True):
        """
        Return a list of all objects that send information into this neuron and optionally any projecting :class:`neurites <Network.Neurite.Neurite>`.
        
        The list may contain any number of :class:`arborizations <Network.Arborization.Arborization>`, :class:`gap junctions <Network.GapJunction.GapJunction>`, :class:`stimuli <Network.Stimulus.Stimulus>` or :class:`synapses <Network.Synapse.Synapse>`.
        """
        
        inputs = Object.inputs(self, recurse)
        if recurse:
            for neurite in self._neurites:
                inputs += neurite.inputs()
        return inputs
    
    
    def outputs(self, recurse = True):
        """
        Return a list of all objects that receive information from this neuron and optionally any projecting :class:`neurites <Network.Neurite.Neurite>`.
        
        The list may contain any number of :class:`arborizations <Network.Arborization.Arborization>`, :class:`gap junctions <Network.GapJunction.GapJunction>`, :class:`innervations <Network.Innervation.Innervation>` or :class:`synapses <Network.Synapse.Synapse>`.
        """
        
        outputs = Object.outputs(self, recurse)
        if recurse:
            for neurite in self._neurites:
                outputs += neurite.outputs()
        return outputs
    
    
    def setHasFunction(self, function, hasFunction):
        """
        Set whether or not this neuron has the indicated function.
        
        >>> neuron1.setHasFunction(Neuron.Function.SENSORY, True)
        
        The function argument should be one of the attributes of Neuron.Function.
        
        The hasFunction argument should indicate whether or not this neuron has the indicated function.
        """
        
        if hasFunction and function not in self._functions:
            self._functions.add(function)
            dispatcher.send(('set', 'functions'), self)
        elif not hasFunction and function in self._functions:
            self._functions.remove(function)
            dispatcher.send(('set', 'functions'), self)
    
    
    def hasFunction(self, function):
        """
        Return whether or not this neuron has the indicated function.
        
        >>> # Show all sensory neurons in red.
        >>> if neuron.hasFunction(Neuron.Function.SENSORY):
        ...     display.setVisibleColor(neuron, (1.0, 0.0, 0.0))
        
        The function argument should be one of the attributes of Neuron.Function.
        """
        
        return function in self._functions
    
