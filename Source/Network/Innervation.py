from Object import Object
import xml.etree.ElementTree as ElementTree

class Innervation(Object):
    
    def __init__(self, network, neurite, muscle, *args, **keywords):
        Object.__init__(self, network, *args, **keywords)
        self.neurite = neurite
        self.muscle = muscle
    
    
    @classmethod
    def fromXMLElement(cls, network, xmlElement):
        object = super(Innervation, cls).fromXMLElement(network, xmlElement)
        neuriteId = xmlElement.get('neuriteId')
        object.neurite = network.objectWithId(neuriteId)
        if object.neurite is None:
            raise ValueError, gettext('Neurite with id "%s" does not exist') % (neuriteId)
        object.neurite._innervations.append(object)
        muscleId = xmlElement.get('muscleId')
        object.muscle = network.objectWithId(muscleId)
        if object.muscle is None:
                raise ValueError, gettext('Muscle with id "%s" does not exist') % (muscleId)
        object.muscle.innervations.append(object)
        return object
    
    
    def toXMLElement(self, parentElement):
        innervationElement = Object.toXMLElement(self, parentElement)
        innervationElement.set('neuriteId', str(self.neurite.networkId))
        innervationElement.set('muscleId', str(self.muscle.networkId))
        return innervationElement
