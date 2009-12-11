import wx
from object_inspector import ObjectInspector
from network.innervation import Innervation


class InnervationInspector( ObjectInspector ):
    
    @classmethod
    def objectClass(cls):
        return Innervation
