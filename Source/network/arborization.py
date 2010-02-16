#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

import neuroptikon
from neuro_object import NeuroObject


class Arborization(NeuroObject):
    
    def __init__(self, neurite, region, sendsOutput=None, receivesInput=None, *args, **keywords):
        """
        Arborizations represent a neurite's arborization within a region.
        
        You create an arborization by messaging a :meth:`neuron <Network.Neuron.Neuron.arborize>` or :meth:`neurite <Network.Neurite.Neurite.arborize>`:
        
        >>> neuron1 = network.createNeuron()
        >>> region1 = network.createRegion()
        >>> arborization_1_1 = neuron1.arborize(region1)
        """
        
        NeuroObject.__init__(self, neurite.network, *args, **keywords)
        self.neurite = neurite
        self.region = region
        self.sendsOutput = sendsOutput      # does the neurite send output to the arbor?      None = unknown
        self.receivesInput = receivesInput  # does the neurite receive input from the arbor?  None = unknown
    
    
    def defaultName(self):
        return str(self.neurite.neuron().name) + ' -> ' + str(self.region.name)
    
    
    @classmethod
    def _fromXMLElement(cls, network, xmlElement):
        arborization = super(Arborization, cls)._fromXMLElement(network, xmlElement)
        neuriteId = xmlElement.get('neuriteId')
        arborization.neurite = network.objectWithId(neuriteId)
        if arborization.neurite is None:
            raise ValueError, gettext('Neurite with id "%s" does not exist') % (neuriteId)
        arborization.neurite.arborization = arborization
        regionId = xmlElement.get('regionId')
        arborization.region = network.objectWithId(regionId)
        if arborization.region is None:
            raise ValueError, gettext('Region with id "%s" does not exist') % (regionId)
        arborization.region.arborizations.append(arborization)
        sends = xmlElement.get('sends')
        if sends == 'true':
            arborization.sendsOutput = True
        elif sends == 'false':
            arborization.sendsOutput = False
        else:
            arborization.sendsOutput = None
        receives = xmlElement.get('receives')
        if receives == 'true':
            arborization.receivesInput = True
        elif receives == 'false':
            arborization.receivesInput = False
        else:
            arborization.receivesInput = None
        return arborization
    
    
    def _toXMLElement(self, parentElement):
        arborizationElement = NeuroObject._toXMLElement(self, parentElement)
        arborizationElement.set('neuriteId', str(self.neurite.networkId))
        arborizationElement.set('regionId', str(self.region.networkId))
        if self.sendsOutput is not None:
            arborizationElement.set('sends', 'true' if self.sendsOutput else 'false')
        if self.receivesInput is not None:
            arborizationElement.set('receives', 'true' if self.receivesInput else 'false')
        return arborizationElement
    
    
    def _creationScriptMethod(self, scriptRefs):
        if self.neurite.networkId in scriptRefs:
            command = scriptRefs[self.neurite.networkId]
        else:
            command = scriptRefs[self.neurite.root.networkId]
        return command + '.arborize'
    
    
    def _creationScriptParams(self, scriptRefs):
        args, keywords = NeuroObject._creationScriptParams(self, scriptRefs)
        args.insert(0, scriptRefs[self.region.networkId])
        if self.sendsOutput is not None:
            keywords['sendsOutput'] = str(self.sendsOutput)
        if self.receivesInput is not None:
            keywords['receivesInput'] = str(self.receivesInput)
        return (args, keywords)
    
    
    def connections(self, recurse = True):
        return NeuroObject.connections(self, recurse) + [self.neurite, self.region]
    
    
    def inputs(self, recurse = True):
        inputs = NeuroObject.inputs(self, recurse)
        if self.sendsOutput:
            inputs += [self.neurite]
        if self.receivesInput:
            inputs += [self.region]
        return inputs
    
    
    def outputs(self, recurse = True):
        outputs = NeuroObject.outputs(self, recurse)
        if self.sendsOutput:
            outputs += [self.region]
        if self.receivesInput:
            outputs += [self.neurite]
        return outputs
    
    
    def disconnectFromNetwork(self):
        self.neurite.arborization = None
        self.region.arborizations.remove(self)
    
    
    @classmethod
    def _defaultVisualizationParams(cls):
        params = NeuroObject._defaultVisualizationParams()
        params['shape'] = 'Line'
        params['color'] = (0.0, 0.0, 0.0)
        params['pathIsFixed'] = None
        return params
    
    
    def defaultVisualizationParams(self):
        params = self.__class__._defaultVisualizationParams()
        params['pathEndPoints'] = (self.neurite.neuron(), self.region)
        params['flowTo'] = self.sendsOutput
        params['flowFrom'] = self.receivesInput
        return params
    