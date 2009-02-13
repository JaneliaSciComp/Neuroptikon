import wx
import sys
from wx.py import dispatcher
import Library


class LibraryFrame( wx.Frame ):
    
    def __init__(self, parent=None):
        wx.Frame.__init__(self, parent, -1, gettext('Library'), size=(320, 250), style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_TOOL_WINDOW)
        
        self.itemClasses = {}
        
        toolbar = wx.ToolBar(self, style = wx.TB_TEXT)
        toolbar.SetToolBitmapSize(wx.Size(32, 32))        toolbar.Realize()
        self.SetToolBar(toolbar)
        self.Bind(wx.EVT_TOOL, self.onShowItemClass)
        
        # TODO: use a tree control instead so library items can be hierarchical
        self.listBox = wx.ListBox(self, wx.ID_ANY, style = wx.LB_SORT)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.onShowItem)
        self.SetSizer(wx.BoxSizer(wx.VERTICAL))
        self.GetSizer().Add(self.listBox, 1, wx.EXPAND | wx.ALL, 5)
        self.Bind(wx.EVT_CLOSE, self.onClose)
    
    
    def addItemClass(self, itemClass):
        if itemClass not in self.itemClasses.values():
            actionID = wx.NewId()
            self.itemClasses[actionID] = itemClass
            bitmap = itemClass.bitmap() or wx.EmptyBitmap(32, 32)
            if bitmap.GetWidth() != 32 or bitmap.GetHeight() != 32:
                image = bitmap.ConvertToImage()
                image.Rescale(32, 32, wx.IMAGE_QUALITY_HIGH)
                bitmap = wx.BitmapFromImage(image)
            self.GetToolBar().AddRadioLabelTool(actionID, itemClass.displayName() or '', bitmap)
            self.GetToolBar().Realize()
    
    
    def onShowItemClass(self, event):
        if event.GetId() in self.itemClasses:
            itemClass = self.itemClasses[event.GetId()]
            libraryItems = getattr(wx.GetApp().library, itemClass.listProperty())()
            self.listBox.Clear()
            for libraryItem in libraryItems:
                self.listBox.Append(libraryItem.name or libraryItem.identifier, libraryItem)
        event.Skip()
    
    
    def onShowItem(self, event):
        libraryItem = self.listBox.GetClientData(event.Selection)
        if libraryItem is not None:
            libraryItem.browse()
        event.Skip()
        
    
    def onClose(self, event):
        self.Hide()
        return True
    
