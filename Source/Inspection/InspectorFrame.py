import wx
import sys
import Inspection

# TODO: should use dispatcher to listen for selection changes from the current display

class InspectorFrame( wx.Frame ):
    
    def __init__(self, parent=None):
        wx.Frame.__init__(self, parent, -1, _("Inspector"), size=(200,300), style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_TOOL_WINDOW)
        
        self.toolBook = wx.Toolbook(self, wx.ID_ANY)
        self.toolBook.SetFitToCurrentPage(True)
        self.imageList = wx.ImageList(16, 16)
        self.toolBook.SetImageList(self.imageList)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.onPageChanging, self.toolBook)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onPageChanged, self.toolBook)
        self.grabChosenInspectorClass = False
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.toolBook, 0, wx.EXPAND)
        self.SetSizer(sizer)
        
        self.Bind(wx.EVT_CLOSE, self.Close)
        
        
# TODO: move to new multi-selection inspector
#        self.multiGridSizer = wx.FlexGridSizer(0, 3, 8, 8)
#        self.multiGridSizer.SetFlexibleDirection(wx.HORIZONTAL)
#        self.multiSelectionBox = wx.BoxSizer(wx.VERTICAL)
#        self.multiSelectionBox.Add(self.multiGridSizer, 1, wx.EXPAND)
#            self.iconField.SetBitmap(self.emptyBitmap)
#            self.titleField.SetLabel(str(len(objects)) + _(" items selected"))
#            self.subTitleField.SetLabel("")
#            self.multiGridSizer.Clear(True)
#            allFixed = True
#            allUnfixed = True
#            for object in self.objects:
#                bitmap = wx.StaticBitmap(self, -1)
#                bitmap.SetMinSize(wx.Size(16, 16))
#                bitmap.SetMaxSize(wx.Size(16, 16))
#                image = object.image()
#                if image is None or not image.Ok():
#                    bitmap.SetBitmap(wx.NullBitmap)
#                else:
#                    scaledImage = image.Rescale(16, 16)
#                    bitmap.SetBitmap(wx.BitmapFromImage(scaledImage))
#                self.multiGridSizer.Add(bitmap)
#                self.multiGridSizer.Add(wx.StaticText(self, -1, object.name or _("Unnamed ") + object.__class__.__name__))
#                selectButton = wx.Button(self, -1, _("Select"), wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT)
#                selectButton.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)
#                selectButton.SetSize(wx.Size(50, selectButton.GetSize().GetHeight()))
#                selectButton.SetMinSize(selectButton.GetSize())
#                self.Bind(wx.EVT_BUTTON, self.onSelectObject)
#                self.multiGridSizer.Add(selectButton, 0, 0, 0, object)
#            self.Layout()
#    def onSelectObject(self, event):
#        sizerItem = self.multiGridSizer.GetItem(event.GetEventObject())
#        self.display.selectObject(sizerItem.GetUserData())


# TODO: move to new visible inspector
#        self.fixedPositionCheckBox = wx.CheckBox(self, -1, _("Fixed position"), wx.DefaultPosition, wx.DefaultSize, wx.CHK_3STATE)
#        self.Bind(wx.EVT_CHECKBOX, self.onSetPositionIsFixed)
#        self.footerBox = wx.BoxSizer(wx.VERTICAL)
#        self.footerBox.Add(self.fixedPositionCheckBox, 0, wx.EXPAND )
#        self.fixedPositionCheckBox.SetValue(visible.positionIsFixed())
#        self.fixedPositionCheckBox.Enable(True)
    
    
    def inspect(self, display, visibles):
        self.display = display
        self.visibles = visibles
        
        inspector = self.toolBook.GetCurrentPage()
        if inspector is not None:
            inspector.willBeClosed()
        
        self.Unbind(wx.EVT_TOOLBOOK_PAGE_CHANGING, self.toolBook)
        self.Unbind(wx.EVT_TOOLBOOK_PAGE_CHANGED, self.toolBook)
        
        inspectors = []
        for i in range(self.toolBook.GetPageCount() - 1, -1, -1):
            inspector = self.toolBook.GetPage(i)
            if inspector.canInspect(self.display, self.visibles):
                inspector.inspect(self.display, self.visibles)
                inspectors.append(inspector)
            else:
                self.toolBook.DeletePage(i)
                self.imageList.Remove(i)
        
        for inspectorClass in Inspection.inspectorClasses():
            existingInspector = None
            for inspector in inspectors:
                if inspector.__class__ == inspectorClass:
                    existingInspector = inspector
            if existingInspector is None:
                inspector = inspectorClass(self.toolBook)
                if inspector.canInspect(display, visibles):
                    self.imageList.Add(inspector.bitmap())
                    self.toolBook.AddPage(inspector, inspector.name(), imageId = self.imageList.GetImageCount() - 1)
                    inspector.inspect(self.display, self.visibles)
        self.Bind(wx.EVT_TOOLBOOK_PAGE_CHANGING, self.onPageChanging, self.toolBook)
        self.Bind(wx.EVT_TOOLBOOK_PAGE_CHANGED, self.onPageChanged, self.toolBook)
        
        self.Layout()
    
    
    def onPageChanging(self, event):
        inspector = self.toolBook.GetCurrentPage()
        if inspector is not None:
            inspector.willBeClosed()
        event.Skip()
    
    
    def onPageChanged(self, event):
        inspector = self.toolBook.GetCurrentPage()
        if inspector is not None:
            inspector.willBeShown()
            inspector.Layout()
            self.Layout()
            self.Fit()
            self.SetTitle(inspector.name() + ' ' + _('Inspector'))
        event.Skip()
        
    
    def Close(self, event=None):
        self.Hide()
        return True
    
