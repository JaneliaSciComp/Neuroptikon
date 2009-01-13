import wx
from ObjectInspector import ObjectInspector
from Neurite import Neurite


class NeuriteInspector( ObjectInspector ):
    
    @classmethod
    def objectClass(cls):
        return Neurite
