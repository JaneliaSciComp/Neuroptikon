import wx
from ObjectInspector import ObjectInspector
from Neuron import Neuron


class NeuronInspector( ObjectInspector ):
    
    @classmethod
    def objectClass(cls):
        return Neuron
    
    
    @classmethod
    def inspectedAttributes(cls):
        return ['neuronClass', 'function', 'polarity', 'neurotransmitter']
    
    
    def _appendNeuronClass(self, neuronClass, indent):
        self._neuronClassChoice.Append("    " * indent + neuronClass.name, neuronClass)
        for subClass in neuronClass.subClasses:
            self._appendNeuronClass(subClass, indent + 1)
        
    
    def objectSizer(self, parentWindow):
        if not hasattr(self, '_sizer'):
            self._sizer = wx.FlexGridSizer(2, 2, 8, 8)
            self._sizer.SetFlexibleDirection(wx.HORIZONTAL)
            
            self._sizer.Add(wx.StaticText(parentWindow, wx.ID_ANY, _('Class:')))
            self._neuronClassChoice = wx.Choice(parentWindow, wx.ID_ANY)
            for neuronClass in wx.GetApp().library.neuronClasses():
                if neuronClass.parentClass is None:
                    self._appendNeuronClass(neuronClass, 0)
            self._unknownNeuronClassId = self._neuronClassChoice.Append(_('Unknown'), None)
            self._multipleNeuronClassesId = wx.NOT_FOUND
            self._sizer.Add(self._neuronClassChoice)
            parentWindow.Bind(wx.EVT_CHOICE, self.onChooseNeuronClass, self._neuronClassChoice)
            
            self._sizer.Add(wx.StaticText(parentWindow, wx.ID_ANY, _('Function:')))
            self._functionChoice = wx.Choice(parentWindow, wx.ID_ANY)
            self._functionChoice.Append(_('Sensory neuron'), Neuron.Function.SENSORY)
            self._functionChoice.Append(_('Interneuron'), Neuron.Function.INTERNEURON)
            self._functionChoice.Append(_('Motor neuron'), Neuron.Function.MOTOR)
            self._unknownFunctionId = self._functionChoice.Append(_('Unknown'), None)
            self._multipleFunctionsId = wx.NOT_FOUND
            self._sizer.Add(self._functionChoice)
            parentWindow.Bind(wx.EVT_CHOICE, self.onChooseFunction, self._functionChoice)
            
            self._sizer.Add(wx.StaticText(parentWindow, wx.ID_ANY, _('Polarity:')))
            self._polarityChoice = wx.Choice(parentWindow, wx.ID_ANY)
            self._polarityChoice.Append(_('Unipolar'), Neuron.Polarity.UNIPOLAR)
            self._polarityChoice.Append(_('Bipolar'), Neuron.Polarity.BIPOLAR)
            self._polarityChoice.Append(_('Pseudo-unipolar'), Neuron.Polarity.PSEUDOUNIPOLAR)
            self._polarityChoice.Append(_('Multipolar'), Neuron.Polarity.MULTIPOLAR)
            self._unknownPolarityId = self._polarityChoice.Append(_('Unknown'), None)
            self._multiplePolaritiesId = wx.NOT_FOUND
            self._sizer.Add(self._polarityChoice)
            parentWindow.Bind(wx.EVT_CHOICE, self.onChoosePolarity, self._polarityChoice)
            
            self._sizer.Add(wx.StaticText(parentWindow, wx.ID_ANY, _('Neurotransmitter:')))
            self._neurotransmitterChoice = wx.Choice(parentWindow, wx.ID_ANY)
            for neurotransmitter in wx.GetApp().library.neurotransmitters():
                self._neurotransmitterChoice.Append(neurotransmitter.name, neurotransmitter)
            self._unknownNeurotransmitterId = self._neurotransmitterChoice.Append(_('Unknown'), None)
            self._multipleNeurotransmittersId = wx.NOT_FOUND
            self._sizer.Add(self._neurotransmitterChoice)
            parentWindow.Bind(wx.EVT_CHOICE, self.onChooseNeurotransmitter, self._neurotransmitterChoice)
            
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
                self._multipleNeuronClassesId = self._neuronClassChoice.Append(_('Multiple values'), None)
                self._neuronClassChoice.SetSelection(self._multipleNeuronClassesId)
        
        if attribute is None or attribute == 'function':
            # Choose the appropriate item in the pop-up menu.
            if self.objects.haveEqualAttr('function'):
                if self.objects[0].function is None:
                    self._functionChoice.SetSelection(self._unknownFunctionId)
                else:
                    for index in range(0, self._functionChoice.GetCount()):
                        if self._functionChoice.GetClientData(index) == self.objects[0].function:
                            self._functionChoice.SetSelection(index)
            else:
                self._multipleFunctionsId = self._functionChoice.Append(_('Multiple values'), None)
                self._functionChoice.SetSelection(self._multipleFunctionsId)
        
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
                self._multiplePolaritiesId = self._polarityChoice.Append(_('Multiple values'), None)
                self._polarityChoice.SetSelection(self._multiplePolaritiesId)
        
        if attribute is None or attribute == 'neurotransmitter':
            # Choose the appropriate item in the pop-up menu.
            if self.objects.haveEqualAttr('neurotransmitter'):
                if self.objects[0].neurotransmitter is None:
                    self._neurotransmitterChoice.SetSelection(self._unknownNeurotransmitterId)
                else:
                    self._neurotransmitterChoice.SetStringSelection(self.objects[0].neurotransmitter.name)
            else:
                self._multipleNeurotransmittersId = self._neurotransmitterChoice.Append(_('Multiple values'), None)
                self._neurotransmitterChoice.SetSelection(self._multipleNeurotransmittersId)
        
        self._sizer.Layout()
        
    
    def onChooseNeuronClass(self, event):
        neuronClass = self._neuronClassChoice.GetClientData(self._neuronClassChoice.GetSelection())
        for neuron in self.objects:
            neuron.neuronClass = neuronClass
        # Remove the "multiple values" choice now that all of the neurons have the same value.
        if self._multipleNeuronClassesId != wx.NOT_FOUND:
            self._neuronClassChoice.Delete(self._multipleNeuronClassesId)
            self._multipleNeuronClassesId = wx.NOT_FOUND
        
    
    def onChooseFunction(self, event):
        function = self._functionChoice.GetClientData(self._functionChoice.GetSelection())
        for neuron in self.objects:
            neuron.function = function
        # Remove the "multiple values" choice now that all of the neurons have the same value.
        if self._multipleFunctionsId != wx.NOT_FOUND:
            self._functionChoice.Delete(self._multipleFunctionsId)
            self._multipleFunctionsId = wx.NOT_FOUND
        
    
    def onChoosePolarity(self, event):
        polarity = self._polarityChoice.GetClientData(self._polarityChoice.GetSelection())
        for neuron in self.objects:
            neuron.polarity = polarity
        # Remove the "multiple values" choice now that all of the neurons have the same value.
        if self._multiplePolaritiesId != wx.NOT_FOUND:
            self._polarityChoice.Delete(self._multiplePolaritiesId)
            self._multiplePolaritiesId = wx.NOT_FOUND
        
    
    def onChooseNeurotransmitter(self, event):
        neurotransmitter = self._neurotransmitterChoice.GetClientData(self._neurotransmitterChoice.GetSelection())
        for neuron in self.objects:
            neuron.neurotransmitter = neurotransmitter
        # Remove the "multiple values" choice now that all of the neurons have the same value.
        if self._multipleNeurotransmittersId != wx.NOT_FOUND:
            self._neurotransmitterChoice.Delete(self._multipleNeurotransmittersId)
            self._multipleNeurotransmittersId = wx.NOT_FOUND
