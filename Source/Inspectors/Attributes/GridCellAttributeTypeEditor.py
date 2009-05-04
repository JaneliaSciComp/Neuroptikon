import wx, wx.grid
import weakref
from Network.Attribute import Attribute


class GridCellAttributeTypeEditor(wx.grid.PyGridCellEditor):
    
    def __init__(self, grid):
        self.gridRef = weakref.ref(grid)
        
        wx.grid.PyGridCellEditor.__init__(self)


    def Create(self, parent, id, evtHandler):
        self._tc = wx.Choice(parent, id, (100, 50), choices = Attribute.TYPES)

        self.SetControl(self._tc)
        if evtHandler:
            self._tc.PushEventHandler(evtHandler)


    def SetSize(self, rect):
        self._tc.SetDimensions(rect.x, rect.y, rect.width + 2, rect.height + 2, wx.SIZE_ALLOW_MINUS_ONE)


    def BeginEdit(self, row, col, grid):
        self.startValue = grid.GetTable().GetValue(row, col)
        self._tc.SetStringSelection(self.startValue)
        self._tc.SetFocus()


    def EndEdit(self, row, col, grid):
        changed = False

        val = self._tc.GetStringSelection()
        if val != self.startValue:
            changed = True
            grid.GetTable().SetValue(row, col, val) # update the table

        self.startValue = 'zero'
        self._tc.SetStringSelection('zero')
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
        pass
#        grid = self.gridRef()
#        if grid is not None:
#            if grid.CanEnableCellControl():
#                grid.EnableCellEditControl()
        


    def Destroy(self):
        self.base_Destroy()


    def Clone(self):
        return GridCellAttributeTypeEditor(self.gridRef())

