'''Display package'''

__version__ = "1.0.0"

# To be able to associate layout classes with menu items they need to have a unique ID.
import wx

__layoutClasses__ = {}

def registerLayoutClass(layoutClass):
    __layoutClasses__[wx.NewId()] = layoutClass

def layoutClasses(*args, **keywordArgs):
    return __layoutClasses__

# TODO: add API/prefs for permanent layout registration
