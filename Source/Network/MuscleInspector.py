import wx
from ObjectInspector import ObjectInspector
from Muscle import Muscle


class MuscleInspector( ObjectInspector ):
    
    def objectClass(self):
        return Muscle
    
    
    def inspect(self, display, visibles):
        ObjectInspector.inspect(self, display, visibles)
        
        # Lazily create our UI
        if not hasattr(self, ''):
#            self.GetSizer().Add(foo, 0, wx.EXPAND)
            self.GetSizer().Layout()
