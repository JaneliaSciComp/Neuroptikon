import wx, wx.lib.colourselect
import os, sys
from Inspection.Inspector import Inspector


class DisplayInspector(Inspector):
    
    @classmethod
    def name(cls):
        return gettext('Display')


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
            self.zyButton = wx.RadioButton(self._window, wx.ID_ANY, gettext('ZY'))
            self._window.Bind(wx.EVT_RADIOBUTTON, self.onSetOrthoViewZY, self.zyButton)
            self._sizer.Add(self.zyButton, 0)
            
            self._ghostingOpacitySlider = wx.Slider(self._window, wx.ID_ANY, 20, 0, 100)
            self._ghostingOpacitySlider.Bind(wx.EVT_SCROLL, self.onSetGhostingOpacity, self._ghostingOpacitySlider)
            self._sizer.Add(wx.StaticText(self._window, wx.ID_ANY, gettext('Ghosting Opacity:')), 0)
            self._sizer.Add(self._ghostingOpacitySlider, 1, wx.EXPAND)
            
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
        elif self.display.orthoViewPlane == 'zy':
            self.zyButton.SetValue(True)
        
        self._ghostingOpacitySlider.SetValue(self.display.ghostingOpacity() * 100.0)
    
    
    def onColorChanged(self, event):
        color = self.backgroundColorPicker.GetColour()
        self.display.setBackgroundColor((color.Red() / 255.0, color.Green() / 255.0, color.Blue() / 255.0, color.Alpha() / 255.0))
    
    
    def onSetOrthoViewXY(self, event):
        self.display.setOrthoViewPlane('xy')
    
    
    def onSetOrthoViewXZ(self, event):
        self.display.setOrthoViewPlane('xz')
    
    
    def onSetOrthoViewZY(self, event):
        self.display.setOrthoViewPlane('zy')
    
    
    def onSetGhostingOpacity(self, event):
        opacity = self._ghostingOpacitySlider.GetValue() / 100.0
        self.display.setGhostingOpacity(opacity)
    
