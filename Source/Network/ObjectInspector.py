import wx
from Inspection.Inspector import Inspector
from Object import Object
from ObjectList import ObjectList


class ObjectInspector(Inspector):
    
    def objectClass(self):
        return Object
    
    
    def name(self):
        return self.objectClass().displayName()
    
    
    def bitmap(self):
        image = self.objectClass().image()
        if image is None or not image.IsOk():
            return Inspector.bitmap(self)
        else:
            scaledImage = image.Rescale(16, 16)
            return wx.BitmapFromImage(scaledImage)
    
    
    def canInspectDisplay(self, display):
        # This inspector can be used if there is at least one object of this type selected.
        for visible in display.selection():
            if visible.client.__class__ == self.objectClass():
                return True
        return False
    
    
    def inspectDisplay(self, display):
        if not hasattr(self, 'iconField'):
            self.iconField = wx.StaticBitmap(self, wx.ID_ANY)
            self.iconField.SetMinSize(wx.Size(32, 32))
            self.iconField.SetMaxSize(wx.Size(32, 32))
            self.titleField = wx.StaticText(self, wx.ID_ANY, "")
            headerBox = wx.BoxSizer(wx.HORIZONTAL)
            headerBox.Add(self.iconField, 0, wx.EXPAND)
            headerBox.AddSpacer(8)
            headerBox.Add(self.titleField, 1, wx.EXPAND)
            
            mainSizer = wx.BoxSizer(wx.VERTICAL)
            mainSizer.Add(headerBox, 0, wx.ALL, 5)
            self.SetSizer(mainSizer)
        
        self.objects = ObjectList()
        for visible in display.selection():
            if visible.client.__class__ == self.objectClass():
                self.objects.append(visible.client)
        
        # Set the icon
        image = self.objects[0].__class__.image()
        if image is None or not image.IsOk():
            pass    #self.iconField.SetBitmap(wx.NullBitmap)
        else:
            scaledImage = image.Rescale(32, 32)
            self.iconField.SetBitmap(wx.BitmapFromImage(scaledImage))
        
        # Set the name
        if self.objects.haveEqualAttr('name'):
            self.titleField.SetLabel(self.objects[0].name or ("<" + _("unnamed ") + self.objectClass().displayName().lower() + ">"))
        else:
            self.titleField.SetLabel(_("Multiple names"))
        
        # Object inspectors are supposed to work purely at the network/biological layer so they don't need to know what the display is.
        self.inspectObjects()


    def inspectObjects(self):
        pass
