import wx
from pydispatch import dispatcher
from inspection.inspector import Inspector
from network.object_list import ObjectList
from display.visible import Visible


class GeometryInspector(Inspector):
    
    @classmethod
    def name(cls):
        return gettext('Geometry')
    
    
    @classmethod
    def canInspectDisplay(cls, display):
        return display and any(display.selection())


    def window(self, parentWindow=None):
        if not hasattr(self, '_window'):
            self._window = wx.Window(parentWindow, wx.ID_ANY)
            gridSizer = wx.FlexGridSizer(3, 2, 8, 8)
            
            # Add a check box for fixing the position.
            self.fixedPositionCheckBox = wx.CheckBox(self._window, wx.ID_ANY, gettext('Fixed'), style=wx.CHK_3STATE)
            self._window.Bind(wx.EVT_CHECKBOX, self.onSetPositionIsFixed, self.fixedPositionCheckBox)
            gridSizer.Add(wx.StaticText(self._window, wx.ID_ANY, gettext('Position:')), 0)
            gridSizer.Add(self.fixedPositionCheckBox, 1)
            
            # Add a check box for fixing the size.
            self.fixedSizeCheckBox = wx.CheckBox(self._window, wx.ID_ANY, gettext('Fixed'), style=wx.CHK_3STATE)
            self._window.Bind(wx.EVT_CHECKBOX, self.onSetSizeIsFixed, self.fixedSizeCheckBox)
            gridSizer.Add(wx.StaticText(self._window, wx.ID_ANY, gettext('Size:')), 0)
            gridSizer.Add(self.fixedSizeCheckBox, 1)
            
            # TODO: controls for position, size, rotation, sizeIsAbsolute, ???
            
            mainSizer = wx.BoxSizer(wx.VERTICAL)
            mainSizer.Add(gridSizer, 1, wx.ALL, 5)
            self._window.SetSizer(mainSizer)
        
        return self._window
    
    
    def inspectDisplay(self, display):
        self.visibles = display.selection()
        for visible in self.visibles:
            for attributeName in ['position', 'positionIsFixed', 'size', 'sizeIsFixed', 'sizeIsAbsolute', 'rotation']:
                dispatcher.connect(self.refreshGUI, ('set', attributeName), visible)
        self.refreshGUI()
    
    
    def refreshGUI(self, signal = ('set', None), **arguments):
        updatedAttribute = signal[1]
        
        if updatedAttribute is None or updatedAttribute == 'positionIsFixed':
            if self.visibles.haveEqualAttr('positionIsFixed'):
                if self.visibles[0].positionIsFixed():
                    self.fixedPositionCheckBox.Set3StateValue(wx.CHK_CHECKED)
                else:
                    self.fixedPositionCheckBox.Set3StateValue(wx.CHK_UNCHECKED)
            else:
                self.fixedPositionCheckBox.Set3StateValue(wx.CHK_UNDETERMINED)
        
        if updatedAttribute is None or updatedAttribute == 'sizeIsFixed':
            if self.visibles.haveEqualAttr('sizeIsFixed'):
                if self.visibles[0].sizeIsFixed():
                    self.fixedSizeCheckBox.Set3StateValue(wx.CHK_CHECKED)
                else:
                    self.fixedSizeCheckBox.Set3StateValue(wx.CHK_UNCHECKED)
            else:
                self.fixedSizeCheckBox.Set3StateValue(wx.CHK_UNDETERMINED)
        
        self._window.Layout()
    
    
    def onSetPositionIsFixed(self, event):
        newValue = self.fixedPositionCheckBox.GetValue()
        for visible in self.visibles:
            visible.setPositionIsFixed(newValue == wx.CHK_CHECKED)
    
    
    def onSetSizeIsFixed(self, event):
        newValue = self.fixedSizeCheckBox.GetValue()
        for visible in self.visibles:
            visible.setSizeIsFixed(newValue == wx.CHK_CHECKED)
    
