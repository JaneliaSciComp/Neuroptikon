import Neuroptikon
from neuro_object import NeuroObject


class Innervation(NeuroObject):
    
    def __init__(self, network, neurite, muscle, *args, **keywords):
        """
        Innervations represent a :class:`neurite's <Network.Neurite.Neurite>` connection to a :class:`muscle <Network.Muscle.Muscle>`.
        
        Create an innervation by messaging a :meth:`neuron <Network.Neuron.Neuron.innervate>` or :meth:`neurite <Network.Neurite.Neurite.innervate>`:
        
        >>> neuron1 = network.createNeuron()
        >>> muscle1 = network.createMuscle()
        >>> innervation_1_1 = neuron1.innervate(muscle1)
        """
        
        NeuroObject.__init__(self, network, *args, **keywords)
        self.neurite = neurite
        self.muscle = muscle
    
    
    def defaultName(self):
        return str(self.neurite.neuron().name) + ' -> ' + str(self.muscle.name)
    
    
    @classmethod
    def _fromXMLElement(cls, network, xmlElement):
        innervation = super(Innervation, cls)._fromXMLElement(network, xmlElement)
        neuriteId = xmlElement.get('neuriteId')
        innervation.neurite = network.objectWithId(neuriteId)
        if innervation.neurite is None:
            raise ValueError, gettext('Neurite with id "%s" does not exist') % (neuriteId)
        innervation.neurite._innervations.append(innervation)
        muscleId = xmlElement.get('muscleId')
        innervation.muscle = network.objectWithId(muscleId)
        if innervation.muscle is None:
            raise ValueError, gettext('Muscle with id "%s" does not exist') % (muscleId)
        innervation.muscle._innervations.append(innervation)
        return innervation
    
    
    def _toXMLElement(self, parentElement):
        innervationElement = NeuroObject._toXMLElement(self, parentElement)
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
        args, keywords = NeuroObject._creationScriptParams(self, scriptRefs)
        args.insert(0, scriptRefs[self.muscle.networkId])
        return (args, keywords)
    
    
    def connections(self, recurse = True):
        return NeuroObject.connections(self, recurse) + [self.neurite, self.muscle]
    
    
    def inputs(self, recurse = True):
        return NeuroObject.inputs(self, recurse) + [self.neurite]
    
    
    def outputs(self, recurse = True):
        return NeuroObject.outputs(self, recurse) + [self.muscle]
    
    
    def defaultVisualizationParams(self):
        params = NeuroObject.defaultVisualizationParams(self)
        shapeClasses = Neuroptikon.scriptLocals()['shapes']
        params['shape'] = shapeClasses['Line']
        params['color'] = (0.55, 0.35, 0.25)
        params['pathEndPoints'] = (self.neurite.neuron(), self.muscle)
        params['flowTo'] = True
        return params
    