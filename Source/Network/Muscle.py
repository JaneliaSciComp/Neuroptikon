from Object import Object
import xml.etree.ElementTree as ElementTree

class Muscle(Object):
    
    # TODO: stretch receptors?
    
    def __init__(self, network, *args, **keywords):
        Object.__init__(self, network, *args, **keywords)
        self.innervations = []
    
    
    @classmethod
    def fromXMLElement(cls, network, xmlElement):
        object = super(Muscle, cls).fromXMLElement(network, xmlElement)
        object.innervations = []
        return object
    
    
    def needsScriptRef(self):
        return True
    
    
    def inputs(self):
        return self.innervations
    
    
