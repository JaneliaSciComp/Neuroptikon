import wx
import sys
from wx.py import dispatcher
import Inspection
import Inspector    # Not needed by the code but insures that the Inspector module gets packaged by setuptools.


class InspectorFrame( wx.Frame ):
    
    def __init__(self, parent=None):
        wx.Frame.__init__(self, parent, -1, gettext('Inspector'), size=(200,300), style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_TOOL_WINDOW)
        
        self.display = None
        self.toolBook = None
        
        self._updatingInspectors = False
        self._lastClickedInspectorClass = None
        
        self.SetSizer(wx.BoxSizer(wx.VERTICAL))
        
        self.Bind(wx.EVT_SIZE, self.OnSize)
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
        
        self._updatingInspectors = True
        
        if self.toolBook is not None:
            self.currentInspector().willBeClosed()
            self.Unbind(wx.EVT_TOOLBOOK_PAGE_CHANGING, self.toolBook)
            self.Unbind(wx.EVT_TOOLBOOK_PAGE_CHANGED, self.toolBook)
            self.toolBook.DeleteAllPages()
            self.GetSizer().Remove(self.toolBook)
            self.toolBook.Destroy()
        
        self.toolBook = wx.Toolbook(self, wx.ID_ANY)
        
        self.inspectors = []
        if self.display is not None:
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
            self.GetSizer().Add(self.toolBook, 1, wx.EXPAND)
            self.Bind(wx.EVT_TOOLBOOK_PAGE_CHANGING, self.onPageChanging, self.toolBook)
            self.Bind(wx.EVT_TOOLBOOK_PAGE_CHANGED, self.onPageChanged, self.toolBook)
        
        # Try to re-select the same inspector that was most recently chosen by the user.
        if self._lastClickedInspectorClass is not None:
            foundInspector = False
            for i in range(0, len(self.inspectors)):
                if isinstance(self.inspectors[i], self._lastClickedInspectorClass):
                    self.toolBook.ChangeSelection(i)
                    foundInspector = True
            if not foundInspector:
                # No exact match in the current list of inspectors, see if there is one with the same base class.
                lastInspectorBaseClass = self._lastClickedInspectorClass.__bases__[0]
                for i in range(0, len(self.inspectors)):
                    inspectorBaseClasses = self.inspectors[i].__class__.__bases__
                    if lastInspectorBaseClass in inspectorBaseClasses:
                        self.toolBook.ChangeSelection(i)
        
        self._updatingInspectors = False
    
    
    def currentInspector(self):
        return self.inspectors[self.toolBook.GetSelection()]
    
    
    def onPageChanging(self, event):
        inspector = self.inspectors[event.GetOldSelection()]
        if inspector is not None:
            inspector.willBeClosed()
        inspector = self.inspectors[event.GetSelection()]
        if inspector is not None:
            inspector.willBeShown()
    
    
    def onPageChanged(self, event):
        inspector = self.inspectors[event.GetSelection()]
        if inspector is not None:
            self.SetTitle(inspector.name() + ' ' + gettext('Inspector'))
            if not self._updatingInspectors:
                self._lastClickedInspectorClass = inspector.__class__
            self.Layout()
            self.Fit()
            
            # wx.StaticBoxSizers in wx.ToolBooks are flaky with the current wx.  Any static boxes in the inspector won't be laid out correctly at this point.
            # We have to wait until they get realized and rendered once and then layout again.
            wx.CallAfter(self.relayout)
    
    
    def relayout(self):
        self.Fit()
        self.currentInspector().window().Layout()
    
    
    def OnSize(self, event):
        self.currentInspector().window().Layout()
        event.Skip()
    
    
    def Close(self, event=None):
        self.Hide()
        return True
    
