import wx
from ObjectInspector import ObjectInspector
from Neurite import Neurite


class NeuriteInspector( ObjectInspector ):
    
    def objectClass(self):
        return Neurite
    
    
    def inspectObjects(self):
        
        # Lazily create our UI
        if not hasattr(self, ''):
#            self.GetSizer().Add(foo, 0, wx.EXPAND)
            self.GetSizer().Layout()
