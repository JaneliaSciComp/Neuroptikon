from Object import Object
import xml.etree.ElementTree as ElementTree

class Muscle(Object):
    
    # TODO: stretch receptors?
    
    def __init__(self, network, *args, **keywords):
        """
        Muscle objects represent muscles in the :class:`network <Network.Network.Network>` and can be :class:`innervated <Network.Innervation.Innervation>` by :class:`neurites <Network.Neurite.Neurite>`.
        
        Create a muscle by messaging the network:
        
        >>> muscle1 = network.createMuscle()
        >>> neuron1.innervate(muscle1)
        """
        
        Object.__init__(self, network, *args, **keywords)
        self._innervations = []
    
    
    @classmethod
    def _fromXMLElement(cls, network, xmlElement):
        object = super(Muscle, cls)._fromXMLElement(network, xmlElement)
        object._innervations = []
        return object
    
    
    def _needsScriptRef(self):
        return True
    
    
    def innervations(self):
        """
        Return the list of :class:`innervations <Network.Innervation.Innervation>` of this muscle.
        
        If no neurites innervate this muscle then an empty list will be returned.
        """
        
        return list(self._innervations)
    
    
    def connections(self, recurse = True):
        return Object.connections(self, recurse) + self._innervations
    
    
    def inputs(self, recurse = True):
        return Object.inputs(self, recurse) + self._innervations
