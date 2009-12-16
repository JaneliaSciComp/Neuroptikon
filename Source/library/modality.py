#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

import wx
from library_item import LibraryItem
from network.stimulus import Stimulus

class Modality(LibraryItem):
    
    @classmethod
    def listProperty(cls):
        return 'modalities'
    
    
    @classmethod
    def lookupProperty(cls):
        return 'modality'
    
    
    @classmethod
    def bitmap(cls):
        image = Stimulus.image()
        if image == None:
            return None
        else:
            return wx.BitmapFromImage(image)
    
    

# Possible additional attributes for the future:  
#     Hierarchy, i.e. - electromagnetic (light, magnetic field), chemical (odor, taste), phsyical (sound, touch), etc..
