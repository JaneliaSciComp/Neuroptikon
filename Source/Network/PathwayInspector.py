import wx
from ObjectInspector import ObjectInspector
from Pathway import Pathway


class PathwayInspector( ObjectInspector ):
    
    @classmethod
    def objectClass(cls):
        return Pathway
