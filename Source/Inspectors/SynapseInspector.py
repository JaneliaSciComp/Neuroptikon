import wx
from ObjectInspector import ObjectInspector
from Network.Synapse import Synapse


class SynapseInspector( ObjectInspector ):
    
    @classmethod
    def objectClass(self):
        return Synapse
    
    
    @classmethod
    def inspectedAttributes(cls):
        return ['activation']
    
    
    def objectSizer(self, parentWindow):
        if not hasattr(self, '_sizer'):
            self._sizer = wx.FlexGridSizer(2, 2, 8, 8)
            
            self.excitatoryButton = wx.RadioButton(parentWindow, wx.ID_ANY, gettext('Excitatory'), style=wx.RB_GROUP)
            parentWindow.Bind(wx.EVT_RADIOBUTTON, self.onSetActivation, self.excitatoryButton)
            self._sizer.Add(wx.StaticText(parentWindow, wx.ID_ANY, gettext('Activation:')), 0)
            self._sizer.Add(self.excitatoryButton, 0)
            self.inhibitoryButton = wx.RadioButton(parentWindow, wx.ID_ANY, gettext('Inhibitory'))
            parentWindow.Bind(wx.EVT_RADIOBUTTON, self.onSetActivation, self.inhibitoryButton)
            self._sizer.AddStretchSpacer()
            self._sizer.Add(self.inhibitoryButton, 0)
            self.unknownActivationButton = wx.RadioButton(parentWindow, wx.ID_ANY, gettext('Unknown'))
            parentWindow.Bind(wx.EVT_RADIOBUTTON, self.onSetActivation, self.unknownActivationButton)
            self._sizer.AddStretchSpacer()
            self._sizer.Add(self.unknownActivationButton, 0)
            self.multipleActivationsButton = wx.RadioButton(parentWindow, wx.ID_ANY, gettext('Multiple Values'))
            self._sizer.AddStretchSpacer()
            self._sizer.Add(self.multipleActivationsButton, 0)
        
        return self._sizer
    
    
    def populateObjectSizer(self, attribute = None):
        if attribute is None or attribute == 'activation':
            if self.objects.haveEqualAttr('activation'):
                self.excitatoryButton.SetValue(self.objects[0].activation is not None and self.objects[0].activation == 'excitatory')
                self.inhibitoryButton.SetValue(self.objects[0].activation is not None and self.objects[0].activation == 'inhibitory')
                self.unknownActivationButton.SetValue(self.objects[0].activation is None)
                self.multipleActivationsButton.SetValue(False)
                self.multipleActivationsButton.Hide()
            else:
                self.excitatoryButton.SetValue(False)
                self.inhibitoryButton.SetValue(False)
                self.unknownActivationButton.SetValue(False)
                self.multipleActivationsButton.SetValue(True)
                self.multipleActivationsButton.Show()
        
        self._sizer.Layout()
    
    
    def onSetActivation(self, event):
        if self.excitatoryButton.GetValue():
            newValue = 'excitatory'
        elif self.inhibitoryButton.GetValue():
            newValue = 'inhibitory'
        elif self.unknownActivationButton.GetValue():
            newValue = None
        else:
            return
        
        for object in self.objects:
            object.activation = newValue
