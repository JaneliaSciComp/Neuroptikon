import wx
import sys
from pydispatch import dispatcher
import Inspection

# TODO: should use dispatcher to listen for selection changes from the current display

class InspectorFrame( wx.Frame ):
    
    def __init__(self, parent=None):
        wx.Frame.__init__(self, parent, -1, _("Inspector"), size=(200,300), style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_TOOL_WINDOW)
        
        self.display = None
        self.toolBook = None
        
        self.SetSizer(wx.BoxSizer(wx.VERTICAL))
        
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
        else:
            lastInspectorClass = None
        
        self.toolBook = wx.Toolbook(self, wx.ID_ANY)
        inspectors = []
        for inspectorClass in Inspection.inspectorClasses():
            # Create a new inspector instance
            inspector = inspectorClass(self.toolBook)
            if inspector.canInspectDisplay(self.display):
                inspectors.append(inspector)
        
        if len(inspectors) == 0:
            self.toolBook = None
        else:
            self.toolBook.SetFitToCurrentPage(True)
            imageList = wx.ImageList(16, 16)
            self.toolBook.SetImageList(imageList)
            for inspector in inspectors:
                imageList.Add(inspector.bitmap())
                self.toolBook.AddPage(inspector, inspector.name(), imageId = imageList.GetImageCount() - 1)
                inspector.inspectDisplay(self.display)
            self.GetSizer().Add(self.toolBook, 0, wx.EXPAND)
            self.Bind(wx.EVT_TOOLBOOK_PAGE_CHANGING, self.onPageChanging, self.toolBook)
            self.Bind(wx.EVT_TOOLBOOK_PAGE_CHANGED, self.onPageChanged, self.toolBook)
        
        if lastInspectorClass is not None:
            foundInspector = False
            for i in range(0, len(inspectors)):
                if inspectors[i].__class__ == lastInspectorClass:
                    self.toolBook.ChangeSelection(i)
                    foundInspector = True
            if not foundInspector:
                lastInspectorBaseClass = lastInspectorClass.__bases__[0]
                for i in range(0, len(inspectors)):
                    inspectorBaseClasses = inspectors[i].__class__.__bases__
                    if lastInspectorBaseClass in inspectorBaseClasses:
                        self.toolBook.ChangeSelection(i)
        
        self.Layout()
    
    
    def currentInspector(self):
        return self.toolBook.GetCurrentPage()
    
    
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
    
