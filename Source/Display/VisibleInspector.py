import wx, wx.lib.colourselect
import os, sys
from Inspection.Inspector import Inspector
from Network.ObjectList import ObjectList


class VisibleInspector(Inspector):
    
    @classmethod
    def name(cls):
        return _('Visible')
    
    
    @classmethod
    def bitmap(cls):
        displayDir = os.path.abspath(os.path.dirname(sys.modules['Display'].__file__))
        image = wx.Image(displayDir + os.sep + 'VisibleInspector.png')
        if image.IsOk():
            image.Rescale(16, 16)
            return image.ConvertToBitmap()
        else:
            return Inspector.bitmap(cls)
    
    
    @classmethod
    def canInspectDisplay(cls, display):
        return len(display.selection()) > 0


    def window(self, parentWindow=None):
        if not hasattr(self, '_window'):
            self._window = wx.Window(parentWindow, wx.ID_ANY)
            gridSizer = wx.FlexGridSizer(2, 2, 8, 8)
            
            self.colorPicker = wx.lib.colourselect.ColourSelect(self._window, wx.ID_ANY)
            self._window.Bind(wx.lib.colourselect.EVT_COLOURSELECT, self.onColorChanged, self.colorPicker)
            gridSizer.Add(wx.StaticText(self._window, wx.ID_ANY, _('Color:')), 0)
            gridSizer.Add(self.colorPicker, 1)
            
            self.fixedPositionCheckBox = wx.CheckBox(self._window, -1, _('Fixed'), style=wx.CHK_3STATE)
            self._window.Bind(wx.EVT_CHECKBOX, self.onSetPositionIsFixed)
            gridSizer.Add(wx.StaticText(self._window, wx.ID_ANY, _('Position:')), 0)
            gridSizer.Add(self.fixedPositionCheckBox, 1)
            
            # TODO: label, shape, opacity, ???
            
            mainSizer = wx.BoxSizer(wx.VERTICAL)
            mainSizer.Add(gridSizer, 1, wx.ALL, 5)
            self._window.SetSizer(mainSizer)
        
        return self._window
    
    
    def inspectDisplay(self, display):
        self.visibles = display.selection()
        
        if self.visibles.haveEqualAttr('color'):
            red, green, blue = self.visibles[0].color()
            self.colorPicker.SetColour(wx.Color(red * 255, green * 255, blue * 255, 255))
        else:
            pass    # TODO
        
        if self.visibles.haveEqualAttr('positionIsFixed'):
            if self.visibles[0].positionIsFixed():
                self.fixedPositionCheckBox.Set3StateValue(wx.CHK_CHECKED)
            else:
                self.fixedPositionCheckBox.Set3StateValue(wx.CHK_UNCHECKED)
        else:
            self.fixedPositionCheckBox.Set3StateValue(wx.CHK_UNDETERMINED)
        
        self._window.Layout()
        
        # TODO: listed for changes to the visibles' attributes
    
    
    def onColorChanged(self, event):
        wxColor = self.colorPicker.GetColour()
        colorTuple = (wxColor.Red() / 255.0, wxColor.Green() / 255.0, wxColor.Blue() / 255.0)
        for visible in self.visibles:
            visible.setColor(colorTuple)
    
    
    def onSetPositionIsFixed(self, event):
        newValue = self.fixedPositionCheckBox.GetValue()
        for visible in self.visibles:
            visible.setPositionIsFixed(newValue == wx.CHK_CHECKED)
