import wx
from ObjectInspector import ObjectInspector
from Pathway import Pathway


class PathwayInspector( ObjectInspector ):
    
    def objectClass(self):
        return Pathway
    
    
    def inspectObjects(self):
        
        # Lazily create our UI
        if not hasattr(self, ''):
#            self.GetSizer().Add(foo, 0, wx.EXPAND)
            self.GetSizer().Layout()
