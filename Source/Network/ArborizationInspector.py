import wx
from ObjectInspector import ObjectInspector
from Arborization import Arborization


class ArborizationInspector( ObjectInspector ):
    
    @classmethod
    def objectClass(cls):
        return Arborization
