#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

import wx
from library_item import LibraryItem
from network.neuron import Neuron

class NeuronClass(LibraryItem):
    
    @classmethod
    def displayName(cls):
        return gettext('Neuron Class')
    
    @classmethod
    def listProperty(cls):
        return 'neuronClasses'
    
    
    @classmethod
    def lookupProperty(cls):
        return 'neuronClass'
    
    
    @classmethod
    def bitmap(cls):
        image = Neuron.image()
        if image == None:
            return None
        else:
            return wx.BitmapFromImage(image)
    
    
    def __init__(self, parentClass = None, *args, **keywordArgs):
        """  """
        
        # Pull out the keyword arguments specific to this class before we call super.
        # We need to do this so we can know if the caller specified an argument or not.
        # For example, the caller might specify a parent class and one attribute to override.  We need to know which attributes _not_ to set.
        localAttrNames = ['activation', 'functions', 'neurotransmitters', 'polarity']
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
            if attrName == 'functions':
                attrValue = set([])
            elif attrName == 'neurotransmitters':
                attrValue = []
            else:
                attrValue = None
            if attrName in localKeywordArgs:
                # The user has explicitly set the attribute.
                if attrName == 'functions':
                    attrValue = set(localKeywordArgs[attrName])
                else:
                    attrValue = localKeywordArgs[attrName]  
            elif self.parentClass:
                attrValue = getattr(self.parentClass, attrName) # Inherit the value from the parent class
            setattr(self, attrName, attrValue)
