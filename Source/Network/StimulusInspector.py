import wx
from ObjectInspector import ObjectInspector
from Stimulus import Stimulus


class StimulusInspector( ObjectInspector ):
    
    def objectClass(self):
        return Stimulus
    
    
    def inspectObjects(self):
        
        # Lazily create our UI
        if not hasattr(self, ''):
#            self.GetSizer().Add(foo, 0, wx.EXPAND)
            self.GetSizer().Layout()
