#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

import wx
from library_item import LibraryItem
from network.synapse import Synapse

class Neurotransmitter(LibraryItem):
    
    @classmethod
    def listProperty(cls):
        return 'neurotransmitters'
    
    
    @classmethod
    def lookupProperty(cls):
        return 'neurotransmitter'
    
    
    @classmethod
    def bitmap(cls):
        image = Synapse.image()
        if image == None:
            return None
        else:
            return wx.BitmapFromImage(image)


# Possible additional attributes for the future:  
#     enzyme
#     activity (specific, probably specific, specificity uncertain, etc.)
