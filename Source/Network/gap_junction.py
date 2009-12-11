import neuroptikon
from neuro_object import NeuroObject

class GapJunction(NeuroObject):
    
    # TODO: gap junctions can be directional?
    
    def __init__(self, network, neurite1, neurite2, *args, **keywords):
        """
        GapJunction objects represent a gap junction between two :class:`neurites <Network.Neurite.Neurite>` in a :class:`network <Network.Network.Network>`.
        
        Instances of this class are created by using the gapJunctionWith method of :meth:`Neuron <Network.Neuron.Neuron.gapJunctionWith>` and :meth:`Neurite <Network.Neurite.Neurite.gapJunctionWith>` objects.
        
        >>> neuron1.gapJunctionWith(neuron2)
        """
        
        NeuroObject.__init__(self, network, *args, **keywords)
        self._neurites = set([neurite1, neurite2])
    
    
    def defaultName(self):
        neurite1, neurite2 = list(self._neurites)
        names = [str(neurite1.neuron().name), str(neurite2.neuron().name)]
        names.sort()
        return names[0] + ' <-> ' + names[1]
    
    
    @classmethod
    def _fromXMLElement(cls, network, xmlElement):
        gapJunction = super(GapJunction, cls)._fromXMLElement(network, xmlElement)
        neurite1Id = xmlElement.get('neurite1Id')
        neurite1 = network.objectWithId(neurite1Id)
        neurite2Id = xmlElement.get('neurite2Id')
        neurite2 = network.objectWithId(neurite2Id)
        if neurite1 is None:
            raise ValueError, gettext('Neurite with id "%s" does not exist') % (neurite1Id)
        elif neurite2 is None:
            raise ValueError, gettext('Neurite with id "%s" does not exist') % (neurite2Id)
        else:
            gapJunction._neurites = set([neurite1, neurite2])
            neurite1._gapJunctions.append(gapJunction)
            neurite2._gapJunctions.append(gapJunction)
            return gapJunction
    
    
    def _toXMLElement(self, parentElement):
        gapJunctionElement = NeuroObject._toXMLElement(self, parentElement)
        neurites = list(self._neurites)
        gapJunctionElement.set('neurite1Id', str(neurites[0].networkId))
        gapJunctionElement.set('neurite2Id', str(neurites[1].networkId))
        return gapJunctionElement
    
    
    def _creationScriptCommand(self, scriptRefs):
        neurite1 = list(self._neurites)[0]
        if neurite1.networkId not in scriptRefs:
            neurite1 = neurite1.root
        return scriptRefs[neurite1.networkId] + '.gapJunctionWith'
    
    
    def _creationScriptParams(self, scriptRefs):
        args, keywords = NeuroObject._creationScriptParams(self, scriptRefs)
        neurite2 = list(self._neurites)[1]
        if neurite2.networkId not in scriptRefs:
            neurite2 = neurite2.root
        args.insert(0, scriptRefs[neurite2.networkId])
        return (args, keywords)
    
    
    @classmethod
    def displayName(cls):
        return gettext('Gap Junction')
    
    
    def neurites(self):
        """
        Return a tuple containing the two :class:`neurites <Network.Neurite.Neurite>` connected by this gap junction.
        """
        
        return tuple(self._neurites)
    
    
    def connections(self, recurse = True):
        return NeuroObject.connections(self, recurse) + list(self._neurites)    
    
    
    def inputs(self, recurse = True):
        return NeuroObject.inputs(self, recurse) + list(self._neurites)    
    
    
    def outputs(self, recurse = True):
        return NeuroObject.outputs(self, recurse) + list(self._neurites)
    
    
    def disconnectFromNetwork(self):
        for neurite in self._neurites:
            neurite._gapJunctions.remove(self)
    
    
    def defaultVisualizationParams(self):
        params = NeuroObject.defaultVisualizationParams(self)
        shapeClasses = neuroptikon.scriptLocals()['shapes']
        params['shape'] = shapeClasses['Line']
        params['color'] = (.65, 0.75, 0.4)
        params['pathEndPoints'] = tuple([neurite.neuron() for neurite in self.neurites()])
        params['flowTo'] = True
        params['flowFrom'] = True
        return params
    