import wx


class Inspector( object ):
    
    @classmethod
    def name(cls):
        return ''
    
    
    @classmethod
    def bitmap(cls):
        return wx.EmptyBitmap(16, 16)
    
    
    @classmethod
    def canInspectDisplay(cls, display):
        return True
    
    
    def window(self, parentWindow=None):
        return None
    
    
    def willBeShown(self):
        pass
    
    
    def inspectDisplay(self, display):
        pass
    
    
    def willBeClosed(self):
        pass
