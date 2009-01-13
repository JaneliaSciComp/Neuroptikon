import wx
from ObjectInspector import ObjectInspector
from Neuron import Neuron


class NeuronInspector( ObjectInspector ):
    
    @classmethod
    def objectClass(cls):
        return Neuron
    
    
    @classmethod
    def inspectedAttributes(cls):
        return ['neurotransmitter']
    
    
    def objectSizer(self, parentWindow):
        if not hasattr(self, '_sizer'):
            self._sizer = wx.FlexGridSizer(1, 2, 8, 8)
            self._sizer.SetFlexibleDirection(wx.HORIZONTAL)
            self._sizer.Add(wx.StaticText(parentWindow, wx.ID_ANY, _('Neurotransmitter') + ":"))
            self._neurotransmitterChoice = wx.Choice(parentWindow, wx.ID_ANY)
            for neurotransmitter in wx.GetApp().library.neurotransmitters():
                self._neurotransmitterChoice.Append(neurotransmitter.name, neurotransmitter)
            self._unknownNeurotransmitterId = self._neurotransmitterChoice.Append(_('Unknown'), None)
            self._multipleNeurotransmittersId = wx.NOT_FOUND
            self._sizer.Add(self._neurotransmitterChoice)
            parentWindow.Bind(wx.EVT_CHOICE, self.onChooseNeurotransmitter, self._neurotransmitterChoice)
            
        return self._sizer
    
    
    def populateObjectSizer(self, attribute = None):
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
        
    
    def onChooseNeurotransmitter(self, event):
        neurotransmitter = self._neurotransmitterChoice.GetClientData(self._neurotransmitterChoice.GetSelection())
        for neuron in self.objects:
            neuron.neurotransmitter = neurotransmitter
        # Remove the "multiple values" choice now that all of the neurons have the same value.
        if self._multipleNeurotransmittersId != wx.NOT_FOUND:
            self._neurotransmitterChoice.Delete(self._multipleNeurotransmittersId)
            self._multipleNeurotransmittersId = wx.NOT_FOUND
