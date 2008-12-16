import wx
from Display import Visible
from Network import Object
import platform


class Inspector( wx.Frame ):
    
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "Inspector", size=(200,300), pos=(-1,-1))	#, style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_TOOL_WINDOW)
        
        # Create an empty bitmap
        emptyImage = wx.EmptyImage(32, 32)
        emptyImage.SetMaskColour(0, 0, 0)
        emptyImage.InitAlpha()
        self.emptyBitmap = emptyImage.ConvertToBitmap()
        
        # Build the header UI
        self.iconField = wx.StaticBitmap(self, -1)
        self.iconField.SetMinSize(wx.Size(32, 32))
        self.iconField.SetMaxSize(wx.Size(32, 32))
        titleSizer = wx.BoxSizer(wx.VERTICAL)
        self.titleField = wx.StaticText(self, -1, "")
        self.subTitleField = wx.StaticText(self, -1, "")
        if platform.system() == 'Windows':
            self.subTitleField.SetForegroundColour('LIGHT GRAY')
        else:
            self.subTitleField.SetForegroundColour('GRAY')
        titleSizer.Add(self.titleField, 0, wx.EXPAND)
        titleSizer.Add(self.subTitleField, 0, wx.EXPAND)
        headerBox = wx.BoxSizer(wx.HORIZONTAL)
        headerBox.Add(self.iconField, 0, wx.EXPAND)
        headerBox.AddSpacer(8)
        headerBox.Add(titleSizer, 1, wx.EXPAND)
        
        # Build the no selection UI
        self.noSelectionBox = wx.BoxSizer(wx.VERTICAL)
        noSelectionField = wx.StaticText(self, -1, "No selection")
        noSelectionField.SetForegroundColour('GRAY')
        self.noSelectionBox.Add(noSelectionField, 1, wx.ALIGN_CENTER_VERTICAL)
        
        # Build the single selection UI
        self.text = wx.StaticText(self, -1, "")
        self.singleSelectionBox = wx.BoxSizer(wx.VERTICAL)
        self.singleSelectionBox.Add(self.text, 1, wx.EXPAND )
        
        # Build the multi selection UI
        self.multiGridSizer = wx.FlexGridSizer(0, 3, 8, 8)
        self.multiGridSizer.SetFlexibleDirection(wx.HORIZONTAL)
        self.multiSelectionBox = wx.BoxSizer(wx.VERTICAL)
        self.multiSelectionBox.Add(self.multiGridSizer, 1, wx.EXPAND)
        
        # Build the footer UI
        self.fixedPositionCheckBox = wx.CheckBox(self, -1, "Fixed position", wx.DefaultPosition, wx.DefaultSize, wx.CHK_3STATE)
        self.Bind(wx.EVT_CHECKBOX, self.onSetPositionIsFixed)
        self.footerBox = wx.BoxSizer(wx.VERTICAL)
        self.footerBox.Add(self.fixedPositionCheckBox, 0, wx.EXPAND )
        
        # Bundle them together
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(headerBox, 0, wx.ALL, 5)
        self.mainSizer.Add(self.noSelectionBox, 1, wx.ALIGN_CENTER | wx.ALL, 5)
        self.mainSizer.Add(self.singleSelectionBox, 1, wx.EXPAND | wx.ALL, 5)
        self.mainSizer.Add(self.multiSelectionBox, 1, wx.EXPAND | wx.ALL, 5)
        self.mainSizer.Add(self.footerBox, 0, wx.ALL, 5)
        self.SetSizer(self.mainSizer)
        
        # Set the initial display state (no selection)
        self.mainSizer.Hide(self.singleSelectionBox, True)
        self.mainSizer.Hide(self.multiSelectionBox, True)
        self.fixedPositionCheckBox.Enable(False)
        
        self.Bind(wx.EVT_CLOSE, self.Close)
    
    
    def inspectObjects(self, display, objects):
        self.objects = objects
        self.display = display
        if len(objects) == 0:
            self.iconField.SetBitmap(self.emptyBitmap)
            self.titleField.SetLabel("")
            self.subTitleField.SetLabel("")
            self.mainSizer.Show(self.noSelectionBox)
            self.mainSizer.Hide(self.singleSelectionBox)
            self.mainSizer.Hide(self.multiSelectionBox)
            self.fixedPositionCheckBox.Enable(False)
            self.fixedPositionCheckBox.Set3StateValue(wx.CHK_UNCHECKED)
        elif len(objects) == 1:
            object = self.objects[0]
            visible = display.visibleForObject(object)
            image = object.image()
            if image is None or not image.Ok():
                pass    #self.iconField.SetBitmap(wx.NullBitmap)
            else:
                scaledImage = image.Rescale(32, 32)
                self.iconField.SetBitmap(wx.BitmapFromImage(scaledImage))
            self.titleField.SetLabel(object.name or "<unnamed>")
            self.subTitleField.SetLabel(object.__class__.__name__)
            self.mainSizer.Hide(self.noSelectionBox)
            self.mainSizer.Show(self.singleSelectionBox)
            self.mainSizer.Hide(self.multiSelectionBox)
            self.fixedPositionCheckBox.SetValue(visible.positionIsFixed())
            self.fixedPositionCheckBox.Enable(True)
        else:
            self.iconField.SetBitmap(self.emptyBitmap)
            self.titleField.SetLabel(str(len(objects)) + " items selected")
            self.subTitleField.SetLabel("")
            self.multiGridSizer.Clear(True)
            allFixed = True
            allUnfixed = True
            for object in self.objects:
                bitmap = wx.StaticBitmap(self, -1)
                bitmap.SetMinSize(wx.Size(16, 16))
                bitmap.SetMaxSize(wx.Size(16, 16))
                image = object.image()
                if image is None or not image.Ok():
                    bitmap.SetBitmap(wx.NullBitmap)
                else:
                    scaledImage = image.Rescale(16, 16)
                    bitmap.SetBitmap(wx.BitmapFromImage(scaledImage))
                self.multiGridSizer.Add(bitmap)
                self.multiGridSizer.Add(wx.StaticText(self, -1, object.name or "Unnamed " + object.__class__.__name__))
                selectButton = wx.Button(self, -1, "Select", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT)
                selectButton.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)
                selectButton.SetSize(wx.Size(50, selectButton.GetSize().GetHeight()))
                selectButton.SetMinSize(selectButton.GetSize())
                self.Bind(wx.EVT_BUTTON, self.onSelectObject)
                self.multiGridSizer.Add(selectButton, 0, 0, 0, object)
                visible = display.visibleForObject(object)
                if visible.positionIsFixed():
                    allUnfixed = False
                else:
                    allFixed = False
            self.mainSizer.Hide(self.noSelectionBox)
            self.mainSizer.Hide(self.singleSelectionBox)
            self.mainSizer.Show(self.multiSelectionBox)
            if allFixed:
                self.fixedPositionCheckBox.Set3StateValue(wx.CHK_CHECKED)
            elif allUnfixed:
                self.fixedPositionCheckBox.Set3StateValue(wx.CHK_UNCHECKED)
            else:
                self.fixedPositionCheckBox.Set3StateValue(wx.CHK_UNDETERMINED)
            self.fixedPositionCheckBox.Enable(True)
        self.Layout()
    
    
    def onSetPositionIsFixed(self, event):
        newValue = self.fixedPositionCheckBox.GetValue()
        for object in self.objects:
            visible = self.display.visibleForObject(object)
            visible.setPositionIsFixed(newValue)
    
    
    def onSelectObject(self, event):
        sizerItem = self.multiGridSizer.GetItem(event.GetEventObject())
        self.display.selectObject(sizerItem.GetUserData())
        
    
    def Close(self, event=None):
        self.Hide()
        return True
    
