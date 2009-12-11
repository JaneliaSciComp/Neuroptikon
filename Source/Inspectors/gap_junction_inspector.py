import wx
from object_inspector import ObjectInspector
from network.gap_junction import GapJunction


class GapJunctionInspector( ObjectInspector ):
    
    @classmethod
    def objectClass(cls):
        return GapJunction
