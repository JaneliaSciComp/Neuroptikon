#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

import wx, wx.grid, wx.combo
import weakref
from network.attribute import Attribute

USE_WX_COMBO = False


class GridCellAttributeTypeEditor(wx.grid.PyGridCellEditor):
    
    def __init__(self, inspector):
        self.inspectorRef = weakref.ref(inspector)
        
        wx.grid.PyGridCellEditor.__init__(self)


    def Create(self, parent, id, evtHandler):
        if USE_WX_COMBO:
            self._tc = wx.combo.BitmapComboBox(parent, id, style = wx.CB_READONLY)
        else:
            self._tc = wx.Choice(parent, id, (100, 50))
        for attrType in Attribute.TYPES:
            displayName = Attribute.displayNameForType(attrType)
            if USE_WX_COMBO:
                if attrType in self.inspectorRef().icons:
                    self._tc.Append(displayName, self.inspectorRef().icons[attrType], attrType)
                else:
                    self._tc.Append(displayName, wx.EmptyBitmap(16, 16), attrType)
            else:
                self._tc.Append(displayName, attrType)
        
        self.SetControl(self._tc)
        if evtHandler:
            self._tc.PushEventHandler(evtHandler)


    def SetSize(self, rect):
        self._tc.SetDimensions(rect.x, rect.y, rect.width + 2, rect.height + 2, wx.SIZE_ALLOW_MINUS_ONE)


    def BeginEdit(self, row, col, grid):
        self.startValue = grid.GetTable().GetValue(row, col)
        for i in range(self._tc.GetCount()):
            if self._tc.GetClientData(i) == self.startValue:
                self._tc.SetSelection(i)
        if USE_WX_COMBO:
            if not self._tc.IsPopupShown():
                self._tc.ShowPopup()
        else:
            self._tc.SetFocus()


    def EndEdit(self, row, col, grid):
        changed = False

        val = self._tc.GetClientData(self._tc.GetSelection())
        if val != self.startValue:
            changed = True
            grid.GetTable().SetValue(row, col, val) # update the table

        self.startValue = 'zero'
        self._tc.SetStringSelection('zero')
        if USE_WX_COMBO:
            if self._tc.IsPopupShown():
                self._tc.HidePopup()
        
        return changed


    def Reset(self):
        self._tc.SetStringSelection(self.startValue)


    def IsAcceptedKey(self, evt):
        return (not (evt.ControlDown() or evt.AltDown()) and evt.GetKeyCode() != WXK_SHIFT)


    def StartingKey(self, evt):
        key = evt.GetKeyCode()
        ch = None
        if key in [wx.WXK_NUMPAD0, wx.WXK_NUMPAD1, wx.WXK_NUMPAD2, wx.WXK_NUMPAD3, wx.WXK_NUMPAD4,
                   wx.WXK_NUMPAD5, wx.WXK_NUMPAD6, wx.WXK_NUMPAD7, wx.WXK_NUMPAD8, wx.WXK_NUMPAD9]:
            ch = chr(ord('0') + key - wx.WXK_NUMPAD0)

        elif key < 256 and key >= 0 and chr(key) in string.printable:
            ch = chr(key)
            if not evt.ShiftDown():
                ch = ch.lower()

        if ch is not None:
            self._tc.SetStringSelection(ch)
        else:
            evt.Skip()


    def StartingClick(self):
        """
        If the editor is enabled by clicking on the cell, this method will be
        called to allow the editor to simulate the click on the control if
        needed.
        """
        if USE_WX_COMBO:
            if not self._tc.IsPopupShown():
                self._tc.ShowPopup()
        


    def Destroy(self):
        self.base_Destroy()


    def Clone(self):
        return GridCellAttributeTypeEditor(self.gridRef())

