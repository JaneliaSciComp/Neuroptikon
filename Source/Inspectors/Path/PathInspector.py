import wx, wx.lib.colourselect
from wx.py import dispatcher
from Inspection.Inspector import Inspector
from Network.ObjectList import ObjectList
from Display.Visible import Visible


class PathInspector(Inspector):
    
    @classmethod
    def name(cls):
        return gettext('Path')
    
    
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
            self._flowToLabel = wx.StaticText(self._window, wx.ID_ANY, gettext('Animate:'))
            flowToGridSizer.Add(self._flowToLabel, 0)
            flowToGridSizer.Add(self._flowToCheckBox, 1)
            
            self._flowToColorPicker = wx.lib.colourselect.ColourSelect(self._window, wx.ID_ANY)
            self._window.Bind(wx.lib.colourselect.EVT_COLOURSELECT, self.onSetFlowToColor, self._flowToColorPicker)
            flowToGridSizer.Add(wx.StaticText(self._window, wx.ID_ANY, gettext('Color:')), 0)
            flowToGridSizer.Add(self._flowToColorPicker, 1)
            
            self._flowToSpacingSlider = wx.Slider(self._window, wx.ID_ANY, 0, -99, 99)
            self._flowToSpacingSlider.Bind(wx.EVT_SCROLL, self.onSetFlowToSpacing, self._flowToSpacingSlider)
            flowToGridSizer.Add(wx.StaticText(self._window, wx.ID_ANY, gettext('Spacing:')), 0)
            flowToGridSizer.Add(self._flowToSpacingSlider, 1)
            
            self._flowToSpeedSlider = wx.Slider(self._window, wx.ID_ANY, 0, -99, 99)
            self._flowToSpeedSlider.Bind(wx.EVT_SCROLL, self.onSetFlowToSpeed, self._flowToSpeedSlider)
            flowToGridSizer.Add(wx.StaticText(self._window, wx.ID_ANY, gettext('Speed:')), 0)
            flowToGridSizer.Add(self._flowToSpeedSlider, 1)
            
            self._flowToSpreadSlider = wx.Slider(self._window, wx.ID_ANY, 10, 0, 100)
            self._flowToSpreadSlider.Bind(wx.EVT_SCROLL, self.onSetFlowToSpread, self._flowToSpreadSlider)
            flowToGridSizer.Add(wx.StaticText(self._window, wx.ID_ANY, gettext('Spread:')), 0)
            flowToGridSizer.Add(self._flowToSpreadSlider, 1)
            
            self._flowToBoxSizer.Add(flowToGridSizer, 1, wx.EXPAND)
            self._sizer.Add(self._flowToBoxSizer, 1, wx.EXPAND | wx.ALL, 5)
            
            self._flowFromBoxSizer = wx.StaticBoxSizer(wx.StaticBox(self._window, wx.ID_ANY, gettext('Flow to')), wx.HORIZONTAL)
            
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
            
            self._flowFromSpacingSlider = wx.Slider(self._window, wx.ID_ANY, 0, -50, 50)
            self._flowFromSpacingSlider.Bind(wx.EVT_SCROLL, self.onSetFlowFromSpacing, self._flowFromSpacingSlider)
            flowFromGridSizer.Add(wx.StaticText(self._window, wx.ID_ANY, gettext('Spacing:')), 0)
            flowFromGridSizer.Add(self._flowFromSpacingSlider, 1)
            
            self._flowFromSpeedSlider = wx.Slider(self._window, wx.ID_ANY, 0, -50, 50)
            self._flowFromSpeedSlider.Bind(wx.EVT_SCROLL, self.onSetFlowFromSpeed, self._flowFromSpeedSlider)
            flowFromGridSizer.Add(wx.StaticText(self._window, wx.ID_ANY, gettext('Speed:')), 0)
            flowFromGridSizer.Add(self._flowFromSpeedSlider, 1)
            
            self._flowFromSpreadSlider = wx.Slider(self._window, wx.ID_ANY, 10, 0, 100)
            self._flowFromSpreadSlider.Bind(wx.EVT_SCROLL, self.onSetFlowFromSpread, self._flowFromSpreadSlider)
            flowFromGridSizer.Add(wx.StaticText(self._window, wx.ID_ANY, gettext('Spread:')), 0)
            flowFromGridSizer.Add(self._flowFromSpreadSlider, 1)
            
            self._flowFromBoxSizer.Add(flowFromGridSizer, 1, wx.EXPAND)
            self._sizer.Add(self._flowFromBoxSizer, 1, wx.EXPAND | wx.ALL, 5)
            
            self._window.SetSizer(self._sizer)
        
        return self._window

    
    def inspectDisplay(self, display):
        self.display = display
        
        # Get the subset of visibles that are paths.
        self.paths = ObjectList()
        self.visibles = display.selection()
        for visible in self.visibles:
            if visible.isPath():
                self.paths.append(visible)
        
        if len(self.paths) == 0:
            self._flowToLabel.Hide()
            self._flowToCheckBox.Hide()
            self._sizer.Hide(self._flowFromBoxSizer, True)
            dispatcher.connect(self.refreshGUI, ('set', 'defaultFlowColor'), self.display)
            dispatcher.connect(self.refreshGUI, ('set', 'defaultFlowSpread'), self.display)
        else:
            self._flowToLabel.Show()
            self._flowToCheckBox.Show()
            self._sizer.Show(self._flowFromBoxSizer, True)
            for path in self.paths:
                for attributeName in ['flowTo', 'flowToColor', 'flowToSpread', 'flowFrom', 'flowFromColor', 'flowFromSpread']:
                    dispatcher.connect(self.refreshGUI, ('set', attributeName), visible)
        self._flowToBoxSizer.Layout()
        self.refreshGUI()
    
    
    def refreshGUI(self, signal = ('set', None), **arguments):
        updatedAttribute = signal[1]
        
        usingDefault = len(self.paths) == 0
        
        if usingDefault:
            self._flowToBoxSizer.GetStaticBox().SetLabel(gettext('Default flow appearance'))
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
            self._flowFromBoxSizer.GetStaticBox().SetLabel(gettext('Flow to %s') % (flowFromName))
        
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
        
        if updatedAttribute is None or updatedAttribute == 'flowToColor' or updatedAttribute == 'defaultFlowColor':
            if usingDefault or self.paths.haveEqualAttr('flowToColor'):
                if usingDefault:
                    red, green, blue, alpha = self.display.defaultFlowColor
                else:
                    red, green, blue, alpha = self.paths[0].flowToColor()
                self._flowToColorPicker.SetColour(wx.Color(red * 255, green * 255, blue * 255, alpha * 255))
                self._flowToColorPicker.SetLabel(gettext(''))
            else:
                self._flowToColorPicker.SetColour(wx.NamedColour('GRAY'))  # TODO: be clever and pick the average color?
                self._flowToColorPicker.SetLabel(gettext('Multiple values'))
        
        if updatedAttribute is None or updatedAttribute == 'flowToSpacing' or updatedAttribute == 'defaultFlowSpacing':
            if usingDefault or self.paths.haveEqualAttr('flowToSpacing'):
                if usingDefault:
                    spacing = self.display.defaultFlowSpacing
                else:
                    spacing = self.paths[0].flowToSpacing()
                self._flowToSpacingSlider.SetLabel('')
                if spacing < 1.0:
                    self._flowToSpacingSlider.SetValue(99 * (spacing - 1.0) / 0.9)
                else:
                    self._flowToSpacingSlider.SetValue(99 * (spacing - 1.0) / 9.0)
            else:
                self._flowToSpacingSlider.SetLabel(gettext('Multiple values'))
                self._flowToSpacingSlider.SetValue(0)
        
        if updatedAttribute is None or updatedAttribute == 'flowToSpeed' or updatedAttribute == 'defaultFlowSpeed':
            if usingDefault or self.paths.haveEqualAttr('flowToSpeed'):
                if usingDefault:
                    speed = self.display.defaultFlowSpeed
                else:
                    speed = self.paths[0].flowToSpeed()
                self._flowToSpeedSlider.SetLabel('')
                if speed < 1.0:
                    self._flowToSpeedSlider.SetValue(99 * (speed - 1.0) / 0.9)
                else:
                    self._flowToSpeedSlider.SetValue(99 * (speed - 1.0) / 9.0)
            else:
                self._flowToSpeedSlider.SetLabel(gettext('Multiple values'))
                self._flowToSpeedSlider.SetValue(0)
        
        if updatedAttribute is None or updatedAttribute == 'flowToSpread' or updatedAttribute == 'defaultFlowSpread':
            if usingDefault or self.paths.haveEqualAttr('flowToSpread'):
                if usingDefault:
                    spread = self.display.defaultFlowSpread
                else:
                    spread = self.paths[0].flowToSpread()
                self._flowToSpreadSlider.SetLabel('')
                self._flowFromSpreadSlider.SetValue(spread * 100.0)
            else:
                self._flowToSpreadSlider.SetLabel(gettext('Multiple values'))
                self._flowToSpreadSlider.SetValue(50)
        
        if (updatedAttribute is None or updatedAttribute == 'flowFrom') and not usingDefault:
            if self.paths.haveEqualAttr('flowFrom'):
                if self.paths[0].flowFrom:
                    self._flowFromCheckBox.Set3StateValue(wx.CHK_CHECKED)
                else:
                    self._flowFromCheckBox.Set3StateValue(wx.CHK_UNCHECKED)
            else:
                self._flowFromCheckBox.Set3StateValue(wx.CHK_UNDETERMINED)
            self._flowFromCheckBox.Enable()
        
        if (updatedAttribute is None or updatedAttribute == 'flowFromColor') and not usingDefault:
            if self.paths.haveEqualAttr('flowFromColor'):
                red, green, blue, alpha = self.paths[0].flowFromColor()
                self._flowFromColorPicker.SetColour(wx.Color(red * 255, green * 255, blue * 255, alpha * 255))
                self._flowFromColorPicker.SetLabel(gettext(''))
            else:
                self._flowFromColorPicker.SetColour(wx.NamedColour('GRAY'))  # TODO: be clever and pick the average color?
                self._flowFromColorPicker.SetLabel(gettext('Multiple values'))
        
        if updatedAttribute is None or updatedAttribute == 'flowFromSpacing' or updatedAttribute == 'defaultFlowSpacing':
            if usingDefault or self.paths.haveEqualAttr('flowFromSpacing'):
                if usingDefault:
                    spacing = self.display.defaultFlowSpacing
                else:
                    spacing = self.paths[0].flowFromSpacing()
                self._flowFromSpacingSlider.SetLabel('')
                if spacing < 1.0:
                    self._flowFromSpacingSlider.SetValue(99 * (spacing - 1.0) / 0.9)
                else:
                    self._flowFromSpacingSlider.SetValue(99 * (spacing - 1.0) / 9.0)
            else:
                self._flowFromSpacingSlider.SetLabel(gettext('Multiple values'))
                self._flowFromSpacingSlider.SetValue(0)
        
        if updatedAttribute is None or updatedAttribute == 'flowFromSpeed' or updatedAttribute == 'defaultFlowSpeed':
            if usingDefault or self.paths.haveEqualAttr('flowFromSpeed'):
                if usingDefault:
                    speed = self.display.defaultFlowSpeed
                else:
                    speed = self.paths[0].flowFromSpeed()
                self._flowFromSpeedSlider.SetLabel('')
                if speed < 1.0:
                    self._flowFromSpeedSlider.SetValue(99 * (speed - 1.0) / 0.9)
                else:
                    self._flowFromSpeedSlider.SetValue(99 * (speed - 1.0) / 9.0)
            else:
                self._flowFromSpeedSlider.SetLabel(gettext('Multiple values'))
                self._flowFromSpeedSlider.SetValue(0)
        
        if (updatedAttribute is None or updatedAttribute == 'flowFromSpread') and not usingDefault:
            if self.paths.haveEqualAttr('flowFromSpread'):
                spread = self.paths[0].flowFromSpread()
                self._flowFromSpreadSlider.SetLabel('')
                self._flowFromSpreadSlider.SetValue(spread * 100.0)
            else:
                self._flowFromSpreadSlider.SetLabel(gettext('Multiple values'))
                self._flowFromSpreadSlider.SetValue(50)
        
        self._window.Layout()
    
    
    def onSetAnimateFlowTo(self, event):
        newValue = self._flowToCheckBox.GetValue()
        for path in self.paths:
            path.setFlowDirection(path.pathStart, path.pathEnd, newValue == wx.CHK_CHECKED, path.flowFrom)
    
    
    def onSetFlowToColor(self, event):
        wxColor = self._flowToColorPicker.GetColour()
        newColor = (wxColor.Red() / 255.0, wxColor.Green() / 255.0, wxColor.Blue() / 255.0, wxColor.Alpha() / 255.0)
        if len(self.paths) == 0:
            self.display.setDefaultFlowColor(newColor)
        else:
            for path in self.paths:
                path.setFlowToColor(newColor)
        
    
    def onSetFlowToSpacing(self, event):
        newSpacing = self._flowToSpacingSlider.GetValue()
        if newSpacing < 0:
           newSpacing = 1.0 + 0.9 * newSpacing / 99.0
        else:
           newSpacing = 1.0 + 9.0 * newSpacing / 99.0
        if len(self.paths) == 0:
            self.display.setDefaultFlowSpacing(newSpacing)
        else:
            for path in self.paths:
                path.setFlowToSpacing(newSpacing)
    
    
    def onSetFlowToSpeed(self, event):
        newSpeed = self._flowToSpeedSlider.GetValue()
        if newSpeed < 0:
           newSpeed = 1.0 + 0.9 * newSpeed / 99.0
        else:
           newSpeed = 1.0 + 9.0 * newSpeed / 99.0
        if len(self.paths) == 0:
            self.display.setDefaultFlowSpeed(newSpeed)
        else:
            for path in self.paths:
                path.setFlowToSpeed(newSpeed)
    
    
    def onSetFlowToSpread(self, event):
        newSpread = self._flowToSpreadSlider.GetValue() / 100.0
        if len(self.paths) == 0:
            self.display.setDefaultFlowSpread(newSpread)
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
        for path in self.paths:
            path.setFlowFromColor(newColor)
        
    
    def onSetFlowFromSpacing(self, event):
        newSpacing = self._flowFromSpacingSlider.GetValue()
        if newSpacing < 0:
           newSpacing = 1.0 + 0.9 * newSpacing / 99.0
        else:
           newSpacing = 1.0 + 9.0 * newSpacing / 99.0
        if len(self.paths) == 0:
            self.display.setDefaultFlowSpacing(newSpacing)
        else:
            for path in self.paths:
                path.setFlowFromSpacing(newSpacing)
    
    
    def onSetFlowFromSpeed(self, event):
        newSpeed = self._flowFromSpeedSlider.GetValue()
        if newSpeed < 0:
           newSpeed = 1.0 + 0.9 * newSpeed / 99.0
        else:
           newSpeed = 1.0 + 9.0 * newSpeed / 99.0
        if len(self.paths) == 0:
            self.display.setDefaultFlowSpeed(newSpeed)
        else:
            for path in self.paths:
                path.setFlowFromSpeed(newSpeed)
        
    
    def onSetFlowFromSpread(self, event):
        newSpread = self._flowFromSpreadSlider.GetValue() / 100.0
        for path in self.paths:
            path.setFlowFromSpread(newSpread)
  
