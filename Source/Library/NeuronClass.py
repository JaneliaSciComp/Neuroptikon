from LibraryItem import LibraryItem

class NeuronClass(LibraryItem):
    
    @classmethod
    def listProperty(cls):
        return 'neuronClasses'
    
    
    @classmethod
    def lookupProperty(cls):
        return 'neuronClass'
    
    
    def __init__(self, parentClass = None, polarity = None, excitatory = None, neurotransmitter = None, *args, **keywordArgs):
        LibraryItem.__init__(self, *args, **keywordArgs)
        
        # Neuron classes are arranged in a hierarchy.
        self.parentClass = parentClass
        self.subClasses = []
        
        # Properties of this class
        if self.parentClass:
            self.parentClass.subClasses.append(self)
            
            self.polarity = self.parentClass.polarity
            self.excitatory = self.parentClass.excitatory
            self.neurotransmitter = self.parentClass.neurotransmitter
        else:
            self.polarity = polarity
            self.excitatory = excitatory
            self.neurotransmitter = neurotransmitter
            
