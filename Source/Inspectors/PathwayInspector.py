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
        return ['region1', 'region1Projects', 'region2', 'region2Projects']
    
    
    def objectSizer(self, parentWindow):
        if not hasattr(self, '_sizer'):
            self._sizer = wx.BoxSizer(wx.VERTICAL)
            
            regionImage = Region.image()
            if regionImage != None:
                self._regionBitmap = wx.BitmapFromImage(regionImage.Rescale(16, 16, wx.IMAGE_QUALITY_HIGH))
            else:
                self._regionBitmap = None
            
            region1Sizer = wx.BoxSizer(wx.HORIZONTAL)
            region1Sizer.Add(wx.StaticText(parentWindow, wx.ID_ANY, gettext('Region 1:')))
            if self._regionBitmap:
                region1Sizer.Add(wx.StaticBitmap(parentWindow, wx.ID_ANY, self._regionBitmap), 0, wx.LEFT, 4)
            self._region1NameField = wx.StaticText(parentWindow, wx.ID_ANY)
            region1Sizer.Add(self._region1NameField, 0, wx.LEFT, 4)
            self._selectRegion1Button = wx.Button(parentWindow, wx.ID_ANY, gettext('Select'), style = wx.BU_EXACTFIT)
            self._selectRegion1Button.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)
            self._selectRegion1Button.SetSize(wx.Size(50, self._selectRegion1Button.GetSize().GetHeight()))
            self._selectRegion1Button.SetMinSize(self._selectRegion1Button.GetSize())
            self._window.Bind(wx.EVT_BUTTON, self.onSelectRegion, self._selectRegion1Button)
            region1Sizer.Add(self._selectRegion1Button, 0, wx.LEFT, 8)
            self._sizer.Add(region1Sizer, 0, wx.TOP, 10)
            
            region1ProjectsSizer = wx.BoxSizer(wx.HORIZONTAL)
            region1ProjectsSizer.Add(wx.StaticText(parentWindow, wx.ID_ANY, gettext('Projects:')), 0, wx.LEFT, 16)
            self._projectsChoice1 = wx.Choice(parentWindow, wx.ID_ANY)
            self._projectsChoice1.Append(gettext('Yes'), True)
            self._projectsChoice1.Append(gettext('No'), False)
            self._projectsChoice1.Append(gettext('Unknown'), None)
            parentWindow.Bind(wx.EVT_CHOICE, self.onChooseProjects, self._projectsChoice1)
            self._multipleSendsOuputs1Id = wx.NOT_FOUND
            region1ProjectsSizer.Add(self._projectsChoice1, 0, wx.LEFT, 4)
            self._sizer.Add(region1ProjectsSizer, 0, wx.TOP, 8)
            
            region2Sizer = wx.BoxSizer(wx.HORIZONTAL)
            region2Sizer.Add(wx.StaticText(parentWindow, wx.ID_ANY, gettext('Region 2:')))
            if self._regionBitmap:
                region2Sizer.Add(wx.StaticBitmap(parentWindow, wx.ID_ANY, self._regionBitmap), 0, wx.LEFT, 4)
            self._region2NameField = wx.StaticText(parentWindow, wx.ID_ANY)
            region2Sizer.Add(self._region2NameField, 0, wx.LEFT, 4)
            self._selectRegion2Button = wx.Button(parentWindow, wx.ID_ANY, gettext('Select'), style = wx.BU_EXACTFIT)
            self._selectRegion2Button.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)
            self._selectRegion2Button.SetSize(wx.Size(50, self._selectRegion2Button.GetSize().GetHeight()))
            self._selectRegion2Button.SetMinSize(self._selectRegion2Button.GetSize())
            self._window.Bind(wx.EVT_BUTTON, self.onSelectRegion, self._selectRegion2Button)
            region2Sizer.Add(self._selectRegion2Button, 0, wx.LEFT, 8)
            self._sizer.Add(region2Sizer, 0, wx.TOP, 20)
            
            region2ProjectsSizer = wx.BoxSizer(wx.HORIZONTAL)
            region2ProjectsSizer.Add(wx.StaticText(parentWindow, wx.ID_ANY, gettext('Projects:')), 0, wx.LEFT, 16)
            self._projectsChoice2 = wx.Choice(parentWindow, wx.ID_ANY)
            self._projectsChoice2.Append(gettext('Yes'), True)
            self._projectsChoice2.Append(gettext('No'), False)
            self._projectsChoice2.Append(gettext('Unknown'), None)
            parentWindow.Bind(wx.EVT_CHOICE, self.onChooseProjects, self._projectsChoice2)
            self._multipleSendsOuputs2Id = wx.NOT_FOUND
            region2ProjectsSizer.Add(self._projectsChoice2)
            self._sizer.Add(region2ProjectsSizer, 0, wx.TOP, 8)
            
            self._sizer.AddStretchSpacer()
            
            self._sizer.Layout()
        
        return self._sizer
    
    
    def populateObjectSizer(self, attribute = None):
        if attribute is None or attribute == 'region1':
            if self.objects.haveEqualAttr('region1'):
                if self.objects[0].region1 is None:
                    self._region1NameField.SetLabel(gettext('None'))
                    self._selectRegion1Button.Disable()
                else:
                    self._region1NameField.SetLabel(self.objects[0].region1.name or gettext('Unnamed region'))
                    self._selectRegion1Button.Enable()
            else:
                self._region1NameField.SetLabel(gettext('Multiple values'))
                self._selectRegion1Button.Disable()
        
        if attribute is None or attribute == 'region1Projects':
            if self.objects.haveEqualAttr('region1Projects'):
                if self.objects[0].region1Projects is None:
                    self._projectsChoice1.SetSelection(2)
                elif self.objects[0].region1Projects:
                    self._projectsChoice1.SetSelection(0)
                else:
                    self._projectsChoice1.SetSelection(1)
            else:
                self._multipleSendsOuputs1Id = self._projectsChoice1.Append(gettext('Multiple values'))
                self._projectsChoice1.SetSelection(3)
            
        if attribute is None or attribute == 'region2':
            if self.objects.haveEqualAttr('region2'):
                if self.objects[0].region2 is None:
                    self._region2NameField.SetLabel(gettext('None'))
                    self._selectRegion2Button.Disable()
                else:
                    self._region2NameField.SetLabel(self.objects[0].region2.name or gettext('Unnamed region'))
                    self._selectRegion2Button.Enable()
            else:
                self._region2NameField.SetLabel(gettext('Multiple values'))
                self._selectRegion2Button.Disable()
        
        if attribute is None or attribute == 'region2Projects':
            if self.objects.haveEqualAttr('region2Projects'):
                if self.objects[0].region2Projects is None:
                    self._projectsChoice2.SetSelection(2)
                elif self.objects[0].region2Projects:
                    self._projectsChoice2.SetSelection(0)
                else:
                    self._projectsChoice2.SetSelection(1)
            else:
                self._multipleSendsOuputs2Id = self._projectsChoice2.Append(gettext('Multiple values'))
                self._projectsChoice2.SetSelection(3)
        
        self._sizer.Layout()
    
    
    def onSelectRegion(self, event):
        if event.EventObject == self._selectRegion1Button:
            self.selectObject(self.objects[0].region1)
        elif event.EventObject == self._selectRegion2Button:
            self.selectObject(self.objects[0].region2)
        
    
    def onChooseProjects(self, event):
        if event.EventObject == self._projectsChoice1:
            if self._projectsChoice1.GetSelection() != 3:
                projects = self._projectsChoice1.GetClientData(self._projectsChoice1.GetSelection())
                for pathway in self.objects:
                    pathway.region1Projects = projects
                # Remove the "multiple values" choice now that all of the objects have the same value.
                if self._multipleSendsOuputs1Id != wx.NOT_FOUND:
                    self._projectsChoice1.Delete(self._multipleSendsOuputs1Id)
                    self._multipleSendsOuputs1Id = wx.NOT_FOUND
        elif event.EventObject == self._projectsChoice2:
            if self._projectsChoice2.GetSelection() != 3:
                projects = self._projectsChoice2.GetClientData(self._projectsChoice2.GetSelection())
                for pathway in self.objects:
                    pathway.region2Projects = projects
                # Remove the "multiple values" choice now that all of the objects have the same value.
                if self._multipleSendsOuputs2Id != wx.NOT_FOUND:
                    self._projectsChoice2.Delete(self._multipleSendsOuputs2Id)
                    self._multipleSendsOuputs2Id = wx.NOT_FOUND
