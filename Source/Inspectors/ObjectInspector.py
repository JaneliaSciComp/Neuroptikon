import wx
from Inspection.Inspector import Inspector
from Network.Object import Object
from Network.ObjectList import ObjectList
from wx.py import dispatcher


class ObjectInspector(Inspector):
    
    @classmethod
    def name(cls):
        return cls.objectClass().displayName()
    
    
    @classmethod
    def shouldBeRegistered(cls):
        return cls != ObjectInspector.__class__
    
    
    @classmethod
    def objectClass(cls):
        return Object
    
    
    @classmethod
    def inspectedAttributes(cls):
        return []
    
    
    @classmethod
    def bitmap(cls):
        image = cls.objectClass().image()
        if image is None or not image.IsOk():
            return Inspector.bitmap(cls)
        else:
            scaledImage = image.Rescale(16, 16)
            return wx.BitmapFromImage(scaledImage)
    
    
    @classmethod
    def canInspectDisplay(cls, display):
        # This inspector can be used if there is at least one object of this type selected.
        for visible in display.selection():
            if visible.client.__class__ == cls.objectClass():
                return True
        return False
    

    def window(self, parentWindow=None):
        if not hasattr(self, '_window'):
            self._window = wx.Window(parentWindow, wx.ID_ANY)
            
            self.iconField = wx.StaticBitmap(self._window, wx.ID_ANY)
            self.iconField.SetMinSize(wx.Size(32, 32))
            self.iconField.SetMaxSize(wx.Size(32, 32))
            self.titleField = wx.StaticText(self._window, wx.ID_ANY, "")
            headerBox = wx.BoxSizer(wx.HORIZONTAL)
            headerBox.Add(self.iconField, 0, wx.EXPAND)
            headerBox.AddSpacer(8)
            headerBox.Add(self.titleField, 1, wx.EXPAND)
            
            objectSizer = self.objectSizer(self._window)
            
            mainSizer = wx.BoxSizer(wx.VERTICAL)
            mainSizer.Add(headerBox, 0, wx.ALL, 5)
            if objectSizer is not None:
                mainSizer.Add(objectSizer, 1, wx.ALL, 5)
            self._window.SetSizer(mainSizer)
        
        return self._window

    
    def inspectDisplay(self, display):
        # Object inspectors are supposed to work purely at the network/biological layer so they don't need to know what the display is.
        self.display = display
        
        self.objects = ObjectList()
        for visible in display.selection():
            if visible.client.__class__ == self.__class__.objectClass():
                self.objects.append(visible.client)
                dispatcher.connect(self.nameChanged, ('set', 'name'), visible.client)
                for attributePath in self.inspectedAttributes():
                    if '.' in attributePath:
                        (subObject, attribute) = attributePath.split('.')
                        object = getattr(visible.client, subObject)
                    else:
                        object = visible.client
                        attribute = attributePath
                    dispatcher.connect(self.inspectedAttributeChanged, ('set', attribute), object)
        
        # Set the icon
        image = self.objects[0].__class__.image()
        if image is None or not image.IsOk():
            pass
        else:
            scaledImage = image.Rescale(32, 32)
            self.iconField.SetBitmap(wx.BitmapFromImage(scaledImage))
        
        self.populateNameField()
        self.populateObjectSizer()
        self._window.Layout()
    
    
    def objectSizer(self, parentWindow):
        return None
    
    
    def populateNameField(self):
        if self.objects.haveEqualAttr('name'):
            self.titleField.SetLabel(self.objects[0].name or ('<' + gettext('unnamed ') + self.__class__.objectClass().displayName().lower() + '>'))
        else:
            self.titleField.SetLabel(gettext('Multiple names'))
    
    
    def populateObjectSizer(self, attribute = None):
        pass
    
    
    def nameChanged(self, signal, sender, event=None, value=None, **arguments):
        self.populateNameField()
    
    
    def inspectedAttributeChanged(self, signal, sender, **arguments):
        self.populateObjectSizer(signal[1])
    
    
    def selectObject(self, object):
        self.display.selectObject(object)
    
