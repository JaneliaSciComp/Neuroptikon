import wx
from ObjectInspector import ObjectInspector
from Network.Pathway import Pathway
from Network.Region import Region

class PathwayInspector( ObjectInspector ):
    
    @classmethod
    def objectClass(cls):
        return Pathway
    
    
    @classmethod
    def inspectedAttributes(cls):
        return ['terminus1.region', 'terminus1.sendsOutput', 'terminus1.receivesInput', 'terminus2.region', 'terminus2.sendsOutput', 'terminus2.receivesInput']
    
    
    def objectSizer(self, parentWindow):
        if not hasattr(self, '_sizer'):
            self._sizer = wx.BoxSizer(wx.VERTICAL)
            
            regionImage = Region.image()
            if regionImage is not None and regionImage.IsOk():
                self._regionBitmap = wx.BitmapFromImage(regionImage.Rescale(16, 16))
            else:
                self._regionBitmap = None
            
            terminus1Sizer = wx.StaticBoxSizer(wx.StaticBox(parentWindow, wx.ID_ANY, gettext('Terminus 1')), wx.HORIZONTAL)
            
            gridSizer1 = wx.FlexGridSizer(3, 2, 8, 0)
            gridSizer1.SetFlexibleDirection(wx.HORIZONTAL)
            
            gridSizer1.Add(wx.StaticText(parentWindow, wx.ID_ANY, gettext('Region:')))
            regionSizer = wx.BoxSizer(wx.HORIZONTAL)
            if self._regionBitmap is not None:
                regionSizer.Add(wx.StaticBitmap(parentWindow, wx.ID_ANY, self._regionBitmap))
            self._region1NameField = wx.StaticText(parentWindow, wx.ID_ANY)
            regionSizer.Add(self._region1NameField, 1, wx.LEFT, 2)
            self._selectRegion1Button = wx.Button(parentWindow, wx.ID_ANY, gettext('Select'), style = wx.BU_EXACTFIT)
            self._selectRegion1Button.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)
            self._selectRegion1Button.SetSize(wx.Size(50, self._selectRegion1Button.GetSize().GetHeight()))
            self._selectRegion1Button.SetMinSize(self._selectRegion1Button.GetSize())
            self._window.Bind(wx.EVT_BUTTON, self.onSelectRegion, self._selectRegion1Button)
            regionSizer.Add(self._selectRegion1Button, 0, wx.LEFT, 8)
            gridSizer1.Add(regionSizer)
            
            gridSizer1.Add(wx.StaticText(parentWindow, wx.ID_ANY, gettext('Sends output to region:')))
            self._sendsOutputChoice1 = wx.Choice(parentWindow, wx.ID_ANY)
            self._sendsOutputChoice1.Append(gettext('Yes'), True)
            self._sendsOutputChoice1.Append(gettext('No'), False)
            self._sendsOutputChoice1.Append(gettext('Unknown'), None)
            self._multipleSendsOuputs1Id = wx.NOT_FOUND
            gridSizer1.Add(self._sendsOutputChoice1)
            parentWindow.Bind(wx.EVT_CHOICE, self.onChooseSendsOutput, self._sendsOutputChoice1)
            
            gridSizer1.Add(wx.StaticText(parentWindow, wx.ID_ANY, gettext('Receives input from region:')))
            self._receivesInputChoice1 = wx.Choice(parentWindow, wx.ID_ANY)
            self._receivesInputChoice1.Append(gettext('Yes'), True)
            self._receivesInputChoice1.Append(gettext('No'), False)
            self._receivesInputChoice1.Append(gettext('Unknown'), None)
            self._multipleReceivesInputs1Id = wx.NOT_FOUND
            gridSizer1.Add(self._receivesInputChoice1)
            parentWindow.Bind(wx.EVT_CHOICE, self.onChooseReceievesInput, self._receivesInputChoice1)
            
            terminus1Sizer.Add(gridSizer1, 1, wx.EXPAND)
            self._sizer.Add(terminus1Sizer, 1, wx.EXPAND | wx.ALL, 5)
            
            terminus2Sizer = wx.StaticBoxSizer(wx.StaticBox(parentWindow, wx.ID_ANY, gettext('Terminus 2')), wx.HORIZONTAL)
            
            gridSizer2 = wx.FlexGridSizer(3, 2, 8, 0)
            gridSizer2.SetFlexibleDirection(wx.HORIZONTAL)
            
            gridSizer2.Add(wx.StaticText(parentWindow, wx.ID_ANY, gettext('Region:')))
            regionSizer = wx.BoxSizer(wx.HORIZONTAL)
            if self._regionBitmap is not None:
                regionSizer.Add(wx.StaticBitmap(parentWindow, wx.ID_ANY, self._regionBitmap))
            self._region2NameField = wx.StaticText(parentWindow, wx.ID_ANY)
            regionSizer.Add(self._region2NameField, 1, wx.LEFT, 2)
            self._selectRegion2Button = wx.Button(parentWindow, wx.ID_ANY, gettext('Select'), style = wx.BU_EXACTFIT)
            self._selectRegion2Button.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)
            self._selectRegion2Button.SetSize(wx.Size(50, self._selectRegion2Button.GetSize().GetHeight()))
            self._selectRegion2Button.SetMinSize(self._selectRegion2Button.GetSize())
            self._window.Bind(wx.EVT_BUTTON, self.onSelectRegion, self._selectRegion2Button)
            regionSizer.Add(self._selectRegion2Button, 0, wx.LEFT, 8)
            gridSizer2.Add(regionSizer)
            
            gridSizer2.Add(wx.StaticText(parentWindow, wx.ID_ANY, gettext('Sends output to region:')))
            self._sendsOutputChoice2 = wx.Choice(parentWindow, wx.ID_ANY)
            self._sendsOutputChoice2.Append(gettext('Yes'), True)
            self._sendsOutputChoice2.Append(gettext('No'), False)
            self._sendsOutputChoice2.Append(gettext('Unknown'), None)
            self._multipleSendsOuputs2Id = wx.NOT_FOUND
            gridSizer2.Add(self._sendsOutputChoice2)
            parentWindow.Bind(wx.EVT_CHOICE, self.onChooseSendsOutput, self._sendsOutputChoice2)
            
            gridSizer2.Add(wx.StaticText(parentWindow, wx.ID_ANY, gettext('Receives input from region:')))
            self._receivesInputChoice2 = wx.Choice(parentWindow, wx.ID_ANY)
            self._receivesInputChoice2.Append(gettext('Yes'), True)
            self._receivesInputChoice2.Append(gettext('No'), False)
            self._receivesInputChoice2.Append(gettext('Unknown'), None)
            self._multipleReceivesInputs2Id = wx.NOT_FOUND
            gridSizer2.Add(self._receivesInputChoice2)
            parentWindow.Bind(wx.EVT_CHOICE, self.onChooseReceievesInput, self._receivesInputChoice2)
            
            terminus2Sizer.Add(gridSizer2, 1, wx.EXPAND)
            self._sizer.Add(terminus2Sizer, 1, wx.EXPAND | wx.ALL, 5)
            
            terminus1Sizer.Layout()
            terminus2Sizer.Layout()
            self._sizer.Layout()
        
        return self._sizer
    
    
    def populateObjectSizer(self, attribute = None):
        if attribute is None or attribute == 'region':
            if self.objects.haveEqualAttr('terminus1.region'):
                if self.objects[0].terminus1.region is None:
                    self._region1NameField.SetLabel(gettext('None'))
                    self._selectRegion1Button.Disable()
                else:
                    self._region1NameField.SetLabel(self.objects[0].terminus1.region.name or gettext('Unnamed region'))
                    self._selectRegion1Button.Enable()
            else:
                self._region1NameField.SetLabel(gettext('Multiple values'))
                self._selectRegion1Button.Disable()
            if self.objects.haveEqualAttr('terminus2.region'):
                if self.objects[0].terminus2.region is None:
                    self._region2NameField.SetLabel(gettext('None'))
                    self._selectRegion2Button.Disable()
                else:
                    self._region2NameField.SetLabel(self.objects[0].terminus2.region.name or gettext('Unnamed region'))
                    self._selectRegion2Button.Enable()
            else:
                self._region2NameField.SetLabel(gettext('Multiple values'))
                self._selectRegion2Button.Disable()
        
        if attribute is None or attribute == 'sendsOutput':
            if self.objects.haveEqualAttr('terminus1.sendsOutput'):
                if self.objects[0].terminus1.sendsOutput is None:
                    self._sendsOutputChoice1.SetSelection(2)
                elif self.objects[0].terminus1.sendsOutput:
                    self._sendsOutputChoice1.SetSelection(0)
                else:
                    self._sendsOutputChoice1.SetSelection(1)
            else:
                self._multipleSendsOuputs1Id = self._sendsOutputChoice1.Append(gettext('Multiple values'))
                self._sendsOutputChoice1.SetSelection(3)
            if self.objects.haveEqualAttr('terminus2.sendsOutput'):
                if self.objects[0].terminus2.sendsOutput is None:
                    self._sendsOutputChoice2.SetSelection(2)
                elif self.objects[0].terminus2.sendsOutput:
                    self._sendsOutputChoice2.SetSelection(0)
                else:
                    self._sendsOutputChoice2.SetSelection(1)
            else:
                self._multipleSendsOuputs2Id = self._sendsOutputChoice2.Append(gettext('Multiple values'))
                self._sendsOutputChoice2.SetSelection(3)
        
        if attribute is None or attribute == 'receivesInput':
            if self.objects.haveEqualAttr('terminus1.receivesInput'):
                if self.objects[0].terminus1.receivesInput is None:
                    self._receivesInputChoice1.SetSelection(2)
                elif self.objects[0].terminus1.receivesInput:
                    self._receivesInputChoice1.SetSelection(0)
                else:
                    self._receivesInputChoice1.SetSelection(1)
            else:
                self._multipleReceivesInputs1Id = self._receivesInputChoice1.Append(gettext('Multiple values'))
                self._receivesInputChoice1.SetSelection(3)
            if self.objects.haveEqualAttr('terminus2.receivesInput'):
                if self.objects[0].terminus2.receivesInput is None:
                    self._receivesInputChoice2.SetSelection(2)
                elif self.objects[0].terminus2.receivesInput:
                    self._receivesInputChoice2.SetSelection(0)
                else:
                    self._receivesInputChoice2.SetSelection(1)
            else:
                self._multipleReceivesInputs2Id = self._receivesInputChoice2.Append(gettext('Multiple values'))
                self._receivesInputChoice2.SetSelection(3)
        
        self._sizer.Layout()
    
    
    def onSelectRegion(self, event):
        if event.EventObject == self._selectRegion1Button:
            self.selectObject(self.objects[0].terminus1.region)
        elif event.EventObject == self._selectRegion2Button:
            self.selectObject(self.objects[0].terminus2.region)
        
    
    def onChooseSendsOutput(self, event):
        if event.EventObject == self._sendsOutputChoice1:
            if self._sendsOutputChoice1.GetSelection() != 3:
                sendsOutput = self._sendsOutputChoice1.GetClientData(self._sendsOutputChoice1.GetSelection())
                for pathway in self.objects:
                    pathway.terminus1.sendsOutput = sendsOutput
                # Remove the "multiple values" choice now that all of the objects have the same value.
                if self._multipleSendsOuputs1Id != wx.NOT_FOUND:
                    self._sendsOutputChoice1.Delete(self._multipleSendsOuputs1Id)
                    self._multipleSendsOuputs1Id = wx.NOT_FOUND
        elif event.EventObject == self._sendsOutputChoice2:
            if self._sendsOutputChoice2.GetSelection() != 3:
                sendsOutput = self._sendsOutputChoice2.GetClientData(self._sendsOutputChoice2.GetSelection())
                for pathway in self.objects:
                    pathway.terminus2.sendsOutput = sendsOutput
                # Remove the "multiple values" choice now that all of the objects have the same value.
                if self._multipleSendsOuputs2Id != wx.NOT_FOUND:
                    self._sendsOutputChoice2.Delete(self._multipleSendsOuputs2Id)
                    self._multipleSendsOuputs2Id = wx.NOT_FOUND
        
    
    def onChooseReceievesInput(self, event):
        if event.EventObject == self._receivesInputChoice1:
            if self._receivesInputChoice1.GetSelection() != 3:
                receivesInput = self._receivesInputChoice1.GetClientData(self._receivesInputChoice1.GetSelection())
                for pathway in self.objects:
                    pathway.terminus1.receivesInput = receivesInput
                # Remove the "multiple values" choice now that all of the objects have the same value.
                if self._multipleReceivesInputs1Id != wx.NOT_FOUND:
                    self._receivesInputChoice1.Delete(self._multipleReceivesInputs1Id)
                    self._multipleReceivesInputs1Id = wx.NOT_FOUND
        if event.EventObject == self._receivesInputChoice2:
            if self._receivesInputChoice2.GetSelection() != 3:
                receivesInput = self._receivesInputChoice2.GetClientData(self._receivesInputChoice2.GetSelection())
                for pathway in self.objects:
                    pathway.terminus2.receivesInput = receivesInput
                # Remove the "multiple values" choice now that all of the objects have the same value.
                if self._multipleReceivesInputs2Id != wx.NOT_FOUND:
                    self._receivesInputChoice2.Delete(self._multipleReceivesInputs2Id)
                    self._multipleReceivesInputs2Id = wx.NOT_FOUND
