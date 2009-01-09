import wx, wx.lib.colourselect
import os
from Inspection.Inspector import Inspector


class DisplayInspector(Inspector):
    
    def name(self):
        return _('Display')
    
    
    def bitmap(self):
        image = wx.Image('Display' + os.sep + 'DisplayInspector.png')
        if image.IsOk():
            image.Rescale(16, 16)
            return image.ConvertToBitmap()
        else:
            return Inspector.bitmap(self)
            
    
    def inspectDisplay(self, display):
        self.display = display
        
        if not hasattr(self, 'backgroundColorPicker'):
            self.backgroundColorPicker = wx.lib.colourselect.ColourSelect(self, wx.ID_ANY)
            self.Bind(wx.lib.colourselect.EVT_COLOURSELECT, self.onColorChanged, self.backgroundColorPicker)
            colorBox = wx.BoxSizer(wx.HORIZONTAL)
            colorBox.Add(wx.StaticText(self, wx.ID_ANY, _('Background Color:')), 0, wx.EXPAND)
            colorBox.AddSpacer(8)
            colorBox.Add(self.backgroundColorPicker, 1, wx.EXPAND)
            
            mainSizer = wx.BoxSizer(wx.VERTICAL)
            mainSizer.Add(colorBox, 0, wx.ALL, 5)
            self.SetSizer(mainSizer)
            
        red, green, blue, alpha = self.display.backgroundColor
        self.backgroundColorPicker.SetColour(wx.Color(red * 255, green * 255, blue * 255, alpha * 255))
    
    
    def onColorChanged(self, event):
        color = self.backgroundColorPicker.GetColour()
        self.display.setBackgroundColor((color.Red() / 255.0, color.Green() / 255.0, color.Blue() / 255.0, color.Alpha() / 255.0))
