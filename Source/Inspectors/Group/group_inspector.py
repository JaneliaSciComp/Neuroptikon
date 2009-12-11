import wx
from inspection.inspector import Inspector


class GroupInspector(Inspector):
    
    @classmethod
    def name(cls):
        return gettext('Group')
    
    
    @classmethod
    def canInspectDisplay(cls, display):
        return display and len(display.selection()) > 1


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
            bitmap.SetBitmap(wx.EmptyBitmap(16, 16))
            if visible.client is not None:
                image = visible.client.image() or wx.EmptyImage(16, 16)
                scaledImage = image.Rescale(16, 16)
                bitmap.SetBitmap(wx.BitmapFromImage(scaledImage))
            self.gridSizer.Add(bitmap)
            if visible.client is None:
                clientName = gettext('Virtual object')  # TODO: need a better name for a visible that has no counterpart in the biological layer...
            else:
                clientName = visible.client.name or gettext('Unnamed ') + visible.client.__class__.__name__
            self.gridSizer.Add(wx.StaticText(self._window, wx.ID_ANY, clientName))
            selectButton = wx.Button(self._window, wx.ID_ANY, gettext('Select'), wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT)
            selectButton.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)
            selectButton.SetSize(wx.Size(50, selectButton.GetSize().GetHeight()))
            selectButton.SetMinSize(selectButton.GetSize())
            self._window.Bind(wx.EVT_BUTTON, self.onSelectVisible)
            self.gridSizer.Add(selectButton, 0, 0, 0, visible)
        
        self.groupSizeField.SetLabel(str(len(selection)) + gettext(' items selected'))
        
        self._window.Layout()
    
    
    def onSelectVisible(self, event):
        sizerItem = self.gridSizer.GetItem(event.GetEventObject())
        visible = sizerItem.GetUserData()
        visible.display.selectObject(visible.client)
