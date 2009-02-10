import wx
import sys
from wx.py import dispatcher
import Library


class LibraryFrame( wx.Frame ):
    
    def __init__(self, parent=None):
        wx.Frame.__init__(self, parent, -1, gettext('Library'), size=(200,300), style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_TOOL_WINDOW)
        
        self.itemClasses = {}
        
        toolbar = wx.ToolBar(self)
        toolbar.Realize()
        self.SetToolBar(toolbar)
        self.Bind(wx.EVT_TOOL, self.onShowItemClass)
        
        self.listBox = wx.ListBox(self, wx.ID_ANY, style = wx.LB_SORT)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.onShowItem)
        self.SetSizer(wx.BoxSizer(wx.VERTICAL))
        self.GetSizer().Add(self.listBox, 1, wx.EXPAND | wx.ALL, 5)
        self.Bind(wx.EVT_CLOSE, self.onClose)
    
    
    def addItemClass(self, itemClass):
        if itemClass not in self.itemClasses.values():
            actionID = wx.NewId()
            self.itemClasses[actionID] = itemClass
            self.GetToolBar().AddLabelTool(actionID, itemClass.displayName() or '', itemClass.bitmap() or wx.EmptyBitmap(32, 32))
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
    
