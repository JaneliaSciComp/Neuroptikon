'''Display package'''

__version__ = "1.0.0"

# To be able to associate layout classes with menu items they need to have a unique ID.
import wx

__layoutClasses__ = {}
__shapeClasses__ = {}

def registerLayoutClass(layoutClass):
    __layoutClasses__[wx.NewId()] = layoutClass

def layoutClasses(*args, **keywordArgs):
    return __layoutClasses__

def registerShapeClass(shapeClass):
    __shapeClasses__[wx.NewId()] = shapeClass

def shapeClasses(*args, **keywordArgs):
    return __shapeClasses__


# TODO: add API/prefs for permanent layout/shape registration
