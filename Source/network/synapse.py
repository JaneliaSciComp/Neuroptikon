import neuroptikon
from neuro_object import NeuroObject
import xml.etree.ElementTree as ElementTree


class Synapse(NeuroObject):
    def __init__(self, network, preSynapticNeurite = None, postSynapticNeurites = [], activation = None, *args, **keywords):
        """
        A Synapse object represents a chemical synapse between a single pre-synaptic neurite and one or more post-synaptic neurites.
        
        Instances of this class are created by using the synapseOn method of :meth:`Neuron <Network.Neuron.Neuron.synapseOn>` and :meth:`Neurite <Network.Neurite.Neurite.synapseOn>` objects. 
        
        A synapse's activation attribute should be one of None (meaning unknown), 'excitatory' or 'inhibitory'. 
        
        >>> neuron1.synapseOn(neuron2, activation = 'excitatory')
        """
        
        NeuroObject.__init__(self, network, *args, **keywords)
        self.preSynapticNeurite = preSynapticNeurite
        self.postSynapticNeurites = postSynapticNeurites
        self.activation = activation
    
    
    def defaultName(self):
        names = []
        for postNeurite in self.postSynapticNeurites:
            names += [str(postNeurite.neuron().name)]
        names.sort()
        return str(self.preSynapticNeurite.neuron().name) + ' -> ' + ', '.join(names)
    
    
    @classmethod
    def _fromXMLElement(cls, network, xmlElement):
        synapse = super(Synapse, cls)._fromXMLElement(network, xmlElement)
        preSynapticNeuriteId = xmlElement.findtext('PreSynapticNeuriteId')
        if preSynapticNeuriteId is None:
            preSynapticNeuriteId = xmlElement.findtext('preSynapticNeuriteId')
        synapse.preSynapticNeurite = network.objectWithId(preSynapticNeuriteId)
        if synapse.preSynapticNeurite is None:
            raise ValueError, gettext('Neurite with id "%s" does not exist') % (preSynapticNeuriteId)
        synapse.preSynapticNeurite._synapses.append(synapse)
        synapse.postSynapticNeurites = []
        if xmlElement.find('PreSynapticNeuriteId') is not None:
            postSynapticNeuriteIds = xmlElement.findall('PostSynapticNeuriteId')
        else:
            postSynapticNeuriteIds = xmlElement.findall('postSynapticNeuriteId')
        for neuriteElement in postSynapticNeuriteIds:
            neuriteId = neuriteElement.text
            neurite = network.objectWithId(neuriteId)
            if neurite is None:
                raise ValueError, gettext('Neurite with id "%s" does not exist') % (neuriteId)
            synapse.postSynapticNeurites.append(neurite)
            neurite._synapses.append(synapse)
        synapse.activation = xmlElement.findtext('Activation')
        if synapse.activation is None:
            synapse.activation = xmlElement.findtext('activation')
        return synapse
    
    
    def _toXMLElement(self, parentElement):
        synapseElement = NeuroObject._toXMLElement(self, parentElement)
        ElementTree.SubElement(synapseElement, 'PreSynapticNeuriteId').text = str(self.preSynapticNeurite.networkId)
        for neurite in self.postSynapticNeurites:
            ElementTree.SubElement(synapseElement, 'PostSynapticNeuriteId').text = str(neurite.networkId)
        if self.activation is not None:
            ElementTree.SubElement(synapseElement, 'Activation').text = self.activation
        return synapseElement
    
    
    def _creationScriptCommand(self, scriptRefs):
        if self.preSynapticNeurite.networkId in scriptRefs:
            return scriptRefs[self.preSynapticNeurite.networkId]+ '.synapseOn'
        else:
            return scriptRefs[self.preSynapticNeurite.root.networkId]+ '.synapseOn'
    
    
    def _creationScriptParams(self, scriptRefs):
        args, keywords = NeuroObject._creationScriptParams(self, scriptRefs)
        postRefs = []
        for postNeurite in self.postSynapticNeurites:
            if postNeurite.networkId in scriptRefs:
                postRefs.append(scriptRefs[postNeurite.networkId])
            else:
                postRefs.append(scriptRefs[postNeurite.root.networkId])
        if len(postRefs) == 1:
            args.insert(0, postRefs[0])
        else:
            args.insert(0, '(' + ', '.join(postRefs) + ')')
        return (args, keywords)
    
    
    def connections(self, recurse = True):
        return NeuroObject.connections(self, recurse) + [self.preSynapticNeurite] + self.postSynapticNeurites
    
    
    def inputs(self, recurse = True):
        return NeuroObject.inputs(self, recurse) + [self.preSynapticNeurite]
    
    
    def outputs(self, recurse = True):
        return NeuroObject.outputs(self, recurse) + self.postSynapticNeurites
    
    
    def disconnectFromNetwork(self):
        self.preSynapticNeurite._synapses.remove(self)
        for neurite in self.postSynapticNeurites:
            neurite._synapses.remove(self)
    
    
    def defaultVisualizationParams(self):
        params = NeuroObject.defaultVisualizationParams(self)
        shapeClasses = neuroptikon.scriptLocals()['shapes']
        params['shape'] = shapeClasses['Line']
        params['color'] = (1.0, 0.0, 0.0) if self.activation == 'inhibitory' else (0.0, 0.0, 1.0)
        if any(self.postSynapticNeurites):
            params['pathEndPoints'] = (self.preSynapticNeurite.neuron(), self.postSynapticNeurites[0].neuron())
            params['flowTo'] = True
        return params
    