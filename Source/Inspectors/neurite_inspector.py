import wx
from object_inspector import ObjectInspector
from network.neurite import Neurite


class NeuriteInspector( ObjectInspector ):
    
    @classmethod
    def objectClass(cls):
        return Neurite
