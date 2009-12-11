import wx
import cPickle
import library

class LibraryItemFrame( wx.Frame ):
    
    def __init__(self, libraryItem):
        
        wx.Frame.__init__(self, None, -1, gettext('%s: %s') % (libraryItem.__class__.displayName() or gettext('Item'), libraryItem.name or libraryItem.identifier), size=(300, 400), style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_TOOL_WINDOW)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        
        self.libraryItem = libraryItem
        
    
    def onClose(self, event):
        self.Hide()
        return True
    
