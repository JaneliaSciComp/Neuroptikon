import wx, wx.lib.colourselect
from wx.py import dispatcher
from Inspection.Inspector import Inspector
from Network.ObjectList import ObjectList
from Display.Visible import Visible
from math import e, log, sqrt


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
            flowToGridSizer.AddGrowableCol(1, 1)
            
            self._flowToCheckBox = wx.CheckBox(self._window, wx.ID_ANY, '', style=wx.CHK_3STATE)
            self._window.Bind(wx.EVT_CHECKBOX, self.onSetAnimateFlowTo, self._flowToCheckBox)
            self._flowToLabel = wx.StaticText(self._window, wx.ID_ANY, gettext('Animate:'))
            flowToGridSizer.Add(self._flowToLabel, 0)
            flowToGridSizer.Add(self._flowToCheckBox, 1)
            
            self._flowToColorPicker = wx.lib.colourselect.ColourSelect(self._window, wx.ID_ANY)
            self._window.Bind(wx.lib.colourselect.EVT_COLOURSELECT, self.onSetFlowToColor, self._flowToColorPicker)
            flowToGridSizer.Add(wx.StaticText(self._window, wx.ID_ANY, gettext('Color:')), 0)
            flowToGridSizer.Add(self._flowToColorPicker, 1)
            
            self._flowToSpacingSlider = wx.Slider(self._window, wx.ID_ANY, 100, 0, 1000)
            self._flowToSpacingSlider.Bind(wx.EVT_SCROLL, self.onSetFlowToSpacing, self._flowToSpacingSlider)
            flowToGridSizer.Add(wx.StaticText(self._window, wx.ID_ANY, gettext('Spacing:')), 0)
            flowToGridSizer.Add(self._flowToSpacingSlider, 1, wx.EXPAND)
            
            self._flowToSpeedSlider = wx.Slider(self._window, wx.ID_ANY, 100, 0, 1000)
            self._flowToSpeedSlider.Bind(wx.EVT_SCROLL, self.onSetFlowToSpeed, self._flowToSpeedSlider)
            flowToGridSizer.Add(wx.StaticText(self._window, wx.ID_ANY, gettext('Speed:')), 0)
            flowToGridSizer.Add(self._flowToSpeedSlider, 1, wx.EXPAND)
            
            self._flowToSpreadSlider = wx.Slider(self._window, wx.ID_ANY, 25, 0, 100)
            self._flowToSpreadSlider.Bind(wx.EVT_SCROLL, self.onSetFlowToSpread, self._flowToSpreadSlider)
            flowToGridSizer.Add(wx.StaticText(self._window, wx.ID_ANY, gettext('Spread:')), 0)
            flowToGridSizer.Add(self._flowToSpreadSlider, 1, wx.EXPAND)
            
            self._flowToBoxSizer.Add(flowToGridSizer, 1, wx.EXPAND)
            self._sizer.Add(self._flowToBoxSizer, 1, wx.EXPAND | wx.ALL, 5)
            
            self._flowFromBoxSizer = wx.StaticBoxSizer(wx.StaticBox(self._window, wx.ID_ANY, gettext('Flow to')), wx.HORIZONTAL)
            
            flowFromGridSizer = wx.FlexGridSizer(3, 2, 8, 0)
            flowFromGridSizer.SetFlexibleDirection(wx.HORIZONTAL)
            flowFromGridSizer.AddGrowableCol(1, 1)
            
            self._flowFromCheckBox = wx.CheckBox(self._window, wx.ID_ANY, '', style=wx.CHK_3STATE)
            self._window.Bind(wx.EVT_CHECKBOX, self.onSetAnimateFlowFrom, self._flowFromCheckBox)
            flowFromGridSizer.Add(wx.StaticText(self._window, wx.ID_ANY, gettext('Animate:')), 0)
            flowFromGridSizer.Add(self._flowFromCheckBox, 1)
            
            self._flowFromColorPicker = wx.lib.colourselect.ColourSelect(self._window, wx.ID_ANY)
            self._window.Bind(wx.lib.colourselect.EVT_COLOURSELECT, self.onSetFlowFromColor, self._flowFromColorPicker)
            flowFromGridSizer.Add(wx.StaticText(self._window, wx.ID_ANY, gettext('Color:')), 0)
            flowFromGridSizer.Add(self._flowFromColorPicker, 1)
            
            self._flowFromSpacingSlider = wx.Slider(self._window, wx.ID_ANY, 100, 0, 1000)
            self._flowFromSpacingSlider.Bind(wx.EVT_SCROLL, self.onSetFlowFromSpacing, self._flowFromSpacingSlider)
            flowFromGridSizer.Add(wx.StaticText(self._window, wx.ID_ANY, gettext('Spacing:')), 0)
            flowFromGridSizer.Add(self._flowFromSpacingSlider, 1, wx.EXPAND)
            
            self._flowFromSpeedSlider = wx.Slider(self._window, wx.ID_ANY, 100, 0, 1000)
            self._flowFromSpeedSlider.Bind(wx.EVT_SCROLL, self.onSetFlowFromSpeed, self._flowFromSpeedSlider)
            flowFromGridSizer.Add(wx.StaticText(self._window, wx.ID_ANY, gettext('Speed:')), 0)
            flowFromGridSizer.Add(self._flowFromSpeedSlider, 1, wx.EXPAND)
            
            self._flowFromSpreadSlider = wx.Slider(self._window, wx.ID_ANY, 25, 0, 100)
            self._flowFromSpreadSlider.Bind(wx.EVT_SCROLL, self.onSetFlowFromSpread, self._flowFromSpreadSlider)
            flowFromGridSizer.Add(wx.StaticText(self._window, wx.ID_ANY, gettext('Spread:')), 0)
            flowFromGridSizer.Add(self._flowFromSpreadSlider, 1, wx.EXPAND)
            
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
        
        self.refreshGUI()
    
    
    def reasonableSpacingOrSpeed(self):
        # Compute some reasonable spacing/speed based on the bounding box of the visibles in the display.
        self.display.computeVisiblesBound()
        return sqrt(self.display.visiblesSize[0] ** 2 + self.display.visiblesSize[1] ** 2 + self.display.visiblesSize[2] ** 2) / 20.0
    
    
    def refreshGUI(self, signal = ('set', None), **arguments):
        updatedAttribute = signal[1]
        
        usingDefault = len(self.paths) == 0
        
        # The spacing and speed sliders are mapped logarithmically so very small and very large values can be used.
        # The scale is set so that a reasonable spacing and speed are used when the slider is at the midpoint.
        # Unfortunately what is "reasonable" is dependent on the bounding box of the whole display which can change at any time.
        expBase = e ** (log(self.reasonableSpacingOrSpeed() + 1.0) / 500.0)
        
        if usingDefault:
            self._flowToBoxSizer.GetStaticBox().SetLabel(gettext('Default flow appearance'))
        else:
            if len(self.paths) == 1:
                (startPoint, endPoint) = self.paths[0].pathEndPoints()
                flowToName = gettext('ananymous object') if endPoint.client == None else endPoint.client.name or gettext('<unnamed %s>') % ( endPoint.client.__class__.displayName())
                flowFromName = gettext('ananymous object') if startPoint.client == None else startPoint.client.name or gettext('<unnamed %s>') % ( startPoint.client.__class__.displayName())
            else:
                flowToName = gettext('multiple objects')
                flowFromName = gettext('multiple objects')
            self._flowToBoxSizer.GetStaticBox().SetLabel(gettext('Flow to %s') % (flowToName))
            self._flowFromBoxSizer.GetStaticBox().SetLabel(gettext('Flow to %s') % (flowFromName))
        
        if updatedAttribute is None or updatedAttribute == 'flowTo':
            if usingDefault:
                self._flowToCheckBox.Set3StateValue(wx.CHK_UNCHECKED)
                self._flowToCheckBox.Disable()
            else:
                if self.paths.haveEqualAttr('flowTo'):
                    if self.paths[0].flowTo():
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
                    red, green, blue, alpha = self.paths[0].flowToColor() or self.display.defaultFlowColor
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
                    spacing = self.paths[0].flowToSpacing() or self.display.defaultFlowSpacing
                self._flowToSpacingSlider.SetLabel('')
                self._flowToSpacingSlider.SetValue(log(spacing + 1.0, expBase))
            else:
                self._flowToSpacingSlider.SetLabel(gettext('Multiple values'))
                self._flowToSpacingSlider.SetValue(0)
        
        if updatedAttribute is None or updatedAttribute == 'flowToSpeed' or updatedAttribute == 'defaultFlowSpeed':
            if usingDefault or self.paths.haveEqualAttr('flowToSpeed'):
                if usingDefault:
                    speed = self.display.defaultFlowSpeed
                else:
                    speed = self.paths[0].flowToSpeed() or self.display.defaultFlowSpeed
                self._flowToSpeedSlider.SetLabel('')
                self._flowToSpeedSlider.SetValue(log(speed + 1.0, expBase))
            else:
                self._flowToSpeedSlider.SetLabel(gettext('Multiple values'))
                self._flowToSpeedSlider.SetValue(0)
        
        if updatedAttribute is None or updatedAttribute == 'flowToSpread' or updatedAttribute == 'defaultFlowSpread':
            if usingDefault or self.paths.haveEqualAttr('flowToSpread'):
                if usingDefault:
                    spread = self.display.defaultFlowSpread
                else:
                    spread = self.paths[0].flowToSpread() or self.display.defaultFlowSpread
                self._flowToSpreadSlider.SetLabel('')
                self._flowToSpreadSlider.SetValue(spread * 50.0)
            else:
                self._flowToSpreadSlider.SetLabel(gettext('Multiple values'))
                self._flowToSpreadSlider.SetValue(50)
        
        if (updatedAttribute is None or updatedAttribute == 'flowFrom') and not usingDefault:
            if self.paths.haveEqualAttr('flowFrom'):
                if self.paths[0].flowFrom():
                    self._flowFromCheckBox.Set3StateValue(wx.CHK_CHECKED)
                else:
                    self._flowFromCheckBox.Set3StateValue(wx.CHK_UNCHECKED)
            else:
                self._flowFromCheckBox.Set3StateValue(wx.CHK_UNDETERMINED)
            self._flowFromCheckBox.Enable()
        
        if (updatedAttribute is None or updatedAttribute == 'flowFromColor') and not usingDefault:
            if usingDefault or self.paths.haveEqualAttr('flowFromColor'):
                if usingDefault:
                    red, green, blue, alpha = self.display.defaultFlowColor
                else:
                    red, green, blue, alpha = self.paths[0].flowFromColor() or self.display.defaultFlowColor
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
                    spacing = self.paths[0].flowFromSpacing() or self.display.defaultFlowSpacing
                self._flowFromSpacingSlider.SetLabel('')
                self._flowFromSpacingSlider.SetValue(log(spacing + 1.0, expBase))
            else:
                self._flowFromSpacingSlider.SetLabel(gettext('Multiple values'))
                self._flowFromSpacingSlider.SetValue(0)
        
        if updatedAttribute is None or updatedAttribute == 'flowFromSpeed' or updatedAttribute == 'defaultFlowSpeed':
            if usingDefault or self.paths.haveEqualAttr('flowFromSpeed'):
                if usingDefault:
                    speed = self.display.defaultFlowSpeed
                else:
                    speed = self.paths[0].flowFromSpeed() or self.display.defaultFlowSpeed
                self._flowFromSpeedSlider.SetLabel('')
                self._flowFromSpeedSlider.SetValue(log(speed + 1.0, expBase))
            else:
                self._flowFromSpeedSlider.SetLabel(gettext('Multiple values'))
                self._flowFromSpeedSlider.SetValue(0)
        
        if (updatedAttribute is None or updatedAttribute == 'flowFromSpread') and not usingDefault:
            if usingDefault or self.paths.haveEqualAttr('flowFromSpread'):
                if usingDefault:
                    spread = self.display.defaultFlowSpread
                else:
                    spread = self.paths[0].flowFromSpread() or self.display.defaultFlowSpread
                self._flowFromSpreadSlider.SetLabel('')
                self._flowFromSpreadSlider.SetValue(spread * 50.0)
            else:
                self._flowFromSpreadSlider.SetLabel(gettext('Multiple values'))
                self._flowFromSpreadSlider.SetValue(50)
        
        self._window.Layout()
    
    
    def onSetAnimateFlowTo(self, event):
        newValue = self._flowToCheckBox.GetValue()
        for path in self.paths:
            path.setFlowTo(newValue == wx.CHK_CHECKED)
    
    
    def onSetFlowToColor(self, event):
        wxColor = self._flowToColorPicker.GetColour()
        newColor = (wxColor.Red() / 255.0, wxColor.Green() / 255.0, wxColor.Blue() / 255.0, wxColor.Alpha() / 255.0)
        if len(self.paths) == 0:
            self.display.setDefaultFlowColor(newColor)
        else:
            for path in self.paths:
                path.setFlowToColor(newColor)
        
    
    def onSetFlowToSpacing(self, event):
        expBase = e ** (log(self.reasonableSpacingOrSpeed() + 1.0) / 500.0)
        newSpacing = expBase ** self._flowToSpacingSlider.GetValue() - 1.0
        if len(self.paths) == 0:
            self.display.setDefaultFlowSpacing(newSpacing)
        else:
            for path in self.paths:
                path.setFlowToSpacing(newSpacing)
        wx.GetApp().Yield()
    
    
    def onSetFlowToSpeed(self, event):
        expBase = e ** (log(self.reasonableSpacingOrSpeed() + 1.0) / 500.0)
        newSpeed = expBase ** self._flowToSpeedSlider.GetValue() - 1.0
        if len(self.paths) == 0:
            self.display.setDefaultFlowSpeed(newSpeed)
        else:
            for path in self.paths:
                path.setFlowToSpeed(newSpeed)
        wx.GetApp().Yield()
    
    
    def onSetFlowToSpread(self, event):
        newSpread = self._flowToSpreadSlider.GetValue() / 50.0
        if len(self.paths) == 0:
            self.display.setDefaultFlowSpread(newSpread)
        else:
            for path in self.paths:
                path.setFlowToSpread(newSpread)
    
    
    def onSetAnimateFlowFrom(self, event):
        newValue = self._flowFromCheckBox.GetValue()
        for path in self.paths:
            path.setFlowFrom(newValue == wx.CHK_CHECKED)
    
    
    def onSetFlowFromColor(self, event):
        wxColor = self._flowFromColorPicker.GetColour()
        newColor = (wxColor.Red() / 255.0, wxColor.Green() / 255.0, wxColor.Blue() / 255.0, wxColor.Alpha() / 255.0)
        for path in self.paths:
            path.setFlowFromColor(newColor)
        
    
    def onSetFlowFromSpacing(self, event):
        expBase = e ** (log(self.reasonableSpacingOrSpeed() + 1.0) / 500.0)
        newSpacing = expBase ** self._flowFromSpacingSlider.GetValue() - 1.0
        if len(self.paths) == 0:
            self.display.setDefaultFlowSpacing(newSpacing)
        else:
            for path in self.paths:
                path.setFlowFromSpacing(newSpacing)
    
    
    def onSetFlowFromSpeed(self, event):
        expBase = e ** (log(self.reasonableSpacingOrSpeed() + 1.0) / 500.0)
        newSpeed = expBase ** self._flowFromSpeedSlider.GetValue() - 1.0
        if len(self.paths) == 0:
            self.display.setDefaultFlowSpeed(newSpeed)
        else:
            for path in self.paths:
                path.setFlowFromSpeed(newSpeed)
        
    
    def onSetFlowFromSpread(self, event):
        newSpread = self._flowFromSpreadSlider.GetValue() / 50.0
        for path in self.paths:
            path.setFlowFromSpread(newSpread)
  
