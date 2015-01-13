#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

import wx
from object_inspector import ObjectInspector
from network.arborization import Arborization
from network.neuron import Neuron

class ArborizationInspector( ObjectInspector ):
    
    @classmethod
    def objectClass(cls):
        return Arborization
    
    
    @classmethod
    def inspectedAttributes(cls):
        return ['sendsOutput', 'receivesInput']
    
    
    def objectSizer(self, parentWindow):
        if not hasattr(self, '_sizer'):
            self._sizer = wx.FlexGridSizer(3, 2, 8, 8)
            self._sizer.SetFlexibleDirection(wx.HORIZONTAL)
            
            neuronImage = Neuron.image()
            if neuronImage == None:
                self._regionBitmap = wx.EmptyBitmap(16, 16)
            else:
                self._regionBitmap = wx.BitmapFromImage(neuronImage.Rescale(16, 16, wx.IMAGE_QUALITY_HIGH))
            
            
            self._sizer.Add(wx.StaticText(parentWindow, wx.ID_ANY, gettext('Sends output to region:')))
            self._sendsOutputChoice = wx.Choice(parentWindow, wx.ID_ANY)
            self._sendsOutputChoice.Append(gettext('Yes'), True)
            self._sendsOutputChoice.Append(gettext('No'), False)
            self._sendsOutputChoice.Append(gettext('Unknown'), None)
            self._multipleSendsOuputsId = wx.NOT_FOUND
            self._sizer.Add(self._sendsOutputChoice)
            parentWindow.Bind(wx.EVT_CHOICE, self.onChooseSendsOutput, self._sendsOutputChoice)
            
            self._sizer.Add(wx.StaticText(parentWindow, wx.ID_ANY, gettext('Receives input from region:')))
            self._receivesInputChoice = wx.Choice(parentWindow, wx.ID_ANY)
            self._receivesInputChoice.Append(gettext('Yes'), True)
            self._receivesInputChoice.Append(gettext('No'), False)
            self._receivesInputChoice.Append(gettext('Unknown'), None)
            self._multipleReceivesInputsId = wx.NOT_FOUND
            self._sizer.Add(self._receivesInputChoice)
            
            #add a neuron sizer
            self._sizer.Add(wx.StaticText(parentWindow, wx.ID_ANY, gettext('Neuron: ')))
            parentSizer = wx.BoxSizer(wx.HORIZONTAL)
            parentSizer.Add(wx.StaticBitmap(parentWindow, wx.ID_ANY, self._regionBitmap))
            self._parentNameField = wx.StaticText(parentWindow, wx.ID_ANY)
            parentSizer.Add(self._parentNameField, 1, wx.LEFT, 2)
            self._selectParentButton = wx.Button(parentWindow, wx.ID_ANY, gettext('Select'), style = wx.BU_EXACTFIT)
            self._selectParentButton.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)
            self._selectParentButton.SetSize(wx.Size(50, self._selectParentButton.GetSize().GetHeight()))
            self._selectParentButton.SetMinSize(self._selectParentButton.GetSize())
            self._window.Bind(wx.EVT_BUTTON, self.onSelectNeuron, self._selectParentButton)
            parentSizer.Add(self._selectParentButton, 0, wx.LEFT, 8)
            self._selectParentButton.Disable()
            self._sizer.Add(parentSizer)
            
            
            parentWindow.Bind(wx.EVT_CHOICE, self.onChooseReceievesInput, self._receivesInputChoice)
            
        return self._sizer
    
    
    def populateObjectSizer(self, attribute = None):
        if attribute is None or attribute == 'sendsOutput':
            if self.objects.haveEqualAttr('sendsOutput'):
                if self.objects[0].sendsOutput is None:
                    self._sendsOutputChoice.SetSelection(2)
                elif self.objects[0].sendsOutput:
                    self._sendsOutputChoice.SetSelection(0)
                else:
                    self._sendsOutputChoice.SetSelection(1)
            else:
                self._multipleSendsOuputsId = self._sendsOutputChoice.Append(gettext('Multiple values'))
                self._sendsOutputChoice.SetSelection(3)
        
        if attribute is None or attribute == 'receivesInput':
            if self.objects.haveEqualAttr('receivesInput'):
                if self.objects[0].receivesInput is None:
                    self._receivesInputChoice.SetSelection(2)
                elif self.objects[0].receivesInput:
                    self._receivesInputChoice.SetSelection(0)
                else:
                    self._receivesInputChoice.SetSelection(1)
            else:
                self._multipleReceivesInputsId = self._receivesInputChoice.Append(gettext('Multiple values'))
                self._receivesInputChoice.SetSelection(3)
        
        if attribute is None or attribute == 'neurite':
            if self.objects.haveEqualAttr('neurite'):
                if self.objects[0].neurite is None or self.objects[0].neurite.root is None:
                    self._parentNameField.SetLabel(gettext('None'))
                    self._selectParentButton.Disable()
                else:
                    self._parentNameField.SetLabel(self.objects[0].neurite.root.name or gettext('Unnamed neuron'))
                    self._selectParentButton.Enable()
            else:
                self._parentNameField.SetLabel(gettext('Multiple values'))
                self._selectParentButton.Disable()
        
        self._sizer.Layout()
        
    
    def onChooseSendsOutput(self, event):
        if self._sendsOutputChoice.GetSelection() != 3:
            sendsOutput = self._sendsOutputChoice.GetClientData(self._sendsOutputChoice.GetSelection())
            for arborization in self.objects:
                arborization.sendsOutput = sendsOutput
            # Remove the "multiple values" choice now that all of the objects have the same value.
            if self._multipleSendsOuputsId != wx.NOT_FOUND:
                self._sendsOutputChoice.Delete(self._multipleSendsOuputsId)
                self._multipleSendsOuputsId = wx.NOT_FOUND
        
    
    def onChooseReceievesInput(self, event):
        if self._receivesInputChoice.GetSelection() != 3:
            receivesInput = self._receivesInputChoice.GetClientData(self._receivesInputChoice.GetSelection())
            for arborization in self.objects:
                arborization.receivesInput = receivesInput
            # Remove the "multiple values" choice now that all of the objects have the same value.
            if self._multipleReceivesInputsId != wx.NOT_FOUND:
                self._receivesInputChoice.Delete(self._multipleReceivesInputsId)
                self._multipleReceivesInputsId = wx.NOT_FOUND

    def onSelectNeuron(self, event):
        self.selectObject(self.objects[0].neurite.root)