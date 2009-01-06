import wx
import platform
from Display.Display import Display
from Network.Network import Network
from Search.Finder import Finder


class NeuroptikonFrame( wx.Frame ):
    def __init__(self, parent, id=wx.ID_ANY, title=_("Neuroptikon")):
        wx.Frame.__init__(self, parent, id, title, size=(800,600), style=wx.DEFAULT_FRAME_STYLE|wx.FULL_REPAINT_ON_RESIZE)
        
        self.Bind(wx.EVT_CLOSE, self.onCloseWindow)
        
        width, height = self.GetClientSize()
        self.display = Display(self, wx.ID_ANY, 0, 0, width, height)
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
        toolbar.AddLabelTool(view2DId, _("2D View"), self.loadBitmap("View2D.png"))
        self.Bind(wx.EVT_TOOL, self.display.onViewIn2D, id=view2DId)
        view3DId = wx.NewId()
        toolbar.AddLabelTool(view3DId, _("3D View"), self.loadBitmap("View3D.png"))
        self.Bind(wx.EVT_TOOL, self.display.onViewIn3D, id=view3DId)
        toolbar.Realize()
        self.SetToolBar(toolbar)
    
    
    def loadBitmap(self, fileName):
        image = wx.Image(fileName)
        if platform.system() == 'Windows':
            image.Rescale(16, 16)
        return image.ConvertToBitmap()
    
    
    def menuBar(self):
        menuBar = wx.MenuBar()
        
        fileMenu = wx.Menu()
        self.Bind(wx.EVT_MENU, wx.GetApp().onNewNetwork, fileMenu.Append(wx.NewId(), _("New Network\tCtrl-N"), _("Open a new network window")))
        self.Bind(wx.EVT_MENU, self.onCloseWindow, fileMenu.Append(wx.ID_CLOSE, _("Close Network\tCtrl-W"), _("Close the current network window")))
        fileMenu.AppendSeparator()
        self.Bind(wx.EVT_MENU, self.onRunScript, fileMenu.Append(wx.NewId(), _("Run Script...\tCtrl-R"), _("Run a console script file")))
        self.Bind(wx.EVT_MENU, wx.GetApp().onOpenConsole, fileMenu.Append(wx.NewId(), _("Open the Console\tCtrl-Alt-O"), _("Open the Console window")))
        self.Bind(wx.EVT_MENU, wx.GetApp().onOpenPreferences, fileMenu.Append(wx.ID_PREFERENCES, _("Settings"), _("Change Neuroptikon preferences")))
        fileMenu.AppendSeparator()
        self.Bind(wx.EVT_MENU, wx.GetApp().onQuit, fileMenu.Append(wx.ID_EXIT, _("E&xit\tCtrl-Q"), _("Exit this simple sample")))
        menuBar.Append(fileMenu, _("&File"))
        
        editMenu = wx.Menu()
        self.Bind(wx.EVT_MENU, self.onUndo, editMenu.Append(wx.NewId(), _("Undo\tCtrl-Z"), _("Undo the last action")))
        self.Bind(wx.EVT_MENU, self.onRedo, editMenu.Append(wx.NewId(), _("Redo\tCtrl-Shift-Z"), _("Redo the last action")))
        editMenu.AppendSeparator()
        self.cutMenuItem = editMenu.Append(wx.NewId(), _("Cut\tCtrl-X"), _("Move the selected objects to the clipboard"))
        self.Bind(wx.EVT_MENU, self.onCut, self.cutMenuItem)
        self.copyMenuItem = editMenu.Append(wx.NewId(), _("Copy\tCtrl-C"), _("Copy the selected objects to the clipboard"))
        self.Bind(wx.EVT_MENU, self.onCopy, self.copyMenuItem)
        self.pasteMenuItem = editMenu.Append(wx.NewId(), _("Paste\tCtrl-V"), _("Paste the contents of the clipboard"))
        self.Bind(wx.EVT_MENU, self.onPaste, self.pasteMenuItem)
        editMenu.AppendSeparator()
        self.pasteMenuItem = editMenu.Append(wx.NewId(), _("Find\tCtrl-F"), _("Find objects in the network"))
        self.Bind(wx.EVT_MENU, self.onFind, self.pasteMenuItem)
        menuBar.Append(editMenu, _("&Edit"))
        
        viewMenu = wx.Menu()
        self.Bind(wx.EVT_MENU, wx.GetApp().onOpenInspector, viewMenu.Append(wx.NewId(), _("Open Inspector Window\tCtrl-I"), _("Open the inspector window")))
        viewMenu.AppendSeparator()
        self.showRegionNamesMenuItem = viewMenu.Append(wx.NewId(), _("Show Region Names"), _("Show/hide the region names"), True)
        self.showRegionNamesMenuItem.Check(True)
        self.Bind(wx.EVT_MENU, self.onShowHideRegionNames, self.showRegionNamesMenuItem)
        self.showNeuronNamesMenuItem = viewMenu.Append(wx.NewId(), _("Show Neuron Names"), _("Show/hide the neuron names"), True)
        self.Bind(wx.EVT_MENU, self.onShowHideNeuronNames, self.showNeuronNamesMenuItem)
        self.showFlowMenuItem = viewMenu.Append(wx.NewId(), _("Show Flow of Information"), _("Animate the connections between objects"), True)
        self.Bind(wx.EVT_MENU, self.onShowFlow, self.showFlowMenuItem)
        self.useGhostsMenuItem = viewMenu.Append(wx.NewId(), _("Use Ghosting"), _("Dim objects that are not currently selected"), True)
        self.Bind(wx.EVT_MENU, self.onUseGhosts, self.useGhostsMenuItem)
        viewMenu.AppendSeparator()
        self.Bind(wx.EVT_MENU, self.display.onAutoLayout, viewMenu.Append(wx.NewId(), _("Layout Objects\tCtrl-L"), _("Automatically positions all objects")))
        viewMenu.AppendSeparator()
        self.Bind(wx.EVT_MENU, self.display.onCenterView, viewMenu.Append(wx.NewId(), _("Center View"), _("Center the display on all objects")))
        viewMenu.AppendSeparator()
        self.Bind(wx.EVT_MENU, self.display.onSaveView, viewMenu.Append(wx.NewId(), _("Save View as..."), _("Save the current view to a file")))
        menuBar.Append(viewMenu, _("&View"))
        
        return menuBar
    
    
    def onRunScript(self, event):
        # TODO: It would be nice to provide progress for long running scripts.  Would need some kind of callback for scripts to indicate how far along they were.
        # TODO: make this portable
        dlg = wx.FileDialog(None, _('Choose a script to run'), '/Users/midgleyf/Development/Neuroptikon/Source/Scripts', '', '*.py', wx.OPEN)
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
            self.finder = Finder(self, -1, _("Finder"), pos=(-1,-1))
        
        if self.finder.ShowModal() == wx.ID_OK:
            self.display.selectObjectsMatching(self.finder.predicate)
    
    
    def onShowHideRegionNames(self, event):
        self.display.setShowRegionNames(not self.display.showRegionNames())
    
    
    def onShowHideNeuronNames(self, event):
        self.display.setShowNeuronNames(not self.display.showNeuronNames())
    
    
    def onShowFlow(self, event):
        self.display.setShowFlow(not self.display.showFlow())
    
    
    def onUseGhosts(self, event):
        self.display.setUseGhosts(not self.display.useGhosts())
        
        
    def onCloseWindow(self, event):
        self.display.deselectAll()
        self.display.setShowFlow(False)
        wx.GetApp()._frames.remove(self)    # hackish
        self.Destroy()
