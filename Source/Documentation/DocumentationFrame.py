import Neuroptikon
import Documentation
import wx
import platform

try:
    import wx.webkit as webkit
except ImportError:
    webkit = None

try:
    import wx.lib.iewin_old as iewin
except ImportError:
    iewin = None

def showPage(pageURL):
    if Documentation._sharedFrame == None:
        Documentation._sharedFrame = DocumentationFrame(pageURL)
    else:
        Documentation._sharedFrame.showPage(pageURL)


class DocumentationFrame( wx.Frame ):
    
    def __init__(self, pageURL):
        wx.Frame.__init__(self, None, size = (800, 600), style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_TOOL_WINDOW)
        
        self.Bind(wx.EVT_CLOSE, self.onClose)
        
        # Build the UI
        if webkit:
            try:
                self.htmlViewer = webkit.WebKitCtrl(self)
            except:
                self.htmlViewer = None
        if (not webkit or self.htmlViewer == None) and iewin:
            self.htmlViewer = iewin.IEHtmlWindow(self)
            self.htmlViewer.LoadURL = self.htmlViewer.LoadUrl
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(self.htmlViewer, 1, wx.EXPAND)
        self.SetSizer(self.mainSizer)
        
        # Set up the toolbar
        toolbar = wx.ToolBar(self)
        toolbar.SetToolBitmapSize(wx.Size(32, 32))
        self.goBackTool = toolbar.AddLabelTool(wx.NewId(), gettext('Back'), wx.ArtProvider.GetBitmap(wx.ART_GO_BACK, wx.ART_TOOLBAR))
        self.Bind(wx.EVT_TOOL, self.onGoBack, self.goBackTool)
        self.goForwardTool = toolbar.AddLabelTool(wx.NewId(), gettext('Forward'), wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD, wx.ART_TOOLBAR))
        self.Bind(wx.EVT_TOOL, self.onGoForward, self.goForwardTool)
        toolbar.AddSeparator()
        self.goHomeTool = toolbar.AddLabelTool(wx.NewId(), gettext('Home'), wx.ArtProvider.GetBitmap(wx.ART_GO_HOME, wx.ART_TOOLBAR))
        self.Bind(wx.EVT_TOOL, self.onGoHome, self.goHomeTool)
        self.showIndexTool = toolbar.AddLabelTool(wx.NewId(), gettext('Index'), self._loadBitmap('AtoZ.png'))
        self.Bind(wx.EVT_TOOL, self.onShowIndex, self.showIndexTool)
        toolbar.AddSeparator()
        self.searchControl = wx.SearchCtrl(toolbar, wx.NewId(), style = wx.TE_PROCESS_ENTER, size = wx.Size(200, 20))
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.onSearch)
        self.Bind(wx.EVT_TEXT_ENTER, self.onSearch)
        toolbar.AddControl(self.searchControl)
        toolbar.Realize()
        self.SetToolBar(toolbar)
        
        self.pageURL = None
        self.showPage(pageURL)
    
    
    def _loadBitmap(self, fileName):
        image = Neuroptikon.loadImage(fileName)
        if image is None or not image.IsOk():
            image = wx.EmptyImage(32, 32)
        if platform.system() == 'Windows':
            image.Rescale(16, 16, wx.IMAGE_QUALITY_HIGH)
        return image.ConvertToBitmap()
    
    
    def showPage(self, pageURL):
        if pageURL != self.pageURL:
            self.pageURL = pageURL
            
            self.htmlViewer.LoadURL(self.pageURL)
            self.SetTitle('Neuroptikon Documentation')
            #self.SetTitle('Neuroptikon: ' + self.htmlViewer.GetPageTitle())
        
        self.Show(True)
        self.Raise()
        
    
    def onGoBack(self, event):
        self.htmlViewer.GoBack()
    
    
    def onGoForward(self, event):
        self.htmlViewer.GoForward()
     
    
    def onGoHome(self, event):
        self.htmlViewer.LoadURL(Documentation.baseURL() + 'index.html')
        
    
    def onShowIndex(self, event):
        self.htmlViewer.LoadURL(Documentation.baseURL() + 'genindex.html')
 
    
    def onSearch(self, event):
        self.htmlViewer.LoadURL(Documentation.baseURL() + 'search.html?q=' + self.searchControl.GetValue())
    
    
    def onClose(self, event=None):
        self.Hide()
        return True
    
