import Neuroptikon
from Object import Object

class Stimulus(Object):
    
    def __init__(self, network, target = None, modality = None, *args, **keywords):
        """
        Stimulus objects represent external stimulation of objects in the network.
        
        Stimulii are created by calling the :meth:`stimulate <Network.Object.Object.stimulate>` method on an object in the network.  The modality argument must be a :class:`modality <Library.Modality.Modality>` from the library or None to indicate unknown modality.
        
        >>> stimulus = neuron1.stimulate(modality = library.modality('light'))
        """
        
        if target is None:
            raise ValueError, gettext('A stimulus must have a target')
        
        if not keywords.has_key('name') or keywords['name'] is None:
            keywords['name'] = modality.name
            
        Object.__init__(self, network, *args, **keywords)
        self.target = target
        self.modality = modality
    
    
    def defaultName(self):
        return self.modality.identifier + ' -> ' + str(self.target.name)
    
    
    @classmethod
    def _fromXMLElement(cls, network, xmlElement):
        object = super(Stimulus, cls)._fromXMLElement(network, xmlElement)
        targetId = xmlElement.get('targetId')
        object.target = network.objectWithId(targetId)
        if object.target is None:
            raise ValueError, gettext('Object with id "%s" does not exist') % (targetId)
        object.target.stimuli.append(object)
        modalityId = xmlElement.get('modality')
        object.modality = Neuroptikon.library.modality(modalityId)
        if object.modality is None:
            raise ValueError, gettext('Modality "%s" does not exist') % (modalityId)
        return object
    
    
    def _toXMLElement(self, parentElement):
        stimulusElement = Object._toXMLElement(self, parentElement)
        stimulusElement.set('targetId', str(self.target.networkId))
        stimulusElement.set('modality', self.modality.identifier)
        return stimulusElement
    
    
    def _creationScriptCommand(self, scriptRefs):
        return scriptRefs[self.target.networkId] + '.stimulate'
    
    
    def _creationScriptParams(self, scriptRefs):
        args, keywords = Object._creationScriptParams(self, scriptRefs)
        if self.modality is not None:
            keywords['modality'] = 'library.modality(\'' + self.modality.identifier.replace('\\', '\\\\').replace('\'', '\\\'') + '\')'
        return (args, keywords)
    
    
    def connections(self, recurse = True):
        return [self.target]
    
    
    def outputs(self, recurse = True):
        return [self.target]
    
    
