import wx
from ObjectInspector import ObjectInspector
from Synapse import Synapse


class SynapseInspector( ObjectInspector ):
    
    def objectClass(self):
        return Synapse
    
    
    def inspectObjects(self):
        
        # Lazily create our UI
        if not hasattr(self, ''):
#            self.GetSizer().Add(foo, 0, wx.EXPAND)
            self.GetSizer().Layout()
