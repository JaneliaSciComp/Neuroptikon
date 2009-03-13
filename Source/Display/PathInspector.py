import wx, wx.lib.colourselect
import os, sys
from wx.py import dispatcher
from Inspection.Inspector import Inspector
from Network.ObjectList import ObjectList
from Visible import Visible


class PathInspector(Inspector):
    
    @classmethod
    def name(cls):
        return gettext('Path')
    
    
    @classmethod
    def bitmap(cls):
        displayDir = os.path.abspath(os.path.dirname(sys.modules['Display'].__file__))
        image = wx.Image(displayDir + os.sep + 'PathInspector.png')
        if image.IsOk():
            image.Rescale(16, 16)
            return image.ConvertToBitmap()
        else:
            return Inspector.bitmap(cls)
    
    
    @classmethod
    def canInspectDisplay(cls, display):
        for visible in display.selectedVisibles:
            if visible.isPath():
                return True
        return len(display.selectedVisibles) == 0


    def window(self, parentWindow=None):
        if not hasattr(self, '_window'):
            self._window = wx.Window(parentWindow, wx.ID_ANY)
            self._sizer = wx.BoxSizer(wx.VERTICAL)
            
            self._flowToBoxSizer = wx.StaticBoxSizer(wx.StaticBox(self._window, wx.ID_ANY, gettext('Flow to')), wx.HORIZONTAL)
            
            flowToGridSizer = wx.FlexGridSizer(3, 2, 8, 0)
            flowToGridSizer.SetFlexibleDirection(wx.HORIZONTAL)
            
            self._flowToCheckBox = wx.CheckBox(self._window, wx.ID_ANY, '', style=wx.CHK_3STATE)
            self._window.Bind(wx.EVT_CHECKBOX, self.onSetAnimateFlowTo, self._flowToCheckBox)
            flowToGridSizer.Add(wx.StaticText(self._window, wx.ID_ANY, gettext('Animate:')), 0)
            flowToGridSizer.Add(self._flowToCheckBox, 1)
            
            self._flowToColorPicker = wx.lib.colourselect.ColourSelect(self._window, wx.ID_ANY)
            self._window.Bind(wx.lib.colourselect.EVT_COLOURSELECT, self.onSetFlowToColor, self._flowToColorPicker)
            flowToGridSizer.Add(wx.StaticText(self._window, wx.ID_ANY, gettext('Color:')), 0)
            flowToGridSizer.Add(self._flowToColorPicker, 1)
            
            self._flowToSlider = wx.Slider(self._window, wx.ID_ANY, 10, 0, 100)
            self._flowToSlider.Bind(wx.EVT_SCROLL, self.onSetFlowToSpread, self._flowToSlider)
            flowToGridSizer.Add(wx.StaticText(self._window, wx.ID_ANY, gettext('Spread:')), 0)
            flowToGridSizer.Add(self._flowToSlider, 1)
            
            self._flowToBoxSizer.Add(flowToGridSizer, 1, wx.EXPAND)
            self._sizer.Add(self._flowToBoxSizer, 1, wx.EXPAND | wx.ALL, 5)
            
            self._flowFromBoxSizer = wx.StaticBoxSizer(wx.StaticBox(self._window, wx.ID_ANY, gettext('Flow from')), wx.HORIZONTAL)
            
            flowFromGridSizer = wx.FlexGridSizer(3, 2, 8, 0)
            flowFromGridSizer.SetFlexibleDirection(wx.HORIZONTAL)
            
            self._flowFromCheckBox = wx.CheckBox(self._window, wx.ID_ANY, '', style=wx.CHK_3STATE)
            self._window.Bind(wx.EVT_CHECKBOX, self.onSetAnimateFlowFrom, self._flowFromCheckBox)
            flowFromGridSizer.Add(wx.StaticText(self._window, wx.ID_ANY, gettext('Animate:')), 0)
            flowFromGridSizer.Add(self._flowFromCheckBox, 1)
            
            self._flowFromColorPicker = wx.lib.colourselect.ColourSelect(self._window, wx.ID_ANY)
            self._window.Bind(wx.lib.colourselect.EVT_COLOURSELECT, self.onSetFlowFromColor, self._flowFromColorPicker)
            flowFromGridSizer.Add(wx.StaticText(self._window, wx.ID_ANY, gettext('Color:')), 0)
            flowFromGridSizer.Add(self._flowFromColorPicker, 1)
            
            self._flowFromSlider = wx.Slider(self._window, wx.ID_ANY, 10, 0, 100)
            self._flowFromSlider.Bind(wx.EVT_SCROLL, self.onSetFlowFromSpread, self._flowFromSlider)
            flowFromGridSizer.Add(wx.StaticText(self._window, wx.ID_ANY, gettext('Spread:')), 0)
            flowFromGridSizer.Add(self._flowFromSlider, 1)
            
            self._flowFromBoxSizer.Add(flowFromGridSizer, 1, wx.EXPAND)
            self._sizer.Add(self._flowFromBoxSizer, 1, wx.EXPAND | wx.ALL, 5)
            
            self._window.SetSizer(self._sizer)
        
        return self._window

    
    def inspectDisplay(self, display):
        self.display = display
        self.paths = ObjectList()
        self.visibles = display.selection()
        for visible in self.visibles:
            if visible.isPath():
                self.paths.append(visible)
        for path in self.paths:
            for attributeName in ['flowTo', 'flowToColor', 'flowToSpread', 'flowFrom', 'flowFromColor', 'flowFromSpread']:
                dispatcher.connect(self.refreshGUI, ('set', attributeName), visible)
        self.refreshGUI()
    
    
    def refreshGUI(self, signal = ('set', None), **arguments):
        updatedAttribute = signal[1]
        
        usingDefault = len(self.paths) == 0
        
        if usingDefault:
            self._flowToBoxSizer.GetStaticBox().SetLabel(gettext('Default flow to'))
            self._flowFromBoxSizer.GetStaticBox().SetLabel(gettext('Default flow from'))
        else:
            if self.paths.haveEqualAttr('pathEnd.client'):
                flowToName = self.paths[0].pathEnd.client.name or gettext('<unnamed %s>') % ( self.paths[0].pathEnd.client.__class__.displayName())
            else:
                flowToName = gettext('multiple objects')
            self._flowToBoxSizer.GetStaticBox().SetLabel(gettext('Flow to %s') % (flowToName))
            if self.paths.haveEqualAttr('pathStart.client'):
                flowFromName = self.paths[0].pathStart.client.name or gettext('<unnamed %s>') % ( self.paths[0].pathStart.client.__class__.displayName())
            else:
                flowFromName = gettext('multiple objects')
            self._flowFromBoxSizer.GetStaticBox().SetLabel(gettext('Flow from %s') % (flowFromName))
        
        if updatedAttribute is None or updatedAttribute == 'flowTo':
            if usingDefault:
                self._flowToCheckBox.Set3StateValue(wx.CHK_UNCHECKED)
                self._flowToCheckBox.Disable()
            else:
                if self.paths.haveEqualAttr('flowTo'):
                    if self.paths[0].flowTo:
                        self._flowToCheckBox.Set3StateValue(wx.CHK_CHECKED)
                    else:
                        self._flowToCheckBox.Set3StateValue(wx.CHK_UNCHECKED)
                else:
                    self._flowToCheckBox.Set3StateValue(wx.CHK_UNDETERMINED)
                self._flowToCheckBox.Enable()
        
        if updatedAttribute is None or updatedAttribute == 'flowToColor':
            if usingDefault or self.paths.haveEqualAttr('flowToColor'):
                if usingDefault:
                    red, green, blue, alpha = self.display.defaultFlowToColor
                else:
                    red, green, blue, alpha = self.paths[0].flowToColor()
                self._flowToColorPicker.SetColour(wx.Color(red * 255, green * 255, blue * 255, alpha * 255))
                self._flowToColorPicker.SetLabel(gettext(''))
            else:
                self._flowToColorPicker.SetColour(wx.NamedColour('GRAY'))  # TODO: be clever and pick the average color?
                self._flowToColorPicker.SetLabel(gettext('Multiple values'))
        
        if updatedAttribute is None or updatedAttribute == 'flowToSpread':
            if usingDefault or self.paths.haveEqualAttr('flowToSpread'):
                if usingDefault:
                    spread = self.display.defaultFlowToSpread
                else:
                    spread = self.paths[0].flowToSpread()
                self._flowToSlider.SetLabel('')
                self._flowToSlider.SetValue(spread * 100.0)
            else:
                self._flowToSlider.SetLabel(gettext('Multiple values'))
                self._flowToSlider.SetValue(50)
        
        if updatedAttribute is None or updatedAttribute == 'flowFrom':
            if usingDefault:
                self._flowFromCheckBox.Set3StateValue(wx.CHK_UNCHECKED)
                self._flowFromCheckBox.Disable()
            else:
                if self.paths.haveEqualAttr('flowFrom'):
                    if self.paths[0].flowFrom:
                        self._flowFromCheckBox.Set3StateValue(wx.CHK_CHECKED)
                    else:
                        self._flowFromCheckBox.Set3StateValue(wx.CHK_UNCHECKED)
                else:
                    self._flowFromCheckBox.Set3StateValue(wx.CHK_UNDETERMINED)
                self._flowFromCheckBox.Enable()
        
        if updatedAttribute is None or updatedAttribute == 'flowFromColor':
            if usingDefault or self.paths.haveEqualAttr('flowFromColor'):
                if usingDefault:
                    red, green, blue, alpha = self.display.defaultFlowFromColor
                else:
                    red, green, blue, alpha = self.paths[0].flowFromColor()
                self._flowFromColorPicker.SetColour(wx.Color(red * 255, green * 255, blue * 255, alpha * 255))
                self._flowFromColorPicker.SetLabel(gettext(''))
            else:
                self._flowFromColorPicker.SetColour(wx.NamedColour('GRAY'))  # TODO: be clever and pick the average color?
                self._flowFromColorPicker.SetLabel(gettext('Multiple values'))
        
        if updatedAttribute is None or updatedAttribute == 'flowFromSpread':
            if usingDefault or self.paths.haveEqualAttr('flowFromSpread'):
                if usingDefault:
                    spread = self.display.defaultFlowFromSpread
                else:
                    spread = self.paths[0].flowFromSpread()
                self._flowFromSlider.SetLabel('')
                self._flowFromSlider.SetValue(spread * 100.0)
            else:
                self._flowFromSlider.SetLabel(gettext('Multiple values'))
                self._flowFromSlider.SetValue(50)
        
        self._window.Layout()
    
    
    def onSetAnimateFlowTo(self, event):
        newValue = self._flowToCheckBox.GetValue()
        for path in self.paths:
            path.setFlowDirection(path.pathStart, path.pathEnd, newValue == wx.CHK_CHECKED, path.flowFrom)
    
    
    def onSetFlowToColor(self, event):
        wxColor = self._flowToColorPicker.GetColour()
        newColor = (wxColor.Red() / 255.0, wxColor.Green() / 255.0, wxColor.Blue() / 255.0, wxColor.Alpha() / 255.0)
        if len(self.paths) == 0:
            self.display.setDefaultFlowToColor(newColor)
        else:
            for path in self.paths:
                path.setFlowToColor(newColor)
        
    
    def onSetFlowToSpread(self, event):
        newSpread = self._flowToSlider.GetValue() / 100.0
        if len(self.paths) == 0:
            self.display.setDefaultFlowToSpread(newSpread)
        else:
            for path in self.paths:
                path.setFlowToSpread(newSpread)
    
    
    def onSetAnimateFlowFrom(self, event):
        newValue = self._flowFromCheckBox.GetValue()
        for path in self.paths:
            path.setFlowDirection(path.pathStart, path.pathEnd, path.flowTo, newValue == wx.CHK_CHECKED)
    
    
    def onSetFlowFromColor(self, event):
        wxColor = self._flowFromColorPicker.GetColour()
        newColor = (wxColor.Red() / 255.0, wxColor.Green() / 255.0, wxColor.Blue() / 255.0, wxColor.Alpha() / 255.0)
        if len(self.paths) == 0:
            self.display.setDefaultFlowFromColor(newColor)
        else:
            for path in self.paths:
                path.setFlowFromColor(newColor)
        
    
    def onSetFlowFromSpread(self, event):
        newSpread = self._flowFromSlider.GetValue() / 100.0
        if len(self.paths) == 0:
            self.display.setDefaultFlowFromSpread(newSpread)
        else:
            for path in self.paths:
                path.setFlowFromSpread(newSpread)
  
