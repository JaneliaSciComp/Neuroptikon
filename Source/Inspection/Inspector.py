import wx


class Inspector( wx.Panel ):
    
    def __init__(self, parentWindow=None):
        wx.Window.__init__(self, parentWindow, wx.ID_ANY)
        
    
    def name(self):
        return ''
    
    
    def bitmap(self):
        return wx.EmptyBitmap(16, 16)
    
    
    def canInspectDisplay(self, display):
        return True
    
    
    def willBeShown(self):
        pass
    
    
    def inspectDisplay(self, display):
        pass
    
    
    def willBeClosed(self):
        pass
