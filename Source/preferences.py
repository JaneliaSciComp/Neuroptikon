#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

import neuroptikon
import wx, wx.lib.colourselect


class Preferences( wx.Frame ):
    
    def __init__(self, parent=None):
        wx.Frame.__init__(self, parent, wx.ID_ANY, gettext('Preferences'), size = (300, 200), pos = (-1,-1))
        
        # Build the UI
        backgroundColor = wx.Color(neuroptikon.config.ReadFloat('Color/Background/Red', 0.7) * 255, \
                                   neuroptikon.config.ReadFloat('Color/Background/Green', 0.8) * 255, \
                                   neuroptikon.config.ReadFloat('Color/Background/Blue', 0.7) * 255, \
                                   neuroptikon.config.ReadFloat('Color/Background/Alpha', 1.0) * 255)
        self.colorPicker = wx.lib.colourselect.ColourSelect(self, wx.ID_ANY, "", backgroundColor)    #wx.ColourPickerCtrl(self, -1, backgroundColor)
        self.Bind(wx.lib.colourselect.EVT_COLOURSELECT, self.onColorChanged)
        colorBox = wx.BoxSizer(wx.HORIZONTAL)
        colorBox.Add(wx.StaticText(self, wx.ID_ANY, gettext('Default Background Color:')), 0, wx.EXPAND)
        colorBox.AddSpacer(8)
        colorBox.Add(self.colorPicker, 1, wx.EXPAND)
        
        smoothLinesBox = wx.BoxSizer(wx.HORIZONTAL)
        self._smoothLinesCheckBox = wx.CheckBox(self, wx.ID_ANY, gettext('Smooth Lines'))
        self.Bind(wx.EVT_CHECKBOX, self.onSetSmoothLines, self._smoothLinesCheckBox)
        self._smoothLinesCheckBox.SetValue(neuroptikon.config.ReadBool('Smooth Lines'))
        smoothLinesBox.Add(self._smoothLinesCheckBox)
        
        self._defaultScript = gettext('# Enter any Python code that should run when Neuroptikon starts up.\n\n')
        startupScript = neuroptikon.config.Read('Startup Script', self._defaultScript)
        self._scriptCtrl = wx.TextCtrl(self, wx.ID_ANY, startupScript, style = wx.TE_MULTILINE)
        self.Bind(wx.EVT_TEXT, self.onSetStartupScript, self._scriptCtrl)
        
        # Bundle them together
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(colorBox, 0, wx.ALL, 5)
        self.mainSizer.Add(smoothLinesBox, 0, wx.ALL, 5)
        self.mainSizer.Add(wx.StaticText(self, wx.ID_ANY, gettext('Startup script')), 0, wx.TOP | wx.LEFT, 5)
        self.mainSizer.Add(self._scriptCtrl, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(self.mainSizer)
        
        self.Bind(wx.EVT_CLOSE, self.onClose)
        
        self.Fit()
    
    
    def onColorChanged(self, event):
        color = self.colorPicker.GetColour()
        neuroptikon.config.WriteFloat('Color/Background/Red', color.Red() / 255.0)
        neuroptikon.config.WriteFloat('Color/Background/Green', color.Green() / 255.0)
        neuroptikon.config.WriteFloat('Color/Background/Blue', color.Blue() / 255.0)
        neuroptikon.config.WriteFloat('Color/Background/Alpha', color.Alpha() / 255.0)
    
    
    def onSetSmoothLines(self, event_):
        newValue = self._smoothLinesCheckBox.GetValue()
        neuroptikon.config.WriteBool('Smooth Lines', newValue)
    
    
    def onSetStartupScript(self, event_):
        newValue = self._scriptCtrl.GetValue()
        if newValue == '' or newValue == self._defaultScript:
            neuroptikon.config.DeleteEntry('Startup Script')
        else:
            neuroptikon.config.Write('Startup Script', newValue)
        
    
    def onClose(self, event=None):
        self.Hide()
        return True
    
