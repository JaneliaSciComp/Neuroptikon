#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

import os, sys
import wx


def layoutClasses():
    layoutClasses = []
    classesToInspect = Layout.__subclasses__() # pylint_disabled: disable=E1101
    while any(classesToInspect):
        classToInspect = classesToInspect.pop(0)
        if classToInspect.shouldBeRegistered():
            layoutClasses += [classToInspect]
        classesToInspect += classToInspect.__subclasses__()
    return layoutClasses
    

class Layout( object ):
    
    @classmethod
    def name(cls):
        return ''
    
    
    @classmethod
    def shouldBeRegistered(cls):
        return True
    
    
    @classmethod
    def bitmap(cls):
        # Check for an Icon.png in the same directory as this class's module's source file, otherwise return an empty bitmap.
        iconDir = os.path.dirname(sys.modules[cls.__module__].__file__)
        try:
            image = wx.Image(iconDir + os.sep + 'Icon.png')
        except:
            image = None
        if image is not None and image.IsOk():
            image.Rescale(16, 16, wx.IMAGE_QUALITY_HIGH)
            return image.ConvertToBitmap()
        else:
            return wx.EmptyBitmap(16, 16)
    
    
    @classmethod
    def canLayoutDisplay(cls, display):
        return True
    
    
    def layoutDisplay(self, display):
        pass
