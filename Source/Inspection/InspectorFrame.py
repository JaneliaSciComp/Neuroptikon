import wx
import sys
from pydispatch import dispatcher
import Inspection

class InspectorFrame( wx.Frame ):
    
    def __init__(self, parent=None):
        wx.Frame.__init__(self, parent, -1, _("Inspector"), size=(200,300), style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_TOOL_WINDOW)
        
        self.display = None
        self.toolBook = None
        
        self.SetSizer(wx.BoxSizer(wx.VERTICAL))
        self.Bind(wx.EVT_CLOSE, self.Close)
    
    
    def inspectDisplay(self, display):
        if display != self.display:
            if self.display is not None:
                dispatcher.disconnect(self.onDisplaySelectionChanged, ('set', 'selection'), self.display)
            self.display = display
            if self.display is not None:
                dispatcher.connect(self.onDisplaySelectionChanged, ('set', 'selection'), self.display)
            self.updateInspectors()
            # TODO: Are there display attributes other than the selection that would cause the list of inspectors to change?
    
    
    def onDisplaySelectionChanged( self, signal, sender, event=None, value=None, **arguments):
        self.updateInspectors()
    
    
    def updateInspectors(self):
        # Update the available inspectors based on the current selection.
        # wx.ToolBook is buggy when modifying the pages so the safest thing to do is to nuke the whole thing and start from scratch.
        
        if self.toolBook is not None:
            lastInspectorClass = self.currentInspector().__class__
            self.currentInspector().willBeClosed()
            self.Unbind(wx.EVT_TOOLBOOK_PAGE_CHANGING, self.toolBook)
            self.Unbind(wx.EVT_TOOLBOOK_PAGE_CHANGED, self.toolBook)
            self.toolBook.DeleteAllPages()
            self.GetSizer().Remove(self.toolBook)
            self.toolBook.Destroy()
        else:
            lastInspectorClass = None
        
        self.toolBook = wx.Toolbook(self, wx.ID_ANY)
        self.inspectors = []
        for inspectorClass in Inspection.inspectorClasses():
            # Create a new inspector instance
            if inspectorClass.canInspectDisplay(self.display):
                inspector = inspectorClass()
                self.inspectors.append(inspector)
        
        if len(self.inspectors) == 0:
            self.toolBook = None
        else:
            imageList = wx.ImageList(16, 16)
            self.toolBook.SetImageList(imageList)
            self.toolBook.SetFitToCurrentPage(True)
            for inspector in self.inspectors:
                imageList.Add(inspector.__class__.bitmap())
                self.toolBook.AddPage(inspector.window(self.toolBook), inspector.__class__.name(), imageId = imageList.GetImageCount() - 1)
                # TODO: listen for size changes from each inspector's window and call Fit()?
                inspector.inspectDisplay(self.display)
            self.GetSizer().Add(self.toolBook, 0, wx.EXPAND)
            self.Bind(wx.EVT_TOOLBOOK_PAGE_CHANGING, self.onPageChanging, self.toolBook)
            self.Bind(wx.EVT_TOOLBOOK_PAGE_CHANGED, self.onPageChanged, self.toolBook)
        
        if lastInspectorClass is not None:
            foundInspector = False
            for i in range(0, len(self.inspectors)):
                if self.inspectors[i].__class__ == lastInspectorClass:
                    self.toolBook.ChangeSelection(i)
                    foundInspector = True
            if not foundInspector:
                lastInspectorBaseClass = lastInspectorClass.__bases__[0]
                for i in range(0, len(self.inspectors)):
                    inspectorBaseClasses = self.inspectors[i].__class__.__bases__
                    if lastInspectorBaseClass in inspectorBaseClasses:
                        self.toolBook.ChangeSelection(i)

        if self.toolBook is not None:
            if self.toolBook.GetCurrentPage() is not None:
                self.toolBook.GetCurrentPage().Layout()
            self.toolBook.Layout()
        
        self.Layout()
        self.Fit()
    
    
    def currentInspector(self):
        return self.inspectors[self.toolBook.GetSelection()]
    
    
    def onPageChanging(self, event):
        inspector = self.inspectors[event.GetOldSelection()]
        if inspector is not None:
            inspector.willBeClosed()
        inspector = self.inspectors[event.GetSelection()]
        if inspector is not None:
            inspector.willBeShown()
            if self.toolBook.GetCurrentPage() is not None:
                self.toolBook.GetCurrentPage().Layout()
        self.toolBook.Layout()
        self.Layout()
        self.Fit()
        event.Skip()
    
    
    def onPageChanged(self, event):
        inspector = self.inspectors[event.GetSelection()]
        if inspector is not None:
            self.SetTitle(inspector.name() + ' ' + _('Inspector'))
        self.toolBook.Layout()
        self.Layout()
        self.Fit()
        event.Skip()
        
    
    def Close(self, event=None):
        self.Hide()
        return True
    
