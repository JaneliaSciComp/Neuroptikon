import wx
import os, sys
from Inspection.Inspector import Inspector


class GroupInspector(Inspector):
    
    def name(self):
        return _('Group')
    
    
    def bitmap(self):
        displayDir = os.path.abspath(os.path.dirname(sys.modules['Display'].__file__))
        image = wx.Image(displayDir + os.sep + 'GroupInspector.png')
        if image.IsOk():
            image.Rescale(16, 16)
            return image.ConvertToBitmap()
        else:
            return Inspector.bitmap(self)
    
    
    def canInspectDisplay(self, display):
        return len(display.selection()) > 1
    
    
    def inspectDisplay(self, display):
        selection = display.selection()
        
        if not hasattr(self, 'gridSizer'):
            self.gridSizer = wx.FlexGridSizer(0, 3, 8, 8)
            self.gridSizer.SetFlexibleDirection(wx.HORIZONTAL)
            self.groupSizeField = wx.StaticText(self, wx.ID_ANY)
            mainSizer = wx.BoxSizer(wx.VERTICAL)
            mainSizer.Add(self.groupSizeField, 0, wx.EXPAND | wx.LEFT | wx.BOTTOM | wx.RIGHT, 8)
            mainSizer.Add(self.gridSizer, 1, wx.EXPAND)
            self.SetSizer(mainSizer)
        
        self.gridSizer.Clear(True)
        for visible in selection:
            bitmap = wx.StaticBitmap(self, wx.ID_ANY)
            bitmap.SetMinSize(wx.Size(16, 16))
            bitmap.SetMaxSize(wx.Size(16, 16))
            image = visible.client.image()
            if image is None or not image.Ok():
                bitmap.SetBitmap(wx.EmptyBitmap(16, 16))
            else:
                scaledImage = image.Rescale(16, 16)
                bitmap.SetBitmap(wx.BitmapFromImage(scaledImage))
            self.gridSizer.Add(bitmap)
            self.gridSizer.Add(wx.StaticText(self, wx.ID_ANY, visible.client.name or _("Unnamed ") + visible.client.__class__.__name__))
            selectButton = wx.Button(self, wx.ID_ANY, _("Select"), wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT)
            selectButton.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)
            selectButton.SetSize(wx.Size(50, selectButton.GetSize().GetHeight()))
            selectButton.SetMinSize(selectButton.GetSize())
            self.Bind(wx.EVT_BUTTON, self.onSelectVisible)
            self.gridSizer.Add(selectButton, 0, 0, 0, visible)
        
        self.groupSizeField.SetLabel(str(len(selection)) + _(" items selected"))
        
        self.Layout()
    
    
    def onSelectVisible(self, event):
        sizerItem = self.gridSizer.GetItem(event.GetEventObject())
        visible = sizerItem.GetUserData()
        visible.display.selectVisible(visible)
