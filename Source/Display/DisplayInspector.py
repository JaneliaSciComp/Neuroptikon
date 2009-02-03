import wx, wx.lib.colourselect
import os
from Inspection.Inspector import Inspector


class DisplayInspector(Inspector):
    
    @classmethod
    def name(cls):
        return gettext('Display')
    
    
    @classmethod
    def bitmap(cls):
        image = wx.Image('Display' + os.sep + 'DisplayInspector.png')
        if image.IsOk():
            image.Rescale(16, 16)
            return image.ConvertToBitmap()
        else:
            return Inspector.bitmap(cls)


    def window(self, parentWindow=None):
        if not hasattr(self, '_window'):
            self._window = wx.Window(parentWindow, wx.ID_ANY)
            self.backgroundColorPicker = wx.lib.colourselect.ColourSelect(self._window, wx.ID_ANY)
            self._window.Bind(wx.lib.colourselect.EVT_COLOURSELECT, self.onColorChanged, self.backgroundColorPicker)
            colorBox = wx.BoxSizer(wx.HORIZONTAL)
            colorBox.Add(wx.StaticText(self._window, wx.ID_ANY, gettext('Background Color:')), 0, wx.EXPAND)
            colorBox.AddSpacer(8)
            colorBox.Add(self.backgroundColorPicker, 1, wx.EXPAND)
            
            mainSizer = wx.BoxSizer(wx.VERTICAL)
            mainSizer.Add(colorBox, 0, wx.ALL, 5)
            self._window.SetSizer(mainSizer)
            
            self._window.Layout()
        
        return self._window

    
    def inspectDisplay(self, display):
        self.display = display
            
        red, green, blue, alpha = self.display.backgroundColor
        self.backgroundColorPicker.SetColour(wx.Color(red * 255, green * 255, blue * 255, alpha * 255))
    
        # TODO: listen for changes to the background color
    
    
    def onColorChanged(self, event):
        color = self.backgroundColorPicker.GetColour()
        self.display.setBackgroundColor((color.Red() / 255.0, color.Green() / 255.0, color.Blue() / 255.0, color.Alpha() / 255.0))
