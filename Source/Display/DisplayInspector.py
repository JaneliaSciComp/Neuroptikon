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
            
            self._sizer = wx.FlexGridSizer(2, 2, 8, 8)
            
            self.backgroundColorPicker = wx.lib.colourselect.ColourSelect(self._window, wx.ID_ANY)
            self._window.Bind(wx.lib.colourselect.EVT_COLOURSELECT, self.onColorChanged, self.backgroundColorPicker)
            self._sizer.Add(wx.StaticText(self._window, wx.ID_ANY, gettext('Background Color:')), 0)
            self._sizer.Add(self.backgroundColorPicker, 0)
            
            self._sizer.Add(wx.StaticText(self._window, wx.ID_ANY, gettext('2D View Plane:')), 0)
            self.xyButton = wx.RadioButton(self._window, wx.ID_ANY, gettext('XY'), style=wx.RB_GROUP)
            self._window.Bind(wx.EVT_RADIOBUTTON, self.onSetOrthoViewXY, self.xyButton)
            self._sizer.Add(self.xyButton, 0)
            self._sizer.AddStretchSpacer()
            self.xzButton = wx.RadioButton(self._window, wx.ID_ANY, gettext('XZ'))
            self._window.Bind(wx.EVT_RADIOBUTTON, self.onSetOrthoViewXZ, self.xzButton)
            self._sizer.Add(self.xzButton, 0)
            self._sizer.AddStretchSpacer()
            self.yzButton = wx.RadioButton(self._window, wx.ID_ANY, gettext('YZ'))
            self._window.Bind(wx.EVT_RADIOBUTTON, self.onSetOrthoViewYZ, self.yzButton)
            self._sizer.Add(self.yzButton, 0)
            
            mainSizer = wx.BoxSizer(wx.VERTICAL)
            mainSizer.Add(self._sizer, 1, wx.ALL, 5)
            self._window.SetSizer(mainSizer)
            
            self._window.Layout()
        
        return self._window

    
    def inspectDisplay(self, display):
        self.display = display
            
        red, green, blue, alpha = self.display.backgroundColor
        self.backgroundColorPicker.SetColour(wx.Color(red * 255, green * 255, blue * 255, alpha * 255))
    
        # TODO: listen for changes to the background color
        
        if self.display.orthoViewPlane == 'xy':
            self.xyButton.SetValue(True)
        elif self.display.orthoViewPlane == 'xz':
            self.xzButton.SetValue(True)
        elif self.display.orthoViewPlane == 'yz':
            self.yzButton.SetValue(True)
    
    
    def onColorChanged(self, event):
        color = self.backgroundColorPicker.GetColour()
        self.display.setBackgroundColor((color.Red() / 255.0, color.Green() / 255.0, color.Blue() / 255.0, color.Alpha() / 255.0))
    
    
    def onSetOrthoViewXY(self, event):
        self.display.setOrthoViewPlane('xy')
    
    
    def onSetOrthoViewXZ(self, event):
        self.display.setOrthoViewPlane('xz')
    
    
    def onSetOrthoViewYZ(self, event):
        self.display.setOrthoViewPlane('yz')
    
