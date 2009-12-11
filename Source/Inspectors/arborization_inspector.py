import wx
from object_inspector import ObjectInspector
from network.arborization import Arborization


class ArborizationInspector( ObjectInspector ):
    
    @classmethod
    def objectClass(cls):
        return Arborization
    
    
    @classmethod
    def inspectedAttributes(cls):
        return ['sendsOutput', 'receivesInput']
    
    
    def objectSizer(self, parentWindow):
        if not hasattr(self, '_sizer'):
            self._sizer = wx.FlexGridSizer(2, 2, 8, 8)
            self._sizer.SetFlexibleDirection(wx.HORIZONTAL)
            
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
