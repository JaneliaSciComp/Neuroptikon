import wx
import os, sys
from Inspection.Inspector import Inspector


class GroupInspector(Inspector):
    
    @classmethod
    def name(cls):
        return _('Group')
    
    
    @classmethod
    def bitmap(cls):
        displayDir = os.path.abspath(os.path.dirname(sys.modules['Display'].__file__))
        image = wx.Image(displayDir + os.sep + 'GroupInspector.png')
        if image.IsOk():
            image.Rescale(16, 16)
            return image.ConvertToBitmap()
        else:
            return Inspector.bitmap(cls)
    
    
    @classmethod
    def canInspectDisplay(cls, display):
        return len(display.selection()) > 1


    def window(self, parentWindow=None):
        if not hasattr(self, '_window'):
            self._window = wx.Window(parentWindow, wx.ID_ANY)
            self.gridSizer = wx.FlexGridSizer(0, 3, 8, 8)
            self.gridSizer.SetFlexibleDirection(wx.HORIZONTAL)
            self.groupSizeField = wx.StaticText(self._window, wx.ID_ANY)
            mainSizer = wx.BoxSizer(wx.VERTICAL)
            mainSizer.Add(self.groupSizeField, 0, wx.LEFT | wx.BOTTOM | wx.RIGHT, 5)
            mainSizer.Add(self.gridSizer, 1, wx.EXPAND | wx.ALL, 5)
            self._window.SetSizer(mainSizer)
        
        # TODO: use a scrollable table instead of the grid sizer
        
        return self._window
    
    
    def inspectDisplay(self, display):
        selection = display.selection()
        
        self.gridSizer.Clear(True)
        for visible in selection:
            bitmap = wx.StaticBitmap(self._window, wx.ID_ANY)
            bitmap.SetMinSize(wx.Size(16, 16))
            bitmap.SetMaxSize(wx.Size(16, 16))
            image = visible.client.image()
            if image is None or not image.Ok():
                bitmap.SetBitmap(wx.EmptyBitmap(16, 16))
            else:
                scaledImage = image.Rescale(16, 16)
                bitmap.SetBitmap(wx.BitmapFromImage(scaledImage))
            self.gridSizer.Add(bitmap)
            self.gridSizer.Add(wx.StaticText(self._window, wx.ID_ANY, visible.client.name or _("Unnamed ") + visible.client.__class__.__name__))
            selectButton = wx.Button(self._window, wx.ID_ANY, _("Select"), wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT)
            selectButton.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)
            selectButton.SetSize(wx.Size(50, selectButton.GetSize().GetHeight()))
            selectButton.SetMinSize(selectButton.GetSize())
            self._window.Bind(wx.EVT_BUTTON, self.onSelectVisible)
            self.gridSizer.Add(selectButton, 0, 0, 0, visible)
        
        self.groupSizeField.SetLabel(str(len(selection)) + _(' items selected'))
        
        self._window.Layout()
    
    
    def onSelectVisible(self, event):
        sizerItem = self.gridSizer.GetItem(event.GetEventObject())
        visible = sizerItem.GetUserData()
        visible.display.selectVisible(visible)
