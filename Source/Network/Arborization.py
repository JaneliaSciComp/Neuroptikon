from Object import Object
import xml.etree.ElementTree as ElementTree


class Arborization(Object):
    
    def __init__(self, neurite, region, sendsOutput=None, receivesInput=None, *args, **keywords):
        """
        Arborizations represent a neurite's arborization within a region.
        
        You create an arborization by messaging a :meth:`neuron <Network.Neuron.Neuron.arborize>` or :meth:`neurite <Network.Neurite.Neurite.arborize>`:
        
        >>> neuron1 = network.createNeuron()
        >>> region1 = network.createRegion()
        >>> arborization_1_1 = neuron1.arborize(region1)
        """
        
        Object.__init__(self, neurite.network, *args, **keywords)
        self.neurite = neurite
        self.region = region
        self.sendsOutput = sendsOutput      # does the neurite send output to the arbor?      None = unknown
        self.receivesInput = receivesInput  # does the neurite receive input from the arbor?  None = unknown
    
    
    def defaultName(self):
        return str(self.neurite.neuron().name) + ' -> ' + str(self.region.name)
    
    
    @classmethod
    def _fromXMLElement(cls, network, xmlElement):
        object = super(Arborization, cls)._fromXMLElement(network, xmlElement)
        neuriteId = xmlElement.get('neuriteId')
        object.neurite = network.objectWithId(neuriteId)
        if object.neurite is None:
            raise ValueError, gettext('Neurite with id "%s" does not exist') % (neuriteId)
        object.neurite.arborization = object
        regionId = xmlElement.get('regionId')
        object.region = network.objectWithId(regionId)
        if object.region is None:
            raise ValueError, gettext('Region with id "%s" does not exist') % (regionId)
        object.region.arborizations.append(object)
        sends = xmlElement.get('sends')
        if sends == 'true':
            object.sendsOutput = True
        elif sends == 'false':
            object.sendsOutput = False
        else:
            object.sendsOutput = None
        receives = xmlElement.get('receives')
        if receives == 'true':
            object.receivesInput = True
        elif receives == 'false':
            object.receivesInput = False
        else:
            object.receivesInput = None
        return object
    
    
    def _toXMLElement(self, parentElement):
        arborizationElement = Object._toXMLElement(self, parentElement)
        arborizationElement.set('neuriteId', str(self.neurite.networkId))
        arborizationElement.set('regionId', str(self.region.networkId))
        if self.sendsOutput is not None:
            arborizationElement.set('sends', 'true' if self.sendsOutput else 'false')
        if self.receivesInput is not None:
            arborizationElement.set('receives', 'true' if self.receivesInput else 'false')
        return arborizationElement
    
    
    def _creationScriptCommand(self, scriptRefs):
        if self.neurite.networkId in scriptRefs:
            command = scriptRefs[self.neurite.networkId]
        else:
            command = scriptRefs[self.neurite.root.networkId]
        return command + '.arborize'
    
    
    def _creationScriptParams(self, scriptRefs):
        args, keywords = Object._creationScriptParams(self, scriptRefs)
        args.insert(0, scriptRefs[self.region.networkId])
        if self.sendsOutput is not None:
            keywords['sendsOutput'] = str(self.sendsOutput)
        if self.receivesInput is not None:
            keywords['receivesInput'] = str(self.receivesInput)
        return (args, keywords)
    
    
    def connections(self, recurse = True):
        return Object.connections(self, recurse) + [self.neurite, self.region]
    
    
    def inputs(self, recurse = True):
        inputs = Object.inputs(self, recurse)
        if self.sendsOutput:
            inputs += [self.neurite]
        if self.receivesInput:
            inputs += [self.region]
        return inputs
    
    
    def outputs(self, recurse = True):
        outputs = Object.outputs(self, recurse)
        if self.sendsOutput:
            outputs += [self.region]
        if self.receivesInput:
            outputs += [self.neurite]
        return outputs
    