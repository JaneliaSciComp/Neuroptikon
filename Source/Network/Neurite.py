from Object import Object
from Region import Region
from Arborization import Arborization
from Synapse import Synapse
from GapJunction import GapJunction
from Muscle import Muscle
from Innervation import Innervation

import xml.etree.ElementTree as ElementTree


class Neurite(Object):
    
    def __init__(self, network, root, pathway = None, *args, **keywords):
        """
        Neurites represent projections from :class:`neurons <Network.Neuron.Neuron>` or other neurites.
        
        You create a neurite by messaging a :meth:`neuron <Network.Neuron.Neuron.createNeurite>` or :meth:`neurite <Network.Neurite.Neurite.createNeurite>`:
        
        >>> neurite1 = neuron.createNeurite(...)
        >>> neurite2 = neurite1.createNeurite(...)
        """
        
        Object.__init__(self, network, *args, **keywords)
        self.root = root
        self._neurites = []
        self.arborization = None
        self._synapses = []
        self._gapJunctions = []
        self._innervations = []
        self._pathway = pathway
        if pathway is not None:
            pathway.addNeurite(self)
        #self.isStretchReceptor ???
    
    
    @classmethod
    def _fromXMLElement(cls, network, xmlElement):
        object = super(Neurite, cls)._fromXMLElement(network, xmlElement)
        pathwayId = xmlElement.get('pathwayId')
        object.pathway = network.objectWithId(pathwayId)
        if pathwayId is not None and object.pathway is None:
            raise ValueError, gettext('Pathway with id "%s" does not exist') % (pathwayId)
        object._neurites = []
        for neuriteElement in xmlElement.findall('Neurite'):
            neurite = Neurite._fromXMLElement(network, neuriteElement)
            if neurite is None:
                raise ValueError, gettext('Could not create neurite')
            neurite.root = object
            object._neurites += [neurite]
            network.addObject(neurite)
        object.arborization = None
        object._synapses = []
        object._gapJunctions = []
        object._innervations = []
        return object
    
    
    def _toXMLElement(self, parentElement):
        neuriteElement = Object._toXMLElement(self, parentElement)
        if self._pathway is not None:
            neuriteElement.set('pathwayId', str(self._pathway.networkId))
        for neurite in self._neurites:
            neurite._toXMLElement(neuriteElement)
        return neuriteElement
    
    
    def _includeInScript(self, atTopLevel = False):
        # If this neurite is just a dummy neurite used to support a simple arborization, innervation, gap junction or synapse then it does not need to be created.
        from Neuron import Neuron
        connections = self.connections()
        if not self._needsScriptRef() and isinstance(self.root, Neuron) and len(connections) == 1:
            if isinstance(connections[0], (Arborization, Innervation, GapJunction, Synapse)):
                return False
        
        return Object._includeInScript(self)
    
    
    def _needsScriptRef(self):
        return self._pathway is not None or len(self.connections()) > 1 or Object._needsScriptRef(self)
    
    
    def _createScriptRef(self, scriptRefs):
        neuronRef = scriptRefs[self.neuron().networkId]
        if neuronRef in scriptRefs:
            neuriteCount = scriptRefs[neuronRef]
        else:
            neuriteCount = 0
        scriptRefs[neuronRef] = neuriteCount + 1
        scriptRefs[self.networkId] = neuronRef + '_neurite' + str(neuriteCount + 1)
        return scriptRefs[self.networkId]
    
    
    def _creationScriptCommand(self, scriptRefs):
        return scriptRefs[self.root.networkId] + '.createNeurite'
    
    
    def _creationScriptParams(self, scriptRefs):
        args, keywords = Object._creationScriptParams(self, scriptRefs)
        if self._pathway is not None:
            keywords['pathway'] = scriptRefs[pathway.networkId]
        return (args, keywords)
    
    
    def _creationScriptChildren(self):
        children = Object._creationScriptChildren(self)
        children += self._neurites
        return children
    
    
    def neuron(self):
        """
        Return the :class:`neuron <Network.Neuron.Neuron>` of which this neurite is part. 
        """
        
        parent = self.root
        while isinstance(parent, Neurite):
            parent = parent.root
        return parent
    
    
    def createNeurite(self, *args, **keywords):
        """
        Create and return a neurite object that projects from this neurite.
        """
        
        neurite = Neurite(self.network, self, *args, **keywords)
        self._neurites += [neurite]
        return neurite
    
    
    def neurites(self, recurse = True):
        """
        Return a list of all neurites projecting from this neurite.
        
        If recurse is True then the list will include all subsequently projecting neurites.
        
        If no neurites project from this neurite then an empty list will be returned.
        """
        
        neurites = []
        for neurite in self._neurites:
            neurites += [neurite]
            if recurse:
                neurites += neurite.neurites()
        return neurites
    
    
    def arborize(self, region, sendsOutput=None, receivesInput=None, *args, **keywordArgs):
        """
        Indicate that this neurite arborizes the given :class:`region <Network.Region.Region>`.
        
        The sendsOutput argument indicates whether the neurite sends information to the region: one of True, False or None (unknown).
        
        The receivesInput argument indicates whether the neurite receives information from the region, one of True, False or None (unknown).
        
        Returns the :class:`arborization <Network.Arborization.Arborization>` that is created.
        """
        
        # TODO: This will blow away any existing arborization.  Should a new sub-neurite be created?
        
        if region != None and not isinstance(region, Region):
            raise ValueError, 'The region argument to arborize() must be a region in the same network.'
        
        self.arborization = Arborization(self, region, sendsOutput, receivesInput, *args, **keywordArgs)
        region.arborizations += [self.arborization]
        self.network.addObject(self.arborization)
        return self.arborization
    
    
    def arborizations(self, recurse = True):
        """
        Return a list of all :class:`arborizations <Network.Arborization.Arborization>` extending from this neurite.
        
        If recurse is True then the list will include arborizations that extend from all subsequently projecting neurites.
        
        If this neurite does not arborize any regions then an empty list will be returned.
        """
        
        arborizations = []
        if self.arborization:
            arborizations += [self.arborization]
        elif recurse:
            for neurite in self._neurites:
                arborizations += neurite.arborizations()
        return arborizations
    
    
    def synapseOn(self, otherObject, activation = None, *args, **keywordArgs):
        """
        Create a chemical :class:`synapse <Netwok.Synapse.Synapse>` with the other object.
        
        The otherObject parameter can be a :class:`neuron <Network.Neuron.Neuron>`, a :class:`neurite <Network.Neurite.Neurite>` or list containing a combination of the two.
        
        The activation parameter must be one of 'excitatory', 'inhibitory' or None (i.e. unknown).
        
        The :class:`synapse <Network.Synapse.Synapse>` object that is created.
        """
        
        if isinstance(otherObject, (list, set, tuple)):
            otherObjects = otherObject
        else:
            otherObjects = [otherObject]
        
        from Neuron import Neuron
        
        otherNeurites = []
        for otherObject in otherObjects:
            if isinstance(otherObject, Neuron) and otherObject.network == self.network:
                otherNeurites += [otherObject.createNeurite()]
            elif isinstance(otherObject, Neurite) and otherObject.network == self.network:
                otherNeurites += [otherObject]
            else:
                raise ValueError, 'Synapses can only be made with neurons or neurites in the same network.'
        synapse = Synapse(self.network, self, otherNeurites, activation, *args, **keywordArgs)
        self._synapses += [synapse]
        for otherNeurite in otherNeurites:
            otherNeurite._synapses += [synapse]
        self.network.addObject(synapse)
        return synapse
    
    
    def synapses(self, recurse = True, includePre = True, includePost = True):
        """
        Return a list of all :class:`synapses <Network.Synapse.Synapse>` in which this neurite and optionally any sub-neurites are pre- or post-synaptic.
        
        If recurse is True then the list will include synapses from all subsequently projecting neurites.  If includePre is False then synapses where this neurite is pre-synaptic will be excluded.  If includePost is False then synapses where this neurite is post-synaptic will be excluded.
        
        If this neurite does not form a synapse with any other neurite then an empty list will be returned.
        """
        
        synapses = []
        for synapse in self._synapses:
            if (synapse.preSynapticNeurite == self and includePre) or (self in synapse.postSynapticNeurites and includePost):
                synapses += [synapse]
        if recurse:
            for neurite in self._neurites:
                synapses += neurite.synapses(includePre = includePre, includePost = includePost)
        return synapses


    def gapJunctionWith(self, otherObject, *args, **keywordArgs):
        """
        Create a gap junction with the other object.
        
        The otherObject argument should be a :class:`neuron <Network.Neuron.Neuron>` or :class:`neurite <Network.Neurite.Neurite>` from the same :class:`network <Network.Network.Network>`.
        
        Returns the :class:`gap junction <Network.GapJunction.GapJunction>` object that is created.
        """
        
        from Neuron import Neuron
        if isinstance(otherObject, Neuron) and otherObject.network == self.network:
            otherNeurite = otherObject.createNeurite()
        elif isinstance(otherObject, Neurite) and otherObject.network == self.network:
            otherNeurite = otherObject
        else:
            raise ValueError, 'Gap junctions can only be made with neurons or neurites in the same network.'
        gapJunction = GapJunction(self.network, self, otherNeurite, *args, **keywordArgs)
        self._gapJunctions += [gapJunction]
        otherNeurite._gapJunctions += [gapJunction]
        self.network.addObject(gapJunction)
        return gapJunction
    
    
    def gapJunctions(self, recurse = True):
        """
        Return a list of all `gap junctions <Network.GapJunction.GapJunction>` involving this neuron.
        
        If recurse is True then the list will include gap junctions from all subsequently projecting neurites.
        
        If this neurite does not form a gap junction with any other neurite then an empty list will be returned.
        """
        
        junctions = []
        junctions += self._gapJunctions
        if recurse:
            for subNeurite in self._neurites:
                junctions += subNeurite.gapJunctions()
        return junctions
    
    
    def setPathway(self, pathway):
        """
        Indicate the :class:`pathway <Network.Pathway.Pathway>` in which this neurite is bundled.
        """
        
        if pathway != None and not isinstance(pathway, Pathway):
            raise ValueError, 'The pathway argument to setPathway() must be a pathway in the same network or None.'
        
        if pathway != self._pathway:
            if self._pathway != None:
                self._pathway.removeNeurite(self)
            self._pathway = pathway
            if self._pathway != None:
                self._pathway.addNeurite(self)
    
    
    def pathway(self):
        """
        Return the :class:`pathway <Network.Pathway.Pathway>` in which this neurite is bundled.
        """
        
        return self._pathway
    
        
    def innervate(self, muscle, *args, **keywordArgs):
        """
        Indicate that this neurite innervates the given :class:`muscle <Network.Muscle.Muscle>`.
        
        Returns the :class:`innervation <Network.Innervation.Innervation>` object that is created.
        """
        
        if not isinstance(muscle, Muscle) or muscle.network != self.network:
            raise ValueError, 'The muscle argument passed to innervate() must be a muscle in the same network.'
        
        innervation = Innervation(self.network, self, muscle, *args, **keywordArgs)
        self._innervations += [innervation]
        muscle._innervations += [innervation]
        self.network.addObject(innervation)
        return innervation
    
    
    def innervations(self, recurse = True):
        """
        Return a list of all :class:`innervations <Network.Innervation.Innervation>` involving this neurite.
        
        If recurse is True then the list will include innervations from all subsequently projecting neurites.
        
        If this neurite does not innervate any muscles then an empty list will be returned.
        """
        
        innervations = list(self._innervations)
        if recurse:
            for subNeurite in self._neurites:
                innervations += subNeurite.innervations()
        return innervations


    def connections(self, recurse = True):
        """
        Return a list of all objects that connect to this neurite and optionally any projecting neurites.
        
        The list may contain any number of :class:`arborizations <Network.Arborization.Arborization>`, :class:`gap junctions <Network.GapJunction.GapJunction>`, :class:`innervations <Network.Innervation.Innervation>`, :class:`stimuli <Network.Stimulus.Stimulus>` or :class:`synapses <Network.Synapse.Synapse>`.
        """
        
        connections = Object.connections(self, recurse)
        connections += self.arborizations(recurse)
        connections += self.gapJunctions(recurse)
        connections += self.innervations(recurse)
        connections += self.synapses(recurse)
        return connections
    
    
    def inputs(self, recurse = True):
        """
        Return a list of all objects that send information into this neurite and optionally any projecting neurites.
        
        The list may contain any number of :class:`arborizations <Network.Arborization.Arborization>`, :class:`gap junctions <Network.GapJunction.GapJunction>`, :class:`stimuli <Network.Stimulus.Stimulus>` or :class:`synapses <Network.Synapse.Synapse>`.
        """
        
        inputs = Object.inputs(self, recurse)
        if self.arborization is not None and self.arborization.receivesInput:
            inputs += [self.arborization]
        inputs += self._gapJunctions
        inputs += self.synapses(includePre = False)
        if recurse:
            for neurite in self._neurites:
                inputs += neurite.inputs()
        return inputs
    
    
    def outputs(self, recurse = True):
        """
        Return a list of all objects that receive information from this neurite and optionally any projecting neurites.
        
        The list may contain any number of :class:`arborizations <Network.Arborization.Arborization>`, :class:`gap junctions <Network.GapJunction.GapJunction>`, :class:`innervations <Network.Innervation.Innervation>` or :class:`synapses <Network.Synapse.Synapse>`.
        """
        
        outputs = Object.outputs(self, recurse)
        if self.arborization is not None and self.arborization.sendsOutput:
            outputs += [self.arborization]
        outputs += self._gapJunctions
        outputs += self._innervations
        outputs += self.synapses(includePost = False)
        if recurse:
            for neurite in self._neurites:
                outputs += neurite.outputs()
        return outputs
