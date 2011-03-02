#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

from object import Object


class NeuroObject(Object):
    
    def __init__(self, *args, **keywordArgs):
        """
        The Object class is the base-class for every object in a :class:`network <Network.Network.Network>`.
        
        Any number of user-defined attributes or stimuli can be added to an object.  The connectivity of objects can also be investigated.
        """
        
        Object.__init__(self, *args, **keywordArgs)
        
        self.stimuli = []
    
    
    @classmethod
    def _fromXMLElement(cls, network, xmlElement):
        neuroObject = super(NeuroObject, cls)._fromXMLElement(network, xmlElement)
        
        neuroObject.stimuli = []
        
        return neuroObject
    
    
    def _needsScriptRef(self):
        return any(self.stimuli) or Object._needsScriptRef(self)
    
    
    def connections(self, recurse = True):  # pylint: disable=W0613
        """
        Return a list of the objects that connect to this object.
        """
        
        return Object.connections(self, recurse) + self.stimuli
    
    
    def inputs(self, recurse = True):  # pylint: disable=W0613
        """
        Return a list of objects that send information into this object.
        """
        
        return Object.inputs(self, recurse) + (self.stimuli)
    
    
    def dependentObjects(self):
        return Object.dependentObjects(self) + self.stimuli
    
    
    def disconnectFromNetwork(self):
        for stimulus in self.stimuli:
            stimulus.target = None
    
    
    def stimulate(self, modality = None, *args, **keywordArgs):
        """
        Add a :class:`stimulus <Network.Stimulus.Stimulus>` to this object with the given :class:`modality <Library.Modality.Modality>`.
        
        >>> neuron1.stimulate(library.modality('light')) 
        
        Returns the stimulus object that is created.
        """
        
        from stimulus import Stimulus
        from library.modality import Modality
        
        if modality != None and not isinstance(modality, Modality):
            raise TypeError, 'The modality argument passed to stimulate() must be a value obtained from the library or None.'
        
        stimulus = Stimulus(self.network, target = self, modality = modality, *args, **keywordArgs)
        self.stimuli.append(stimulus)
        self.network.addObject(stimulus)
        return stimulus
    
    
    @classmethod
    def _defaultVisualizationParams(cls):
        params = Object._defaultVisualizationParams()
        params['color'] = (0.9, 0.85, 0.75)
        return params
