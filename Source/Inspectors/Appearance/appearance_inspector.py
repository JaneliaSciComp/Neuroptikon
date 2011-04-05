#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

import neuroptikon
import wx, wx.lib.colourselect
from pydispatch import dispatcher
from inspection.inspector import Inspector
from network.object_list import ObjectList
import display.shape


class AppearanceInspector(Inspector):
    
    @classmethod
    def name(cls):
        return gettext('Appearance')
    
    
    @classmethod
    def canInspectDisplay(cls, display):
        return display and any(display.selection())


    def window(self, parentWindow=None):
        if not hasattr(self, '_window'):
            self._window = wx.Window(parentWindow, wx.ID_ANY)
            gridSizer = wx.FlexGridSizer(5, 2, 8, 8)
            
            # Add a color picker for our fill color.
            self._colorPicker = wx.lib.colourselect.ColourSelect(self._window, wx.ID_ANY)
            self._window.Bind(wx.lib.colourselect.EVT_COLOURSELECT, self.onSetColor, self._colorPicker)
            gridSizer.Add(wx.StaticText(self._window, wx.ID_ANY, gettext('Color:')), 0)
            gridSizer.Add(self._colorPicker, 1)
            
            # Add a slider for setting the opacity.
            self._opacitySlider = wx.Slider(self._window, wx.ID_ANY, 100, 0, 100)
            self._opacitySlider.Bind(wx.EVT_SCROLL, self.onSetOpacity, self._opacitySlider)
            gridSizer.Add(wx.StaticText(self._window, wx.ID_ANY, gettext('Opacity:')), 0)
            gridSizer.Add(self._opacitySlider, 1)
            
            # Add a pop-up for choosing the shape.
            self._shapeChoice = wx.Choice(self._window, wx.ID_ANY)
            shapeClasses = [(shapeClass.__name__, shapeClass) for shapeClass in display.shape.shapeClasses()]
            for shapeName, shapeClass in sorted(shapeClasses):
                self._shapeChoice.Append(shapeName, shapeClass)
            self._shapeChoice.Append(gettext('None'), None)
            self._multipleShapesId = wx.NOT_FOUND
            gridSizer.Add(wx.StaticText(self._window, wx.ID_ANY, gettext('Shape:')), 0)
            gridSizer.Add(self._shapeChoice, 0)
            parentWindow.Bind(wx.EVT_CHOICE, self.onSetShape, self._shapeChoice)
            
            # Add a pop-up for choosing the texture.
            self._textureChoice = wx.Choice(self._window, wx.ID_ANY)
            if hasattr(neuroptikon.library, 'texture'):
                for texture in neuroptikon.library.textures():
                    self._textureChoice.Append(gettext(texture.name), texture)
            self._textureChoice.Append(gettext('None'), None)
            self._multipleTexturesId = wx.NOT_FOUND
            gridSizer.Add(wx.StaticText(self._window, wx.ID_ANY, gettext('Texture:')), 0)
            gridSizer.Add(self._textureChoice, 0)
            parentWindow.Bind(wx.EVT_CHOICE, self.onSetTexture, self._textureChoice)
            
            # Add a slider for setting the weight.
            self._weightSlider = wx.Slider(self._window, wx.ID_ANY, 50, 0, 100)
            self._weightSlider.Bind(wx.EVT_SCROLL, self.onSetWeight, self._weightSlider)
            gridSizer.Add(wx.StaticText(self._window, wx.ID_ANY, gettext('Weight:')), 0)
            gridSizer.Add(self._weightSlider, 1)
            
            # TODO: label, ???
            
            mainSizer = wx.BoxSizer(wx.VERTICAL)
            mainSizer.Add(gridSizer, 1, wx.ALL, 5)
            self._window.SetSizer(mainSizer)
        
        return self._window
    
    
    def inspectDisplay(self, display):
        self.visibles = display.selection()
        for visible in self.visibles:
            for attributeName in ['color', 'opacity', 'shape', 'texture', 'weight']:
                dispatcher.connect(self.refreshGUI, ('set', attributeName), visible)
        self.refreshGUI()
    
    
    def willBeClosed(self):
        for visible in self.visibles:
            for attributeName in ['color', 'opacity', 'shape', 'texture', 'weight']:
                dispatcher.disconnect(self.refreshGUI, ('set', attributeName), visible)
        self.visibles = ObjectList()
    
    
    def refreshGUI(self, signal = ('set', None)):
        if any(self.visibles):
            updatedAttribute = signal[1]
            
            if updatedAttribute is None or updatedAttribute == 'color':
                if self.visibles.haveEqualAttr('color'):
                    red, green, blue = self.visibles[0].color()
                    self._colorPicker.SetColour(wx.Colour(red * 255, green * 255, blue * 255, 255))
                    self._colorPicker.SetLabel(gettext(''))
                else:
                    self._colorPicker.SetColour(wx.NamedColour('GRAY'))  # TODO: be clever and pick the average color?
                    self._colorPicker.SetLabel(gettext('Multiple values'))
            
            if updatedAttribute is None or updatedAttribute == 'opacity':
                if self.visibles.haveEqualAttr('opacity'):
                    self._opacitySlider.SetLabel('')
                    self._opacitySlider.SetValue(self.visibles[0].opacity() * 100.0)
                else:
                    self._opacitySlider.SetLabel(gettext('Multiple values'))
                    self._opacitySlider.SetValue(100)
            
            if updatedAttribute is None or updatedAttribute == 'shape':
                shapeClass = type(self.visibles[0].shape())
                equalClasses = True
                for visible in self.visibles[1:]:
                    if type(visible) != shapeClass:
                        equalClasses = False
                if equalClasses:
                    for index in range(0, self._shapeChoice.GetCount()):
                        if self._shapeChoice.GetClientData(index) == shapeClass:
                            self._shapeChoice.SetSelection(index)
                            break
                else:
                    if self._multipleShapesId == wx.NOT_FOUND:
                        self._multipleShapesId = self._shapeChoice.Append(gettext('Multiple values'), None)
                    self._shapeChoice.SetSelection(self._multipleShapesId)
            
            if updatedAttribute is None or updatedAttribute == 'texture':
                if self.visibles.haveEqualAttr('texture'):
                    for index in range(0, self._textureChoice.GetCount()):
                        if self._textureChoice.GetClientData(index) == self.visibles[0].texture():
                            self._textureChoice.SetSelection(index)
                            break
                else:
                    if self._multipleTexturesId == wx.NOT_FOUND:
                        self._multipleTexturesId = self._textureChoice.Append(gettext('Multiple values'), None)
                    self._textureChoice.SetSelection(self._multipleTexturesId)
            
            if updatedAttribute is None or updatedAttribute == 'weight':
                if self.visibles.haveEqualAttr('weight'):
                    self._weightSlider.SetLabel('')
                    if self.visibles[0].weight() >= 1.0:
                        self._weightSlider.SetValue((self.visibles[0].weight() - 1.0) * 50.0 / 9.0 + 50.0)
                    else:
                        self._weightSlider.SetValue(50.0 - (1.0 - self.visibles[0].weight()) * 10.0 * 50.0 / 9.0)
                else:
                    self._weightSlider.SetLabel(gettext('Multiple values'))
                    self._weightSlider.SetValue(50)
            
            self._window.Layout()
    
    
    def onSetColor(self, event_):
        wxColor = self._colorPicker.GetColour()
        colorTuple = (wxColor.Red() / 255.0, wxColor.Green() / 255.0, wxColor.Blue() / 255.0)
        for visible in self.visibles:
            visible.setColor(colorTuple)
        
    
    def onSetOpacity(self, event_):
        newOpacity = self._opacitySlider.GetValue() / 100.0
        for visible in self.visibles:
            visible.setOpacity(newOpacity)
        
    
    def onSetShape(self, event_):
        shapeClass = self._shapeChoice.GetClientData(self._shapeChoice.GetSelection())
        for visible in self.visibles:
            visible.setShape(None if shapeClass is None else shapeClass())
        # Remove the "multiple values" choice now that all of the visibles have the same value.
        if self._multipleShapesId != wx.NOT_FOUND:
            self._shapeChoice.Delete(self._multipleShapesId)
            self._multipleShapesId = wx.NOT_FOUND
        
    
    def onSetTexture(self, event_):
        texture = self._textureChoice.GetClientData(self._textureChoice.GetSelection())
        for visible in self.visibles:
            visible.setTexture(texture)
            visible.setTextureScale(10.0)
        # Remove the "multiple values" choice now that all of the visibles have the same value.
        if self._multipleTexturesId != wx.NOT_FOUND:
            self._textureChoice.Delete(self._multipleTexturesId)
            self._multipleTexturesId = wx.NOT_FOUND
        
    
    def onSetWeight(self, event_):
        newWeight = self._weightSlider.GetValue()
        if newWeight >= 50:
            newWeight = 1.0 + (newWeight - 50.0) / (50.0 / 9.0)
        else:
            newWeight = 1.0 - (50.0 - newWeight) / (50.0 / 9.0) / 10.0
        for visible in self.visibles:
            visible.setWeight(newWeight)
    
