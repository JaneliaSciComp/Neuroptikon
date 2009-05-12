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
        preSynapticNeuriteId = xmlElement.findtext('PreSynapticNeuriteId')
        if preSynapticNeuriteId is None:
            preSynapticNeuriteId = xmlElement.findtext('preSynapticNeuriteId')
        object.preSynapticNeurite = network.objectWithId(preSynapticNeuriteId)
        if object.preSynapticNeurite is None:
            raise ValueError, gettext('Neurite with id "%s" does not exist') % (preSynapticNeuriteId)
        object.preSynapticNeurite.synapses.append(object)
        object.postSynapticNeurites = []
        if xmlElement.find('PreSynapticNeuriteId') is not None:
            postSynapticNeuriteIds = xmlElement.findall('PostSynapticNeuriteId')
        else:
            postSynapticNeuriteIds = xmlElement.findall('postSynapticNeuriteId')
        for neuriteElement in postSynapticNeuriteIds:
            neuriteId = neuriteElement.text
            neurite = network.objectWithId(neuriteId)
            if neurite is None:
                raise ValueError, gettext('Neurite with id "%s" does not exist') % (neuriteId)
            object.postSynapticNeurites.append(neurite)
            neurite.synapses.append(object)
        object.activation = xmlElement.findtext('Activation')
        if object.activation is None:
            object.activation = xmlElement.findtext('activation')
        return object
    
    
    def toXMLElement(self, parentElement):
        synapseElement = Object.toXMLElement(self, parentElement)
        ElementTree.SubElement(synapseElement, 'PreSynapticNeuriteId').text = str(self.preSynapticNeurite.networkId)
        for neurite in self.postSynapticNeurites:
            ElementTree.SubElement(synapseElement, 'PostSynapticNeuriteId').text = str(neurite.networkId)
        if self.activation is not None:
            ElementTree.SubElement(synapseElement, 'Activation').text = self.activation
        return synapseElement
    
    
    def creationScriptCommand(self, scriptRefs):
        if self.preSynapticNeurite.networkId in scriptRefs:
            return scriptRefs[self.preSynapticNeurite.networkId]+ '.synapseOn'
        else:
            return scriptRefs[self.preSynapticNeurite.root.networkId]+ '.synapseOn'
    
    
    def creationScriptParams(self, scriptRefs):
        args, keywords = Object.creationScriptParams(self, scriptRefs)
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
