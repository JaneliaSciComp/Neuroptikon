import wx, wx.lib.colourselect


class Preferences( wx.Frame ):
    
    def __init__(self, parent=None):
        wx.Frame.__init__(self, parent, -1, gettext('Preferences'), size = (200,300), pos = (-1,-1))
        
        # Build the UI
        config = wx.Config('Neuroptikon')
        backgroundColor = wx.Color(config.ReadFloat('Color/Background/Red', 0.7) * 255, \
                                   config.ReadFloat('Color/Background/Green', 0.8) * 255, \
                                   config.ReadFloat('Color/Background/Blue', 0.7) * 255, \
                                   config.ReadFloat('Color/Background/Alpha', 1.0) * 255)
        self.colorPicker = wx.lib.colourselect.ColourSelect(self, -1, "", backgroundColor)    #wx.ColourPickerCtrl(self, -1, backgroundColor)
        self.Bind(wx.lib.colourselect.EVT_COLOURSELECT, self.onColorChanged)
        colorBox = wx.BoxSizer(wx.HORIZONTAL)
        colorBox.Add(wx.StaticText(self, -1, gettext('Default Background Color:')), 0, wx.EXPAND)
        colorBox.AddSpacer(8)
        colorBox.Add(self.colorPicker, 1, wx.EXPAND)
        
        # Bundle them together
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(colorBox, 0, wx.ALL, 5)
        self.SetSizer(self.mainSizer)
        
        self.Bind(wx.EVT_CLOSE, self.onClose)
    
    
    def onColorChanged(self, event):
        color = self.colorPicker.GetColour()
        config = wx.Config('Neuroptikon')
        config.WriteFloat('Color/Background/Red', color.Red() / 255.0)
        config.WriteFloat('Color/Background/Green', color.Green() / 255.0)
        config.WriteFloat('Color/Background/Blue', color.Blue() / 255.0)
        config.WriteFloat('Color/Background/Alpha', color.Alpha() / 255.0)
        
    
    def onClose(self, event=None):
        self.Hide()
        return True
    
