#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

import wx


class FeedbackDialog(wx.Dialog):
    
    def __init__(self, parent = None, dialogId = -1, title = 'Send Feedback', size = (400, 250), style = wx.DEFAULT_FRAME_STYLE | wx.FRAME_TOOL_WINDOW, *args, **keywordArgs):
        wx.Dialog.__init__(self, parent, dialogId, title, size, style=style, *args, **keywordArgs)
        
        gridSizer = wx.FlexGridSizer(5, 2, 4, 4)
        gridSizer.Add(wx.StaticText(self, wx.ID_ANY, gettext('I would like to:')), 0, wx.ALIGN_RIGHT)
        self._reportBugButton = wx.RadioButton(self, wx.ID_ANY, gettext('Report a bug'), style = wx.RB_GROUP)
        self._reportBugButton.SetValue(True)
        gridSizer.Add(self._reportBugButton)
        gridSizer.AddSpacer(0)
        self._requestFeatureButton = wx.RadioButton(self, wx.ID_ANY, gettext('Request a feature'))
        gridSizer.Add(self._requestFeatureButton)
        gridSizer.Add(wx.StaticText(self, wx.ID_ANY, gettext('Summary:')), 0, wx.ALIGN_RIGHT)
        self._summaryField = wx.TextCtrl(self, wx.ID_ANY, '')
        gridSizer.Add(self._summaryField, 1, wx.EXPAND)
        gridSizer.Add(wx.StaticText(self, wx.ID_ANY, gettext('Description:')), 0, wx.ALIGN_RIGHT)
        self._descriptionField = wx.TextCtrl(self, wx.ID_ANY, '', style = wx.TE_MULTILINE)
        gridSizer.Add(self._descriptionField, 1, wx.EXPAND)
        gridSizer.Add(wx.StaticText(self, wx.ID_ANY, gettext('Contact E-mail:')), 0, wx.ALIGN_RIGHT)
        self._contactEmailField = wx.TextCtrl(self, wx.ID_ANY, '')
        gridSizer.Add(self._contactEmailField, 1, wx.EXPAND)
        gridSizer.AddGrowableCol(1)
        gridSizer.AddGrowableRow(3)
        
        buttonSizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        for buttonItem in buttonSizer.GetChildren():
            button = buttonItem.GetWindow()
            if button and button.GetId() == wx.ID_OK:
                self._okButton = buttonItem.GetWindow()
        
        self._okButton.Enable(False)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(gridSizer, 1, wx.EXPAND | wx.ALL, 8)
        mainSizer.AddSpacer(4)
        mainSizer.AddSizer(buttonSizer, 0, wx.EXPAND)
        mainSizer.AddSpacer(8)
        self.SetSizer(mainSizer)
        
        self.SetMinSize(wx.Size(*size))
        self.Fit()
        
        self.Bind(wx.EVT_TEXT, self.onTextChanged)
    
    
    def onTextChanged(self, event_):
        self._okButton.Enable(self._summaryField.GetValue() != '' and self._descriptionField.GetValue() != '' and '@' in self._contactEmailField.GetValue()[1:-4])
     
    
    def isBugReport(self):
        return self._reportBugButton.GetValue()    
    
    
    def isFeatureRequest(self):
        return self._requestFeatureButton.GetValue()
    
    
    def summary(self):
        return self._summaryField.GetValue()
    
    
    def description(self):
        return self._descriptionField.GetValue()
    
    
    def contactEmail(self):
        return self._contactEmailField.GetValue()
    