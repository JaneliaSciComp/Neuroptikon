from Object import Object
import xml.etree.ElementTree as ElementTree

class GapJunction(Object):
    
    # TODO: gap junctions can be directional
    
    def __init__(self, network, neurite1, neurite2, *args, **keywords):
        Object.__init__(self, network, *args, **keywords)
        self.neurites = set([neurite1, neurite2])
    
    
    @classmethod
    def fromXMLElement(cls, network, xmlElement):
        object = super(GapJunction, cls).fromXMLElement(network, xmlElement)
        neurite1Id = xmlElement.get('neurite1Id')
        neurite1 = network.objectWithId(neurite1Id)
        neurite2Id = xmlElement.get('neurite2Id')
        neurite2 = network.objectWithId(neurite2Id)
        if neurite1 is None:
            raise ValueError, gettext('Neurite with id "%s" does not exist') % (neurite1Id)
        elif neurite2 is None:
            raise ValueError, gettext('Neurite with id "%s" does not exist') % (neurite2Id)
        else:
            object.neurites = set([neurite1, neurite2])
            neurite1._gapJunctions.append(object)
            neurite2._gapJunctions.append(object)
            return object
    
    
    def toXMLElement(self, parentElement):
        gapJunctionElement = Object.toXMLElement(self, parentElement)
        neurites = list(self.neurites)
        gapJunctionElement.set('neurite1Id', str(neurites[0].networkId))
        gapJunctionElement.set('neurite2Id', str(neurites[1].networkId))
        return gapJunctionElement
