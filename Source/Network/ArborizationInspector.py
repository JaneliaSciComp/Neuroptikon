import wx
from ObjectInspector import ObjectInspector
from Arborization import Arborization


class ArborizationInspector( ObjectInspector ):
    
    def objectClass(self):
        return Arborization
    
    
    def inspect(self, display, visibles):
        ObjectInspector.inspect(self, display, visibles)
        
        # Lazily create our UI
        if not hasattr(self, ''):
#            self.GetSizer().Add(foo, 0, wx.EXPAND)
            self.GetSizer().Layout()
