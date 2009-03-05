from Object import Object
import xml.etree.ElementTree as ElementTree


class Synapse(Object):
    
    def __init__(self, network, preSynapticNeurite = None, postSynapticNeurites = [], activation = None, *args, **keywords):
        Object.__init__(self, network, *args, **keywords)
        self.preSynapticNeurite = preSynapticNeurite
        self.postSynapticNeurites = postSynapticNeurites
        self.activation = activation
    
    
    @classmethod
    def fromXMLElement(cls, network, xmlElement):
        object = super(Synapse, cls).fromXMLElement(network, xmlElement)
        object.preSynapticNeurite = network.objectWithId(xmlElement.findtext('preSynapticNeuriteId'))
        if object.preSynapticNeurite is None:
            raise ValueError, gettext('Neurite with id "%s" does not exist') % (xmlElement.findtext('preSynapticNeuriteId'))
        object.preSynapticNeurite.synapses.append(object)
        object.postSynapticNeurites = []
        for neuriteElement in xmlElement.findall('postSynapticNeuriteId'):
            neuriteId = neuriteElement.text
            neurite = network.objectWithId(neuriteId)
            if neurite is None:
                raise ValueError, gettext('Neurite with id "%s" does not exist') % (neuriteId)
            object.postSynapticNeurites.append(neurite)
            neurite.synapses.append(object)
        object.activation = xmlElement.findtext('activation')
        return object
    
    
    def toXMLElement(self, parentElement):
        synapseElement = Object.toXMLElement(self, parentElement)
        ElementTree.SubElement(synapseElement, 'preSynapticNeuriteId').text = str(self.preSynapticNeurite.networkId)
        for neurite in self.postSynapticNeurites:
            ElementTree.SubElement(synapseElement, 'postSynapticNeuriteId').text = str(neurite.networkId)
        if self.activation is not None:
            ElementTree.SubElement(synapseElement, 'activation').text = self.activation
        return synapseElement
