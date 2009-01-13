import wx
from ObjectInspector import ObjectInspector
from Innervation import Innervation


class InnervationInspector( ObjectInspector ):
    
    @classmethod
    def objectClass(cls):
        return Innervation
