import wx
from ObjectInspector import ObjectInspector
from Region import Region


class RegionInspector( ObjectInspector ):
    
    def objectClass(self):
        return Region
    
    
    def inspect(self, display, visibles):
        ObjectInspector.inspect(self, display, visibles)
        
        # Lazily create our UI
        if not hasattr(self, ''):
#            self.GetSizer().Add(foo, 0, wx.EXPAND)
            self.GetSizer().Layout()
