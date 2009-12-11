import wx
import platform, sys
from pydispatch import dispatcher
import inspector as inspector_module


class InspectorFrame( wx.Frame ):
    
    def __init__(self, parent=None):
        wx.Frame.__init__(self, parent, -1, gettext('Inspector'), size=(200,300), style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_TOOL_WINDOW)
        
        self.display = None
        
        self._updatingInspectors = False
        self._lastClickedInspectorClass = None
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(mainSizer)
        
        # Create an instance of each inspector class.
        self._inspectors = []
        for inspectorClass in inspector_module.inspectorClasses():
            inspector = inspectorClass()
            inspectorWindow = inspector.window(self)
            self._inspectors.append(inspector)
            mainSizer.Add(inspectorWindow, 1, wx.EXPAND)
            mainSizer.Hide(inspectorWindow)
        self._inspectors.sort()
        
        self._activeInspectors = []
        self._activeInspector = None
        
        self.CreateToolBar()
        
        self.Bind(wx.EVT_SIZE, self.onSize)
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
    
    
    def onDisplaySelectionChanged(self, signal, sender):
        self.updateInspectors()
    
    
    def updateInspectors(self):
        # Update the available inspectors based on the current selection.
        
        self.setActiveInspector(None)
        
        self._activeInspectors = []
        self._minWidth = self._minHeight = 0
        toolbar = self.GetToolBar()
        toolbar.ClearTools()
        for inspector in self._inspectors:
            inspector.toolbarId = None
            if inspector.canInspectDisplay(self.display):
                self._activeInspectors.append(inspector)
                inspector.toolbarId = wx.NewId()
                bitmapSize = 16 if platform.system() == 'Windows' else 32
                toolbar.AddRadioLabelTool(inspector.toolbarId, inspector.__class__.name(), inspector.__class__.bitmap(bitmapSize), wx.NullBitmap, gettext('%s Inspector') % (inspector.__class__.name()))
                self.Bind(wx.EVT_TOOL, self.onShowInspector, id = inspector.toolbarId)
                bestSize = inspector.window().GetBestSize()
                self._minWidth = max(self._minWidth, bestSize.GetWidth())
                self._minHeight = max(self._minHeight, bestSize.GetHeight())
        toolbar.Realize()
        
        if len(self._activeInspectors) > 0:
            # Try to re-select the same inspector that was most recently chosen by the user.
            if self._lastClickedInspectorClass is not None:
                for inspector in self._activeInspectors:
                    if isinstance(inspector, self._lastClickedInspectorClass):
                        self.setActiveInspector(inspector)
                        break
                if self._activeInspector is None:
                    # No exact match in the current list of inspectors, see if there is one with the same base class.
                    lastInspectorBaseClass = self._lastClickedInspectorClass.__bases__[0]
                    for inspector in self._activeInspectors:
                        inspectorBaseClasses = inspector.__class__.__bases__
                        if lastInspectorBaseClass in inspectorBaseClasses:
                            self.setActiveInspector(inspector)
                            break
            if self._activeInspector is None:
                self.setActiveInspector(self._activeInspectors[0])
    
    
    def setActiveInspector(self, inspector):
        if inspector != self._activeInspector:
            if self._activeInspector is not None:
                self._activeInspector.willBeClosed()
                self.GetSizer().Hide(self._activeInspector.window())
            self._activeInspector = inspector
            if self._activeInspector is None:
                self.SetTitle(gettext('Inspector'))
            else:
                self._activeInspector.willBeShown()
                self._activeInspector.inspectDisplay(self.display)
                self.GetSizer().Show(self._activeInspector.window())
                self.SetTitle(gettext('%s Inspector') % (inspector.name()))
                toolbarWidth = len(self._activeInspectors) * 32
                self.SetMinSize(wx.Size(max(self._minWidth, toolbarWidth), self._minHeight + 40))
                self._activeInspector.window().Layout()
                toolbar = self.GetToolBar()
                toolbar.ToggleTool(self._activeInspector.toolbarId, True)
            self.Layout()
            self.SendSizeEvent()
    
    
    def onShowInspector(self, event):
        for inspector in self._activeInspectors:
            if inspector.toolbarId == event.GetId():
                self._lastClickedInspectorClass = inspector.__class__
                self.setActiveInspector(inspector)
                break
    
    
    def onSize(self, event):
        if self._activeInspector is not None:
            self._activeInspector.window().Layout()
            self.Layout()
    
    
    def Close(self, event=None):
        self.Hide()
        return True
    
