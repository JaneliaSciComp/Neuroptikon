from Object import Object
import xml.etree.ElementTree as ElementTree

class Innervation(Object):
    
    def __init__(self, network, neurite, muscle, *args, **keywords):
        """
        Innervations represent a :class:`neurite's <Network.Neurite.Neurite>` connection to a :class:`muscle <Network.Muscle.Muscle>`.
        
        Create an innervation by messaging a :meth:`neuron <Network.Neuron.Neuron.innervate>` or :meth:`neurite <Network.Neurite.Neurite.innervate>`:
        
        >>> neuron1 = network.createNeuron()
        >>> muscle1 = network.createMuscle()
        >>> innervation_1_1 = neuron1.innervate(muscle1)
        """
        
        Object.__init__(self, network, *args, **keywords)
        self.neurite = neurite
        self.muscle = muscle
    
    
    def defaultName(self):
        return str(self.neurite.neuron().name) + ' -> ' + str(self.muscle.name)
    
    
    @classmethod
    def _fromXMLElement(cls, network, xmlElement):
        object = super(Innervation, cls)._fromXMLElement(network, xmlElement)
        neuriteId = xmlElement.get('neuriteId')
        object.neurite = network.objectWithId(neuriteId)
        if object.neurite is None:
            raise ValueError, gettext('Neurite with id "%s" does not exist') % (neuriteId)
        object.neurite._innervations.append(object)
        muscleId = xmlElement.get('muscleId')
        object.muscle = network.objectWithId(muscleId)
        if object.muscle is None:
            raise ValueError, gettext('Muscle with id "%s" does not exist') % (muscleId)
        object.muscle._innervations.append(object)
        return object
    
    
    def _toXMLElement(self, parentElement):
        innervationElement = Object._toXMLElement(self, parentElement)
        innervationElement.set('neuriteId', str(self.neurite.networkId))
        innervationElement.set('muscleId', str(self.muscle.networkId))
        return innervationElement
    
    
    def _creationScriptCommand(self, scriptRefs):
        if self.neurite.networkId in scriptRefs:
            command = scriptRefs[self.neurite.networkId]
        else:
            command = scriptRefs[self.neurite.root.networkId]
        return command + '.innervate'
    
    
    def _creationScriptParams(self, scriptRefs):
        args, keywords = Object._creationScriptParams(self, scriptRefs)
        args.insert(0, scriptRefs[self.muscle.networkId])
        return (args, keywords)
    
    
    def connections(self, recurse = True):
        return Object.connections(self, recurse) + [self.neurite, self.muscle]
    
    
    def inputs(self, recurse = True):
        return Object.inputs(self, recurse) + [self.neurite]
    
    
    def outputs(self, recurse = True):
        return Object.outputs(self, recurse) + [self.muscle]
    