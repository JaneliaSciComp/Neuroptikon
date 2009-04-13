import wx
from ObjectInspector import ObjectInspector
from Network.GapJunction import GapJunction


class GapJunctionInspector( ObjectInspector ):
    
    @classmethod
    def objectClass(cls):
        return GapJunction
