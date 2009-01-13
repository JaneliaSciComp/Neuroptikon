import wx
from ObjectInspector import ObjectInspector
from Stimulus import Stimulus


class StimulusInspector( ObjectInspector ):
    
    @classmethod
    def objectClass(cls):
        return Stimulus
    
    
    @classmethod
    def inspectedAttributes(cls):
        return ['modality']
    
    
    def objectSizer(self, parentWindow):
        if not hasattr(self, '_sizer'):
            self._sizer = wx.FlexGridSizer(1, 2, 8, 8)
            self._sizer.SetFlexibleDirection(wx.HORIZONTAL)
            self._sizer.Add(wx.StaticText(parentWindow, wx.ID_ANY, _('Modality') + ":"))
            self._modalityChoice = wx.Choice(parentWindow, wx.ID_ANY)
            for modality in wx.GetApp().library.modalities():
                self._modalityChoice.Append(modality.name, modality)
            self._unknownModalityId = self._modalityChoice.Append(_('Unknown'), None)
            self._multipleModalitiesId = wx.NOT_FOUND
            self._sizer.Add(self._modalityChoice)
            parentWindow.Bind(wx.EVT_CHOICE, self.onChooseModality, self._modalityChoice)
            
        return self._sizer
    
    
    def populateObjectSizer(self, attribute = None):
        if attribute is None or attribute == 'modality':
            # Choose the appropriate item in the pop-up menu.
            if self.objects.haveEqualAttr('modality'):
                if self.objects[0].modality is None:
                    self._modalityChoice.SetSelection(self._unknownMadalityId)
                else:
                    self._modalityChoice.SetStringSelection(self.objects[0].modality.name)
            else:
                self._multipleModalitiesId = self._modalityChoice.Append(_('Multiple values'), None)
                self._modalityChoice.SetSelection(self._multipleModalitiesId)
        
        self._sizer.Layout()
        
    
    def onChooseModality(self, event):
        modality = self._modalityChoice.GetClientData(self._modalityChoice.GetSelection())
        for stimulus in self.objects:
            stimulus.modality = modality
        # Remove the "multiple values" choice now that all of the stimuli have the same modality.
        if self._multipleModalitiesId != wx.NOT_FOUND:
            self._modalityChoice.Delete(self._multipleModalitiesId)
            self._multipleModalitiesId = wx.NOT_FOUND
