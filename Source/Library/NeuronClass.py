from LibraryItem import LibraryItem

class NeuronClass(LibraryItem):
    
    @classmethod
    def listProperty(cls):
        return 'neuronClasses'
    
    
    @classmethod
    def lookupProperty(cls):
        return 'neuronClass'
    
    
    def __init__(self, parentClass = None, *args, **keywordArgs):
        """  """
        
        # Pull out the keyword arguments specific to this class before we call super.
        # We need to do this so we can know if the caller specified an argument or not.
        # For example, the caller might specify a parent class and one attribute to override.  We need to know which attributes _not_ to set.
        localAttrNames = ['excitatory', 'function', 'neurotransmitter', 'polarity']
        localKeywordArgs = {}
        for attrName in localAttrNames:
            if attrName in keywordArgs:
                localKeywordArgs[attrName] = keywordArgs[attrName]
                del keywordArgs[attrName]
        
        LibraryItem.__init__(self, *args, **keywordArgs)
        
        # Neuron classes are arranged in a hierarchy.
        self.parentClass = parentClass
        self.subClasses = []
        if self.parentClass:
            self.parentClass.subClasses.append(self)
        
        for attrName in localAttrNames:
            attrValue = None
            if attrName in localKeywordArgs:
                attrValue = localKeywordArgs[attrName]  # The user has explicitly set the attribute.
            elif self.parentClass:
                attrValue = getattr(self.parentClass, attrName) # Inherit the value from the parent class
            setattr(self, attrName, attrValue)
