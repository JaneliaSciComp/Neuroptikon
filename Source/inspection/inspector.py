#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

import os, sys
import wx


def inspectorClasses():
    inspectorClasses = []
    classesToInspect = Inspector.__subclasses__() # pylint_disabled: disable=E1101
    while any(classesToInspect):
        classToInspect = classesToInspect.pop(0)
        if classToInspect.shouldBeRegistered():
            inspectorClasses += [classToInspect]
        classesToInspect += classToInspect.__subclasses__()
    return inspectorClasses


class Inspector( object ):
    
    @classmethod
    def name(cls):
        return ''
    
    
    @classmethod
    def shouldBeRegistered(cls):
        return True
    
    
    @classmethod
    def bitmap(cls, size = 32):
        # Check for an Icon.png in the same directory as this class's module's source file, otherwise return an empty bitmap.
        iconPath = os.path.join(os.path.dirname(sys.modules[cls.__module__].__file__), 'Icon.png')
        if os.path.exists(iconPath):
            try:
                image = wx.Image(iconPath)
            except:
                image = None
        else:
            image = None
        if image is not None and image.IsOk():
            image.Rescale(size, size, wx.IMAGE_QUALITY_HIGH)
            return image.ConvertToBitmap()
        else:
            return wx.EmptyBitmap(size, size)
    
    
    @classmethod
    def canInspectDisplay(cls, display):
        return (display != None)
    
    
    def window(self, parentWindow=None):
        return None
    
    
    def willBeShown(self):
        pass
    
    
    def inspectDisplay(self, display):
        pass
    
    
    def willBeClosed(self):
        pass
    
    
    @classmethod
    def __cmp_name__(cls):
        superClass = cls.__bases__[0]
        if hasattr(superClass, '__cmp_name__'):
            return superClass.__cmp_name__() + ': ' + cls.name()
        else:
            return cls.name()
        
    
    def __cmp__(self, other):
        if isinstance(other, Inspector):
            selfStr = self.__cmp_name__()
            otherStr = other.__cmp_name__()
            if selfStr < otherStr:
                return -1
            elif selfStr == otherStr:
                return 0
            else:
                return 1
        else:
            return 1
    
    
