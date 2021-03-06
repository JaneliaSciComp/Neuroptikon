#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

import neuroptikon
from neuro_object import NeuroObject

class Stimulus(NeuroObject):
    
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
            
        NeuroObject.__init__(self, network, *args, **keywords)
        self.target = target
        self.modality = modality
    
    
    def defaultName(self):
        return self.modality.identifier + ' -> ' + str(self.target.name)
    
    
    @classmethod
    def _fromXMLElement(cls, network, xmlElement):
        stimulus = super(Stimulus, cls)._fromXMLElement(network, xmlElement)
        targetId = xmlElement.get('targetId')
        stimulus.target = network.objectWithId(targetId)
        if stimulus.target is None:
            raise ValueError, gettext('Object with id "%s" does not exist') % (targetId)
        stimulus.target.stimuli.append(stimulus)
        modalityId = xmlElement.get('modality')
        stimulus.modality = neuroptikon.library.modality(modalityId)
        if stimulus.modality is None:
            raise ValueError, gettext('Modality "%s" does not exist') % (modalityId)
        return stimulus
    
    
    def _toXMLElement(self, parentElement):
        stimulusElement = NeuroObject._toXMLElement(self, parentElement)
        stimulusElement.set('targetId', str(self.target.networkId))
        stimulusElement.set('modality', self.modality.identifier)
        return stimulusElement
    
    
    def _creationScriptMethod(self, scriptRefs):
        return scriptRefs[self.target.networkId] + '.stimulate'
    
    
    def _creationScriptParams(self, scriptRefs):
        args, keywords = NeuroObject._creationScriptParams(self, scriptRefs)
        if self.modality is not None:
            keywords['modality'] = 'library.modality(\'' + self.modality.identifier.replace('\\', '\\\\').replace('\'', '\\\'') + '\')'
        return (args, keywords)
    
    
    def connections(self, recurse = True):
        return [self.target]
    
    
    def outputs(self, recurse = True):
        return [self.target]
    
    
    def disconnectFromNetwork(self):
        self.target.stimuli.remove(self)
    
    
    @classmethod
    def _defaultVisualizationParams(cls):
        params = NeuroObject._defaultVisualizationParams()
        params['shape'] = 'Cone'
        params['size'] = (.02, .02, .02) # so the label is in front (hacky...)
        params['color'] = (0.5, 0.5, 0.5)
        params['weight'] = 5.0
        params['pathIsFixed'] = True
        return params
    
    
    def defaultVisualizationParams(self):
        params = self.__class__._defaultVisualizationParams()
        params['label'] = self.abbreviation or self.name
        return params
