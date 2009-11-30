import Neuroptikon
from neuro_object import NeuroObject


class Muscle(NeuroObject):
    
    # TODO: stretch receptors?
    
    def __init__(self, network, *args, **keywords):
        """
        Muscle objects represent muscles in the :class:`network <Network.Network.Network>` and can be :class:`innervated <Network.Innervation.Innervation>` by :class:`neurites <Network.Neurite.Neurite>`.
        
        Create a muscle by messaging the network:
        
        >>> muscle1 = network.createMuscle()
        >>> neuron1.innervate(muscle1)
        """
        
        NeuroObject.__init__(self, network, *args, **keywords)
        self._innervations = []
    
    
    @classmethod
    def _fromXMLElement(cls, network, xmlElement):
        muscle = super(Muscle, cls)._fromXMLElement(network, xmlElement)
        muscle._innervations = []
        return muscle
    
    
    def _needsScriptRef(self):
        return True
    
    
    def innervations(self):
        """
        Return the list of :class:`innervations <Network.Innervation.Innervation>` of this muscle.
        
        If no neurites innervate this muscle then an empty list will be returned.
        """
        
        return list(self._innervations)
    
    
    def connections(self, recurse = True):
        return NeuroObject.connections(self, recurse) + self._innervations
    
    
    def inputs(self, recurse = True):
        return NeuroObject.inputs(self, recurse) + self._innervations
    
    
    def defaultVisualizationParams(self):
        params = NeuroObject.defaultVisualizationParams(self)
        shapeClasses = Neuroptikon.scriptLocals()['shapes']
        params['shape'] = shapeClasses['Capsule']
        params['size'] = (.05, .1, .02)
        params['color'] = (0.75, 0.5, 0.5)
        try:
            params['texture'] = Neuroptikon.library.texture('Stripes')
        except:
            pass
        params['textureScale'] = 20.0
        params['label'] = self.abbreviation or self.name
        return params
