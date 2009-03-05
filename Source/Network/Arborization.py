from Object import Object
import xml.etree.ElementTree as ElementTree


class Arborization(Object):
    
    def __init__(self, neurite, region, sendsOutput=None, receivesInput=None, *args, **keywords):
        Object.__init__(self, neurite.network, *args, **keywords)
        self.neurite = neurite
        self.region = region
        self.sendsOutput = sendsOutput      # does the neurite send output to the arbor?      None = unknown
        self.receivesInput = receivesInput  # does the neurite receive input from the arbor?  None = unknown
    
    
    @classmethod
    def fromXMLElement(cls, network, xmlElement):
        object = super(Arborization, cls).fromXMLElement(network, xmlElement)
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
    
    
    def toXMLElement(self, parentElement):
        arborizationElement = Object.toXMLElement(self, parentElement)
        arborizationElement.set('neuriteId', str(self.neurite.networkId))
        arborizationElement.set('regionId', str(self.region.networkId))
        if self.sendsOutput is None:
            arborizationElement.set('sends', 'unknown')
        elif self.sendsOutput:
            arborizationElement.set('sends', 'true')
        else:
            arborizationElement.set('sends', 'false')
        if self.receivesInput is None:
            arborizationElement.set('receives', 'unknown')
        elif self.receivesInput:
            arborizationElement.set('receives', 'true')
        else:
            arborizationElement.set('receives', 'false')
        return arborizationElement
