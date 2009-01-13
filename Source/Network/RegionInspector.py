import wx
from ObjectInspector import ObjectInspector
from Region import Region


class RegionInspector( ObjectInspector ):
    
    @classmethod
    def objectClass(cls):
        return Region
