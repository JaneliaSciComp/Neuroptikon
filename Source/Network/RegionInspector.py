import wx
from ObjectInspector import ObjectInspector
from Region import Region


class RegionInspector( ObjectInspector ):
    
    @classmethod
    def objectClass(cls):
        return Region
    
    
    @classmethod
    def inspectedAttributes(cls):
        return ['parentRegion', 'subRegions', 'ontologyTerm']
    
    
    def objectSizer(self, parentWindow):
        if not hasattr(self, '_sizer'):
            self._sizer = wx.FlexGridSizer(1, 2, 8, 8)
            self._sizer.SetFlexibleDirection(wx.HORIZONTAL | wx.VERTICAL)
            
            regionImage = Region.image()
            if regionImage is None or not regionImage.IsOk():
                self._regionBitmap = wx.EmptyBitmap(16, 16)
            else:
                self._regionBitmap = wx.BitmapFromImage(regionImage.Rescale(16, 16))
            
            self._sizer.Add(wx.StaticText(parentWindow, wx.ID_ANY, gettext('Ontology term:')))
            ontologySizer = wx.BoxSizer(wx.HORIZONTAL)
            self._ontologyField = wx.StaticText(parentWindow, wx.ID_ANY)
            ontologySizer.Add(self._ontologyField, 1, wx.LEFT, 2)
            self._browseOntologyButton = wx.Button(parentWindow, wx.ID_ANY, gettext('Browse'), style = wx.BU_EXACTFIT)
            self._browseOntologyButton.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)
            self._browseOntologyButton.SetSize(wx.Size(60, self._browseOntologyButton.GetSize().GetHeight()))
            self._browseOntologyButton.SetMinSize(self._browseOntologyButton.GetSize())
            self._window.Bind(wx.EVT_BUTTON, self.onBrowseOntology, self._browseOntologyButton)
            ontologySizer.Add(self._browseOntologyButton, 0, wx.LEFT, 8)
            self._sizer.Add(ontologySizer)
            
            self._sizer.Add(wx.StaticText(parentWindow, wx.ID_ANY, gettext('Parent region:')))
            parentSizer = wx.BoxSizer(wx.HORIZONTAL)
            parentSizer.Add(wx.StaticBitmap(parentWindow, wx.ID_ANY, self._regionBitmap))
            self._parentNameField = wx.StaticText(parentWindow, wx.ID_ANY)
            parentSizer.Add(self._parentNameField, 1, wx.LEFT, 2)
            self._selectParentButton = wx.Button(parentWindow, wx.ID_ANY, gettext('Select'), style = wx.BU_EXACTFIT)
            self._selectParentButton.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)
            self._selectParentButton.SetSize(wx.Size(50, self._selectParentButton.GetSize().GetHeight()))
            self._selectParentButton.SetMinSize(self._selectParentButton.GetSize())
            self._window.Bind(wx.EVT_BUTTON, self.onSelectParentRegion, self._selectParentButton)
            parentSizer.Add(self._selectParentButton, 0, wx.LEFT, 8)
            self._sizer.Add(parentSizer)
            
            self._sizer.Add(wx.StaticText(parentWindow, wx.ID_ANY, gettext('Sub-regions:')))
            self._subRegionsOptions = wx.BoxSizer(wx.VERTICAL)
            self._subRegionsField = wx.StaticText(parentWindow, wx.ID_ANY)
            self._subRegionsOptions.Add(self._subRegionsField, 1, wx.EXPAND)
            self._subRegionsSizer = wx.FlexGridSizer(0, 3, 2, 5)
            self._subRegionsSizer.SetFlexibleDirection(wx.HORIZONTAL)
            self._subRegionsOptions.Add(self._subRegionsSizer, 1, wx.EXPAND)
            self._addSubRegionsButton = wx.Button(parentWindow, wx.ID_ANY, gettext('Add sub-regions from ontology'), style = wx.BU_EXACTFIT)
            self._window.Bind(wx.EVT_BUTTON, self.onAddSubRegions, self._addSubRegionsButton)
            self._subRegionsOptions.Add(self._addSubRegionsButton, 0, wx.EXPAND)
            self._sizer.Add(self._subRegionsOptions)
            
            self._parentWindow = parentWindow
        
        return self._sizer
        
    
    def populateObjectSizer(self, attribute = None):
        if attribute is None or attribute == 'ontologyTerm':
            if self.objects.haveEqualAttr('ontologyTerm'):
                if self.objects[0].ontologyTerm is None:
                    self._ontologyField.SetLabel(gettext('None'))
                    self._browseOntologyButton.Disable()
                else:
                    self._ontologyField.SetLabel(self.objects[0].ontologyTerm.name)
                    self._browseOntologyButton.Enable()
            else:
                self._ontologyField.SetLabel(gettext('Multiple values'))
                self._browseOntologyButton.Disable()
        
        if attribute is None or attribute == 'parentRegion':
            if self.objects.haveEqualAttr('parentRegion'):
                if self.objects[0].parentRegion is None:
                    self._parentNameField.SetLabel(gettext('None'))
                    self._selectParentButton.Disable()
                else:
                    self._parentNameField.SetLabel(self.objects[0].parentRegion.name or gettext('Unnamed region'))
                    self._selectParentButton.Enable()
            else:
                self._parentNameField.SetLabel(gettext('Multiple values'))
                self._selectParentButton.Disable()
        
        self._subRegionsSizer.Clear(True)
        if len(self.objects) > 1:
            self._subRegionsField.Show()
            self._subRegionsField.SetLabel(gettext('Multiple values'))
            self._subRegionsOptions.Hide(self._subRegionsSizer)
            self._addSubRegionsButton.Hide()
        else:
            region = self.objects[0]
            if len(region.subRegions) == 0:
                self._subRegionsOptions.Hide(self._subRegionsSizer)
                if region.ontologyTerm is not None and len(region.ontologyTerm.parts) > 0:
                    self._subRegionsField.Hide()
                    self._addSubRegionsButton.Show()
                else:
                    self._subRegionsField.Show()
                    self._subRegionsField.SetLabel(gettext('None'))
                    self._addSubRegionsButton.Hide()
            else:
                self._subRegionsField.Hide()
                self._addSubRegionsButton.Hide()
                self._subRegionsOptions.Show(self._subRegionsSizer)
                for subRegion in self.objects[0].subRegions:
                    self._subRegionsSizer.Add(wx.StaticBitmap(self._parentWindow, wx.ID_ANY, self._regionBitmap))
                    self._subRegionsSizer.Add(wx.StaticText(self._parentWindow, wx.ID_ANY, subRegion.name or gettext('Unnamed region')))
                    selectButton = wx.Button(self._parentWindow, wx.ID_ANY, gettext('Select'), style = wx.BU_EXACTFIT)
                    selectButton.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)
                    selectButton.SetSize(wx.Size(50, selectButton.GetSize().GetHeight()))
                    selectButton.SetMinSize(selectButton.GetSize())
                    self._parentWindow.Bind(wx.EVT_BUTTON, self.onSelectSubRegion, selectButton)
                    self._subRegionsSizer.Add(selectButton, 0, 0, 0, subRegion)
        
        self._window.Layout()
    
    
    def onBrowseOntology(self, event):
        self.objects[0].ontologyTerm.browse()
    
    
    def onSelectParentRegion(self, event):
        self.selectObject(self.objects[0].parentRegion)
        
    
    def onAddSubRegions(self, event):
        region = self.objects[0]
        for term in region.ontologyTerm.parts:
            region.network.createRegion(ontologyTerm = term, parentRegion = region, addSubTerms = wx.GetKeyState(wx.WXK_ALT))
    
    
    def onSelectSubRegion(self, event):
        sizerItem = self._subRegionsSizer.GetItem(event.GetEventObject())
        subRegion = sizerItem.GetUserData()
        self.selectObject(subRegion)
    
