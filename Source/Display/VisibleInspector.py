import wx, wx.lib.colourselect
import os, sys
from pydispatch import dispatcher
from Inspection.Inspector import Inspector
from Network.ObjectList import ObjectList
from Visible import Visible


class VisibleInspector(Inspector):
    
    @classmethod
    def name(cls):
        return gettext('Visible')
    
    
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
            gridSizer = wx.FlexGridSizer(3, 2, 8, 8)
            
            # Add a color picker for our fill color.
            self._colorPicker = wx.lib.colourselect.ColourSelect(self._window, wx.ID_ANY)
            self._window.Bind(wx.lib.colourselect.EVT_COLOURSELECT, self.onSetColor, self._colorPicker)
            gridSizer.Add(wx.StaticText(self._window, wx.ID_ANY, gettext('Color:')), 0)
            gridSizer.Add(self._colorPicker, 1)
            
            # Add a check box for fixing the position.
            self.fixedPositionCheckBox = wx.CheckBox(self._window, wx.ID_ANY, gettext('Fixed'), style=wx.CHK_3STATE)
            self._window.Bind(wx.EVT_CHECKBOX, self.onSetPositionIsFixed)
            gridSizer.Add(wx.StaticText(self._window, wx.ID_ANY, gettext('Position:')), 0)
            gridSizer.Add(self.fixedPositionCheckBox, 1)
            
            # Add a slider for setting the arrangement weight within our parent.
            self._arrangedWeightSlider = wx.Slider(self._window, wx.ID_ANY, 50, 1, 100, style=wx.SL_HORIZONTAL)
            self._arrangedWeightSlider.Bind(wx.EVT_SCROLL, self.onSetArrangedWeight)
            gridSizer.Add(wx.StaticText(self._window, wx.ID_ANY, gettext('Arranged weight:')), 0)
            gridSizer.Add(self._arrangedWeightSlider, 1)
            
            # Add a pop-up for choosing the child arrangement.
            self._arrangedAxisChoice = wx.Choice(self._window, wx.ID_ANY)
            self._arrangedAxisChoice.Append(gettext('None'), None)
            self._arrangedAxisChoice.Append(gettext('Largest'), 'largest')
            self._arrangedAxisChoice.Append(gettext('X'), 'X')
            self._arrangedAxisChoice.Append(gettext('Y'), 'Y')
            self._arrangedAxisChoice.Append(gettext('Z'), 'Z')
            self._multipleArrangedAxesId = wx.NOT_FOUND
            gridSizer.Add(wx.StaticText(self._window, wx.ID_ANY, gettext('Arrange children along axis:')), 0)
            gridSizer.Add(self._arrangedAxisChoice, 0)
            parentWindow.Bind(wx.EVT_CHOICE, self.onSetArrangedAxis, self._arrangedAxisChoice)
            
            # Add a slider for setting the arrangement spacing.
            self._arrangedSpacingSlider = wx.Slider(self._window, wx.ID_ANY, 20, 0, 249, style=wx.SL_HORIZONTAL)
            self._arrangedSpacingSlider.Bind(wx.EVT_SCROLL, self.onSetArrangedSpacing, self._arrangedSpacingSlider)
            gridSizer.Add(wx.StaticText(self._window, wx.ID_ANY, gettext('Arranged spacing:')), 0)
            gridSizer.Add(self._arrangedSpacingSlider, 1)
            
            # Add a pop-up for choosing the shape.
            self._shapeChoice = wx.Choice(self._window, wx.ID_ANY)
            for geometryName in sorted(Visible.geometries.keys()):
                self._shapeChoice.Append(gettext(geometryName), geometryName)
            self._multipleShapesId = wx.NOT_FOUND
            gridSizer.Add(wx.StaticText(self._window, wx.ID_ANY, gettext('Shape:')), 0)
            gridSizer.Add(self._shapeChoice, 0)
            parentWindow.Bind(wx.EVT_CHOICE, self.onSetShape, self._shapeChoice)
            
            # TODO: label, opacity, ???
            
            mainSizer = wx.BoxSizer(wx.VERTICAL)
            mainSizer.Add(gridSizer, 1, wx.ALL, 5)
            self._window.SetSizer(mainSizer)
        
        return self._window
    
    
    def inspectDisplay(self, display):
        self.visibles = display.selection()
        for visible in self.visibles:
            for attributeName in ['color', 'positionIsFixed', 'shape', 'children', 'arrangedWeight', 'arrangedAxis', 'arrangedSpacing']:
                dispatcher.connect(self.refreshGUI, ('set', attributeName), visible)
        self.refreshGUI()
    
    
    def refreshGUI(self, signal = ('set', None), **arguments):
        updatedAttribute = signal[1]
        
        # Check for parents and children of all of the visibles.
        visibleHasParent = False
        for visible in self.visibles:
            if visible.parent is not None:
                visibleHasParent = True
        commonChildCount = len(self.visibles[0].children)
        for visible in self.visibles[1:]:
            if len(visible.children) != commonChildCount:
                commonChildCount = -1   # different numbers of children
                break
        
        if updatedAttribute is None or updatedAttribute == 'color':
            if self.visibles.haveEqualAttr('color'):
                red, green, blue = self.visibles[0].color()
                self._colorPicker.SetColour(wx.Color(red * 255, green * 255, blue * 255, 255))
                self._colorPicker.SetLabel(gettext(''))
            else:
                self._colorPicker.SetColour(wx.NamedColour('GRAY'))  # TODO: be clever and pick the average color?
                self._colorPicker.SetLabel(gettext('Multiple values'))
        
        if updatedAttribute is None or updatedAttribute == 'positionIsFixed':
            if self.visibles.haveEqualAttr('positionIsFixed'):
                if self.visibles[0].positionIsFixed():
                    self.fixedPositionCheckBox.Set3StateValue(wx.CHK_CHECKED)
                else:
                    self.fixedPositionCheckBox.Set3StateValue(wx.CHK_UNCHECKED)
            else:
                self.fixedPositionCheckBox.Set3StateValue(wx.CHK_UNDETERMINED)
        
        if updatedAttribute is None or updatedAttribute == 'shape':
            if self.visibles.haveEqualAttr('shape'):
                for index in range(0, self._shapeChoice.GetCount()):
                    if self._shapeChoice.GetClientData(index) == self.visibles[0].shape():
                        self._shapeChoice.SetSelection(index)
                        break
            else:
                self._multipleShapesId = self._shapeChoice.Append(gettext('Multiple values'), None)
                self._shapeChoice.SetSelection(self._multipleShapesId)
        
        if updatedAttribute is None or updatedAttribute == 'arrangedWeight':
            if visibleHasParent:
                self._arrangedWeightSlider.Enable()
                if self.visibles.haveEqualAttr('arrangedWeight'):
                    self._arrangedWeightSlider.SetLabel('')
                    self._arrangedWeightSlider.SetValue(self.visibles[0].arrangedWeight)
                else:
                    self._arrangedWeightSlider.SetLabel(gettext('Multiple values'))
                    self._arrangedWeightSlider.SetValue(50)
            else:
                self._arrangedWeightSlider.Disable()
        
        if updatedAttribute is None or updatedAttribute == 'arrangedAxis':
            if commonChildCount > 0:
                self._arrangedAxisChoice.Enable()
                if self.visibles.haveEqualAttr('arrangedAxis'):
                    for index in range(0, self._arrangedAxisChoice.GetCount()):
                        if self._arrangedAxisChoice.GetClientData(index) == self.visibles[0].arrangedAxis:
                            self._arrangedAxisChoice.SetSelection(index)
                            break
                else:
                    self._multipleArrangedAxesId = self._arrangedAxisChoice.Append(gettext('Multiple values'), None)
                    self._arrangedAxisChoice.SetSelection(self._multipleArrangedAxesId)
            else:
                self._arrangedAxisChoice.Disable()
        
        if updatedAttribute is None or updatedAttribute == 'arrangedSpacing':
            if commonChildCount > 0:
                self._arrangedSpacingSlider.Enable()
                if self.visibles.haveEqualAttr('arrangedSpacing'):
                    self._arrangedSpacingSlider.SetLabel('')
                    self._arrangedSpacingSlider.SetValue(self.visibles[0].arrangedSpacing * 1000.0)
                else:
                    self._arrangedSpacingSlider.SetLabel(gettext('Multiple values'))
                    self._arrangedSpacingSlider.SetValue(20)
            else:
                self._arrangedSpacingSlider.Disable()
        
        self._window.Layout()
    
    
    def onSetColor(self, event):
        wxColor = self._colorPicker.GetColour()
        colorTuple = (wxColor.Red() / 255.0, wxColor.Green() / 255.0, wxColor.Blue() / 255.0)
        for visible in self.visibles:
            visible.setColor(colorTuple)
    
    
    def onSetPositionIsFixed(self, event):
        newValue = self.fixedPositionCheckBox.GetValue()
        for visible in self.visibles:
            visible.setPositionIsFixed(newValue == wx.CHK_CHECKED)
        
    
    def onSetArrangedWeight(self, event):
        newWeight = self._arrangedWeightSlider.GetValue()
        for visible in self.visibles:
            visible.setArrangedWeight(newWeight)
        
    
    def onSetArrangedAxis(self, event):
        axis = self._arrangedAxisChoice.GetClientData(self._arrangedAxisChoice.GetSelection())
        for visible in self.visibles:
            visible.setArrangedAxis(axis)
        # Remove the "multiple values" choice now that all of the visibles have the same value.
        if self._multipleArrangedAxesId != wx.NOT_FOUND:
            self._arrangedAxisChoice.Delete(self._multipleArrangedAxesId)
            self._multipleArrangedAxesId = wx.NOT_FOUND
        
    
    def onSetArrangedSpacing(self, event):
        newWeight = self._arrangedSpacingSlider.GetValue() / 1000.0
        for visible in self.visibles:
            visible.setArrangedSpacing(newWeight)
        
    
    def onSetShape(self, event):
        shape = self._shapeChoice.GetClientData(self._shapeChoice.GetSelection())
        for visible in self.visibles:
            visible.setShape(shape)
        # Remove the "multiple values" choice now that all of the visibles have the same value.
        if self._multipleShapesId != wx.NOT_FOUND:
            self._shapeChoice.Delete(self._multipleShapesId)
            self._multipleShapesId = wx.NOT_FOUND
    
