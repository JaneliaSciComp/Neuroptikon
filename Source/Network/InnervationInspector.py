import wx
from ObjectInspector import ObjectInspector
from Innervation import Innervation


class InnervationInspector( ObjectInspector ):
    
    def objectClass(self):
        return Innervation
    
    
    def inspectObjects(self):
        
        # Lazily create our UI
        if not hasattr(self, ''):
#            self.GetSizer().Add(foo, 0, wx.EXPAND)
            self.GetSizer().Layout()
