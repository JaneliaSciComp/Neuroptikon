#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

import neuroptikon
import wx
from object_inspector import ObjectInspector
from network.neuron import Neuron


class NeuronInspector( ObjectInspector ):
    
    @classmethod
    def objectClass(cls):
        return Neuron
    
    
    @classmethod
    def inspectedAttributes(cls):
        return ['neuronClass', 'functions', 'polarity', 'neurotransmitters', 'neuronImage']
    
    
    def _appendNeuronClass(self, neuronClass, indent):
        self._neuronClassChoice.Append("    " * indent + neuronClass.name, neuronClass)
        for subClass in neuronClass.subClasses:
            self._appendNeuronClass(subClass, indent + 1)
        
    
    def objectSizer(self, parentWindow):
        if not hasattr(self, '_sizer'):
            self._sizer = wx.FlexGridSizer(5, 2, 8, 8)
            self._sizer.SetFlexibleDirection(wx.HORIZONTAL | wx.VERTICAL)
            
            self._sizer.Add(wx.StaticText(parentWindow, wx.ID_ANY, gettext('Class:')))
            self._neuronClassChoice = wx.Choice(parentWindow, wx.ID_ANY)
            for neuronClass in neuroptikon.library.neuronClasses():
                if neuronClass.parentClass is None:
                    self._appendNeuronClass(neuronClass, 0)
            self._unknownNeuronClassId = self._neuronClassChoice.Append(gettext('Unknown'), None)
            self._multipleNeuronClassesId = wx.NOT_FOUND
            self._sizer.Add(self._neuronClassChoice)
            parentWindow.Bind(wx.EVT_CHOICE, self.onChooseNeuronClass, self._neuronClassChoice)
            
            self._sizer.Add(wx.StaticText(parentWindow, wx.ID_ANY, gettext('Functions:')))
            functionsSizer = wx.BoxSizer(wx.VERTICAL)
            self._sensoryCheckBox = wx.CheckBox(self._window, wx.ID_ANY, gettext('Sensory'), style=wx.CHK_3STATE)
            self._window.Bind(wx.EVT_CHECKBOX, self.onSetSensoryFunction, self._sensoryCheckBox)
            functionsSizer.Add(self._sensoryCheckBox)
            self._interneuronCheckBox = wx.CheckBox(self._window, wx.ID_ANY, gettext('Interneuron'), style=wx.CHK_3STATE)
            self._window.Bind(wx.EVT_CHECKBOX, self.onSetInterneuronFunction, self._interneuronCheckBox)
            functionsSizer.Add(self._interneuronCheckBox)
            self._motorCheckBox = wx.CheckBox(self._window, wx.ID_ANY, gettext('Motor'), style=wx.CHK_3STATE)
            self._window.Bind(wx.EVT_CHECKBOX, self.onSetMotorFunction, self._motorCheckBox)
            functionsSizer.Add(self._motorCheckBox)
            self._sizer.Add(functionsSizer)
            
            self._sizer.Add(wx.StaticText(parentWindow, wx.ID_ANY, gettext('Polarity:')))
            self._polarityChoice = wx.Choice(parentWindow, wx.ID_ANY)
            self._polarityChoice.Append(gettext('Unipolar'), Neuron.Polarity.UNIPOLAR)
            self._polarityChoice.Append(gettext('Bipolar'), Neuron.Polarity.BIPOLAR)
            self._polarityChoice.Append(gettext('Pseudo-unipolar'), Neuron.Polarity.PSEUDOUNIPOLAR)
            self._polarityChoice.Append(gettext('Multipolar'), Neuron.Polarity.MULTIPOLAR)
            self._unknownPolarityId = self._polarityChoice.Append(gettext('Unknown'), None)
            self._multiplePolaritiesId = wx.NOT_FOUND
            self._sizer.Add(self._polarityChoice)
            parentWindow.Bind(wx.EVT_CHOICE, self.onChoosePolarity, self._polarityChoice)
            
            self._sizer.Add(wx.StaticText(parentWindow, wx.ID_ANY, gettext('Neurotransmitters:')))
            self._neurotransmittersOptions = wx.BoxSizer(wx.VERTICAL)
            self._neurotransmittersSizer = wx.FlexGridSizer(0, 2, 2, 5)
            self._neurotransmittersSizer.SetFlexibleDirection(wx.HORIZONTAL)
            self._neurotransmittersOptions.Add(self._neurotransmittersSizer, 1, wx.EXPAND)
            self._neurotransmitterChoice = wx.Choice(parentWindow, wx.ID_ANY)
            self._neurotransmittersOptions.Add(self._neurotransmitterChoice, 0, wx.TOP, 4)
            self._sizer.Add(self._neurotransmittersOptions)
            parentWindow.Bind(wx.EVT_CHOICE, self.onAddNeurotransmitter, self._neurotransmitterChoice)
            
            self._sizer.Add(wx.StaticText(parentWindow, wx.ID_ANY, gettext('Neuron Image:')))
            self.imageOfNeuron = wx.StaticBitmap(self._window, wx.ID_ANY)
            self.imageOfNeuron.SetMinSize(wx.Size(32, 32))
            self.imageOfNeuron.SetMaxSize(wx.Size(32, 32))
            self._sizer.Add(self.imageOfNeuron, 0, wx.EXPAND)

            self._parentWindow = parentWindow
        
        return self._sizer
    
    
    def populateObjectSizer(self, attribute = None):
        if attribute is None or attribute == 'neuronClass':
            # Choose the appropriate item in the pop-up menu.
            if self.objects.haveEqualAttr('neuronClass'):
                if self.objects[0].neuronClass is None:
                    self._neuronClassChoice.SetSelection(self._unknownNeuronClassId)
                else:
                    for index in range(0, self._neuronClassChoice.GetCount()):
                        if self._neuronClassChoice.GetClientData(index) == self.objects[0].neuronClass:
                            self._neuronClassChoice.SetSelection(index)
            else:
                self._multipleNeuronClassesId = self._neuronClassChoice.Append(gettext('Multiple values'), None)
                self._neuronClassChoice.SetSelection(self._multipleNeuronClassesId)
        
        if attribute is None or attribute == 'functions':
            for function, checkBox in [(Neuron.Function.SENSORY, self._sensoryCheckBox), (Neuron.Function.INTERNEURON, self._interneuronCheckBox), (Neuron.Function.MOTOR, self._motorCheckBox)]:
                mixedFunction = False
                hasFunction = self.objects[0].hasFunction(function)
                for object in self.objects[1:]:
                    if hasFunction != object.hasFunction(function):
                        mixedFunction = True
                if mixedFunction:
                    checkBox.Set3StateValue(wx.CHK_UNDETERMINED)
                elif hasFunction:
                    checkBox.Set3StateValue(wx.CHK_CHECKED)
                else:
                    checkBox.Set3StateValue(wx.CHK_UNCHECKED)
        
        if attribute is None or attribute == 'polarity':
            # Choose the appropriate item in the pop-up menu.
            if self.objects.haveEqualAttr('polarity'):
                if self.objects[0].polarity is None:
                    self._polarityChoice.SetSelection(self._unknownPolarityId)
                else:
                    for index in range(0, self._polarityChoice.GetCount()):
                        if self._polarityChoice.GetClientData(index) == self.objects[0].polarity:
                            self._polarityChoice.SetSelection(index)
            else:
                self._multiplePolaritiesId = self._polarityChoice.Append(gettext('Multiple values'), None)
                self._polarityChoice.SetSelection(self._multiplePolaritiesId)
        
        if attribute is None or attribute == 'neurotransmitters':
            if self.objects.haveEqualAttr('neurotransmitters'):
                self._neurotransmittersSizer.Clear(True)
                self._neurotransmitterChoice.Clear()
                self._neurotransmitterChoice.Append(gettext('Add...'))
                self._neurotransmitterChoice.SetSelection(0)
                for neurotransmitter in neuroptikon.library.neurotransmitters():
                    if neurotransmitter in self.objects[0].neurotransmitters:
                        self._neurotransmittersSizer.Add(wx.StaticText(self._parentWindow, wx.ID_ANY, neurotransmitter.name))
                        removeButton = wx.Button(self._parentWindow, wx.ID_ANY, gettext('Remove'), style = wx.BU_EXACTFIT)
                        removeButton.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)
                        removeButton.SetSize(wx.Size(60, removeButton.GetSize().GetHeight()))
                        removeButton.SetMinSize(removeButton.GetSize())
                        self._parentWindow.Bind(wx.EVT_BUTTON, self.onRemoveNeurotransmitter, removeButton)
                        self._neurotransmittersSizer.Add(removeButton, 0, 0, 0, neurotransmitter)
                    else:
                        self._neurotransmitterChoice.Append(neurotransmitter.name, neurotransmitter)
                if len(self.objects[0].neurotransmitters) == 0:
                    self._neurotransmittersSizer.Add(wx.StaticText(self._parentWindow, wx.ID_ANY, gettext('Unknown')))
                self._neurotransmitterChoice.Enable(self._neurotransmitterChoice.GetCount() > 1)
            else:
                self._neurotransmittersSizer.Add(wx.StaticText(self._parentWindow, wx.ID_ANY, gettext('Multiple values')))
                self._neurotransmitterChoice.Disable()
                
        if attribute is None or attribute == 'neuronImage':
            if self.objects.haveEqualAttr('neuronImage'):
                #TODO replace with real neuron Image
                image = self.objects[0].neuronImage
                if image == None:
                    pass
                else:
                    scaledImage = image.Copy().Rescale(100, 100, wx.IMAGE_QUALITY_HIGH)
                    self.imageOfNeuron.SetBitmap(wx.BitmapFromImage(scaledImage))
            else:
                pass
                #option if not all neurons have the same image
            
        self._sizer.Layout()
        
    
    def onChooseNeuronClass(self, event):
        self.updatingObjects = True
        neuronClass = self._neuronClassChoice.GetClientData(self._neuronClassChoice.GetSelection())
        for neuron in self.objects:
            neuron.neuronClass = neuronClass
        # Remove the "multiple values" choice now that all of the neurons have the same value.
        if self._multipleNeuronClassesId != wx.NOT_FOUND:
            self._neuronClassChoice.Delete(self._multipleNeuronClassesId)
            self._multipleNeuronClassesId = wx.NOT_FOUND
        self.populateObjectSizer('neuronClass')
    
    
    def onSetSensoryFunction(self, event):
        newValue = self._sensoryCheckBox.GetValue()
        for neuron in self.objects:
            neuron.setHasFunction(Neuron.Function.SENSORY, newValue == wx.CHK_CHECKED)
    
    
    def onSetInterneuronFunction(self, event):
        newValue = self._interneuronCheckBox.GetValue()
        for neuron in self.objects:
            neuron.setHasFunction(Neuron.Function.INTERNEURON, newValue == wx.CHK_CHECKED)
    
    
    def onSetMotorFunction(self, event):
        newValue = self._motorCheckBox.GetValue()
        for neuron in self.objects:
            neuron.setHasFunction(Neuron.Function.MOTOR, newValue == wx.CHK_CHECKED)
    
    
    def onChoosePolarity(self, event):
        self.updatingObjects = True
        polarity = self._polarityChoice.GetClientData(self._polarityChoice.GetSelection())
        for neuron in self.objects:
            neuron.polarity = polarity
        # Remove the "multiple values" choice now that all of the neurons have the same value.
        if self._multiplePolaritiesId != wx.NOT_FOUND:
            self._polarityChoice.Delete(self._multiplePolaritiesId)
            self._multiplePolaritiesId = wx.NOT_FOUND
        self.populateObjectSizer('polarity')
    
    
    def onAddNeurotransmitter(self, event):
        self.updatingObjects = True
        neurotransmitter = self._neurotransmitterChoice.GetClientData(self._neurotransmitterChoice.GetSelection())
        for neuron in self.objects:
            neuron.neurotransmitters.append(neurotransmitter)
        self.populateObjectSizer('neurotransmitters')
    
    
    def onRemoveNeurotransmitter(self, event):
        self.updatingObjects = True
        sizerItem = self._neurotransmittersSizer.GetItem(event.GetEventObject())
        neurotransmitter = sizerItem.GetUserData()
        for neuron in self.objects:
            neuron.neurotransmitters.remove(neurotransmitter)
        self.populateObjectSizer('neurotransmitters')
