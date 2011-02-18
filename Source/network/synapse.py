#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

import neuroptikon
from neuro_object import NeuroObject
try:
    import xml.etree.cElementTree as ElementTree
except ImportError:
    import xml.etree.ElementTree as ElementTree


class Synapse(NeuroObject):
    def __init__(self, network, preSynapticNeurite = None, postSynapticPartners = [], activation = None, *args, **keywords):
        """
        A Synapse object represents a chemical synapse between a single pre-synaptic neurite and one or more post-synaptic neurites.
        
        Instances of this class are created by using the synapseOn method of :meth:`Neuron <Network.Neuron.Neuron.synapseOn>` and :meth:`Neurite <Network.Neurite.Neurite.synapseOn>` objects. 
        
        A synapse's activation attribute should be one of None (meaning unknown), 'excitatory' or 'inhibitory'. 
        
        >>> neuron1.synapseOn(neuron2, activation = 'excitatory')
        """
        
        NeuroObject.__init__(self, network, *args, **keywords)
        self.preSynapticNeurite = preSynapticNeurite
        self.postSynapticPartners = postSynapticPartners
        self.activation = activation
    
    
    def defaultName(self):
        names = []
        for postPartner in self.postSynapticPartners:
            if type(postPartner).__name__ == 'Neurite':
                postPartner = postPartner.neuron()
            names += [str(postPartner.name)]
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
        synapse.postSynapticPartners = []
        if xmlElement.find('PostSynapticPartnerId') is not None:
            postSynapticPartnerIds = xmlElement.findall('PostSynapticPartnerId')
        elif xmlElement.find('PostSynapticNeuriteId') is not None:
            postSynapticPartnerIds = xmlElement.findall('PostSynapticNeuriteId')
        else:
            postSynapticPartnerIds = xmlElement.findall('postSynapticNeuriteId')
        for partnerElement in postSynapticPartnerIds:
            partnerId = partnerElement.text
            partner = network.objectWithId(partnerId)
            if partner is None:
                raise ValueError, gettext('Neuron/neurite with id "%s" does not exist') % (partnerId)
            synapse.postSynapticPartners.append(partner)
            partner._synapses.append(synapse)
        synapse.activation = xmlElement.findtext('Activation')
        if synapse.activation is None:
            synapse.activation = xmlElement.findtext('activation')
        return synapse
    
    
    def _toXMLElement(self, parentElement):
        synapseElement = NeuroObject._toXMLElement(self, parentElement)
        ElementTree.SubElement(synapseElement, 'PreSynapticNeuriteId').text = str(self.preSynapticNeurite.networkId)
        for partner in self.postSynapticPartners:
            ElementTree.SubElement(synapseElement, 'PostSynapticPartnerId').text = str(partner.networkId)
        if self.activation is not None:
            ElementTree.SubElement(synapseElement, 'Activation').text = self.activation
        return synapseElement
    
    
    def _creationScriptMethod(self, scriptRefs):
        if self.preSynapticNeurite.networkId in scriptRefs:
            return scriptRefs[self.preSynapticNeurite.networkId]+ '.synapseOn'
        else:
            return scriptRefs[self.preSynapticNeurite.root.networkId]+ '.synapseOn'
    
    
    def _creationScriptParams(self, scriptRefs):
        args, keywords = NeuroObject._creationScriptParams(self, scriptRefs)
        postRefs = []
        for postPartner in self.postSynapticPartners:
            if postPartner in scriptRefs:
                postRefs.append(scriptRefs[postPartner.networkId])
            else:
                postRefs.append(scriptRefs[postPartner.root.networkId])
        if len(postRefs) == 1:
            args.insert(0, postRefs[0])
        else:
            args.insert(0, '(' + ', '.join(postRefs) + ')')
        return (args, keywords)
    
    
    def connections(self, recurse = True):
        return NeuroObject.connections(self, recurse) + [self.preSynapticNeurite] + self.postSynapticPartners
    
    
    def inputs(self, recurse = True):
        return NeuroObject.inputs(self, recurse) + [self.preSynapticNeurite]
    
    
    def outputs(self, recurse = True):
        return NeuroObject.outputs(self, recurse) + self.postSynapticPartners
    
    
    def disconnectFromNetwork(self):
        self.preSynapticNeurite._synapses.remove(self)
        for partner in self.postSynapticPartners:
            partner._synapses.remove(self)
    
    
    @classmethod
    def _defaultVisualizationParams(cls):
        params = NeuroObject._defaultVisualizationParams()
        params['shape'] = 'Line'
        params['color'] = (0.0, 0.0, 1.0)
        return params
    
    
    def defaultVisualizationParams(self):
        params = self.__class__._defaultVisualizationParams()
        params['color'] = (1.0, 0.0, 0.0) if self.activation == 'inhibitory' else (0.0, 0.0, 1.0)
        if any(self.postSynapticPartners):
            postSynapticObject = self.postSynapticPartners[0]
            if type(postSynapticObject).__name__ == 'Neurite':
                postSynapticObject = postSynapticObject.neuron()
            params['pathEndPoints'] = (self.preSynapticNeurite.neuron(), postSynapticObject)
            params['pathIsFixed'] = None
            params['flowTo'] = True
        return params
    