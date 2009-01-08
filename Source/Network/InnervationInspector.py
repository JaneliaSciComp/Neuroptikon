import wx
from ObjectInspector import ObjectInspector
from Innervation import Innervation


class InnervationInspector( ObjectInspector ):
    
    def objectClass(self):
        return Innervation
    
    
    def inspect(self, display, visibles):
        ObjectInspector.inspect(self, display, visibles)
        
        # Lazily create our UI
        if not hasattr(self, ''):
#            self.GetSizer().Add(foo, 0, wx.EXPAND)
            self.GetSizer().Layout()
