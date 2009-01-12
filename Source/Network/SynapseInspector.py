import wx
from ObjectInspector import ObjectInspector
from Synapse import Synapse


class SynapseInspector( ObjectInspector ):
    
    def objectClass(self):
        return Synapse
    
    
    def inspectObjects(self):
        
        # Lazily create our UI
        if not hasattr(self, ''):
            gridSizer = wx.FlexGridSizer(2, 2, 8, 8)
            
            self.excitatoryButton = wx.RadioButton(self, wx.ID_ANY, _('Excitatory'), style=wx.RB_GROUP)
            self.Bind(wx.EVT_RADIOBUTTON, self.onSetActivation, self.excitatoryButton)
            gridSizer.Add(wx.StaticText(self, wx.ID_ANY, _('Activation:')), 0)
            gridSizer.Add(self.excitatoryButton, 0)
            self.inhibitoryButton = wx.RadioButton(self, wx.ID_ANY, _('Inhibitory'))
            self.Bind(wx.EVT_RADIOBUTTON, self.onSetActivation, self.inhibitoryButton)
            gridSizer.AddStretchSpacer()
            gridSizer.Add(self.inhibitoryButton, 0)
            
            self.GetSizer().Add(gridSizer, 1)
        
        if self.objects.haveEqualAttr('excitatory'):
            self.excitatoryButton.SetValue(self.objects[0].excitatory)
            self.inhibitoryButton.SetValue(not self.objects[0].excitatory)
        else:
            self.excitatoryButton.SetValue(false)
            self.inhibitoryButton.SetValue(false)
        
        self.Layout()
    
    
    def onSetActivation(self, event):
        newValue = self.excitatoryButton.GetValue()        for object in self.objects:            object.excitatory = newValue
