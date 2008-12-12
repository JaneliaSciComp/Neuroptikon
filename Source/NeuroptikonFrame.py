import wx
from Display.Display import Display
from Network.Network import Network
from Search.Finder import Finder


class NeuroptikonFrame( wx.Frame ):
    def __init__(self, parent, id=wx.ID_ANY, title="Neuroptikon"):
        wx.Frame.__init__(self, parent, id, title, size=(800,600), style=wx.DEFAULT_FRAME_STYLE|wx.FULL_REPAINT_ON_RESIZE)
        
        width, height = self.GetClientSize()
        self.display = Display(self, wx.ID_ANY, 0, 0, width, height)
        self.Bind(wx.EVT_IDLE, self.display.onPaint)
        displayBox = wx.BoxSizer(wx.VERTICAL)
        displayBox.Add(self.display, 1, wx.EXPAND)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(displayBox, 1, wx.EXPAND)
        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        self.SetMenuBar(self.menuBar())
        self.finder = None
        
        toolbar = wx.ToolBar(self)
        view2DId = wx.NewId()
        toolbar.AddLabelTool(view2DId, "2D View", wx.Bitmap("View2D.png"))
        self.Bind(wx.EVT_TOOL, self.display.onViewIn2D, id=view2DId)
        view3DId = wx.NewId()
        toolbar.AddLabelTool(view3DId, "3D View", wx.Bitmap("View3D.png"))
        self.Bind(wx.EVT_TOOL, self.display.onViewIn3D, id=view3DId)
        toolbar.Realize()
        self.SetToolBar(toolbar)
    
    
    def menuBar(self):
        menuBar = wx.MenuBar()
        fileMenu = wx.Menu()
        self.Bind(wx.EVT_MENU, wx.GetApp().onNewNetwork, fileMenu.Append(wx.NewId(), "New Network\tCtrl-N", "Open a new network window"))
        fileMenu.AppendSeparator()
        self.Bind(wx.EVT_MENU, self.onRunScript, fileMenu.Append(wx.NewId(), "Run Script...\tCtrl-R", "Run a console script file"))
        self.Bind(wx.EVT_MENU, wx.GetApp().onOpenConsole, fileMenu.Append(wx.NewId(), "Open the Console\tCtrl-Alt-O", "Open the Console window"))
        fileMenu.AppendSeparator()
        self.Bind(wx.EVT_MENU, wx.GetApp().onQuit, fileMenu.Append(wx.ID_EXIT, "E&xit\tCtrl-Q", "Exit this simple sample"))
        menuBar.Append(fileMenu, "&File")
        
        editMenu = wx.Menu()
        self.Bind(wx.EVT_MENU, self.onUndo, editMenu.Append(wx.NewId(), "Undo\tCtrl-Z", "Undo the last action"))
        self.Bind(wx.EVT_MENU, self.onRedo, editMenu.Append(wx.NewId(), "Redo\tCtrl-Shift-Z", "Redo the last action"))
        editMenu.AppendSeparator()
        self.cutMenuItem = editMenu.Append(wx.NewId(), "Cut\tCtrl-X", "Move the selected objects to the clipboard")
        self.Bind(wx.EVT_MENU, self.onCut, self.cutMenuItem)
        self.copyMenuItem = editMenu.Append(wx.NewId(), "Copy\tCtrl-C", "Copy the selected objects to the clipboard")
        self.Bind(wx.EVT_MENU, self.onCopy, self.copyMenuItem)
        self.pasteMenuItem = editMenu.Append(wx.NewId(), "Paste\tCtrl-V", "Paste the contents of the clipboard")
        self.Bind(wx.EVT_MENU, self.onPaste, self.pasteMenuItem)
        editMenu.AppendSeparator()
        self.pasteMenuItem = editMenu.Append(wx.NewId(), "Find\tCtrl-F", "Find objects in the network")
        self.Bind(wx.EVT_MENU, self.onFind, self.pasteMenuItem)
        menuBar.Append(editMenu, "&Edit")
        
        viewMenu = wx.Menu()
        self.Bind(wx.EVT_MENU, wx.GetApp().onOpenInspector, viewMenu.Append(wx.NewId(), "Open Inspector Window\tCtrl-I", "Open the inspector window"))
        viewMenu.AppendSeparator()
        self.showRegionNamesMenuItem = viewMenu.Append(wx.NewId(), "Show Region Names", "Show/hide the region names", True)
        self.showRegionNamesMenuItem.Check(True)
        self.Bind(wx.EVT_MENU, self.onShowHideRegionNames, self.showRegionNamesMenuItem)
        self.showNeuronNamesMenuItem = viewMenu.Append(wx.NewId(), "Show Neuron Names", "Show/hide the neuron names", True)
        self.Bind(wx.EVT_MENU, self.onShowHideNeuronNames, self.showNeuronNamesMenuItem)
        self.showFlowMenuItem = viewMenu.Append(wx.NewId(), "Show Flow of Information", "Animate the connections between objects", True)
        self.Bind(wx.EVT_MENU, self.onShowFlow, self.showFlowMenuItem)
        viewMenu.AppendSeparator()
        self.Bind(wx.EVT_MENU, self.display.onAutoLayout, viewMenu.Append(wx.NewId(), "Layout Objects\tCtrl-L", "Automatically positions all objects"))
        viewMenu.AppendSeparator()
        self.Bind(wx.EVT_MENU, self.display.onCenterView, viewMenu.Append(wx.NewId(), "Center View", "Center the display on all objects"))
        menuBar.Append(viewMenu, "&View")
        
        return menuBar
    
    
    def onRunScript(self, event):
        # TODO: It would be nice to provide progress for long running scripts.  Would need some kind of callback for scripts to indicate how far along they were.
        # TODO: make this portable
        dlg = wx.FileDialog(None, 'Choose a script to run', '/Users/midgleyf/Development/Neuroptikon/Source/Scripts', '', '*.py', wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            globals = {"createNetwork": wx.GetApp().createNetwork, 
                       "displayNetwork": wx.GetApp().displayNetwork, 
                       "networks": wx.GetApp().networks, 
                       "network": self.display.network, 
                       "display": self.display}
            # TODO: wrap in a try block?
            execfile(dlg.GetPath(), globals)
        dlg.Destroy()
        self.Refresh(False)
        self.Show(True)
    
    
    def onUndo(self, event):
        pass    # TODO
    
    
    def onRedo(self, event):
        pass    # TODO
    
    
    def onCut(self, event):
        pass    # TODO
    
    
    def onCopy(self, event):
        pass    # TODO
    
    
    def onPaste(self, event):
        pass    # TODO
    
    
    def onFind(self, event):
        if self.finder is None:
            self.finder = Finder(self, -1, "Finder", pos=(-1,-1))
        
        if self.finder.ShowModal() == wx.ID_OK:
            self.display.selectObjectsMatching(self.finder.predicate)
    
    
    def onShowHideRegionNames(self, event):
        self.display.setShowRegionNames(not self.display.showRegionNames())
    
    
    def onShowHideNeuronNames(self, event):
        self.display.setShowNeuronNames(not self.display.showNeuronNames())
    
    
    def onShowFlow(self, event):
        self.display.setShowFlow(not self.display.showFlow())
    
    
    def Close(self, force=False):
        self.display.deselectAll()
        self.display.setShowFlow(False)
        return wx.Frame.Close(self, force)
        
        
    def OnCloseWindow(self, event):
        self.display.deselectAll()
        self.display.setShowFlow(False)
        self.Destroy()
