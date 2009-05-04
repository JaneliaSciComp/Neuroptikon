import wx, wx.grid
import weakref
from Network.Attribute import Attribute


class AttributesTable(wx.grid.PyGridTableBase):
        
        self.object = None
        self._rows = 0
        self.gridRef = weakref.ref(grid)
    
    
    def getGrid(self):
        return self.gridRef()
        
    
    def setObject(self, object):
        self.object = object
        rowDiff = self.GetNumberRows() - self._rows
        if rowDiff > 0:
            self.getGrid().ProcessTableMessage(wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED, rowDiff))
        elif rowDiff < 0:
            self.getGrid().ProcessTableMessage(wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED, self.GetNumberRows(), -rowDiff))
    
    
        if self.object is None:
            return 0
        else:
    
    
    def GetColLabelValue(self, col):
        if col == 0:
            return gettext('Type')
        elif col == 1:
            return gettext('Name')
        else:
            return gettext('Value')
    
    
        attribute = self.object.attributes[row]
        if col == 0:
            return attribute.type
        elif col == 1:
            return attribute.name
        else:
            return attribute.value
    
    
        if col == 0:
            attribute.setType(value)
        elif col == 1:
            attribute.setName(value)
        else:
            attribute.setValue(value)
    
        for rowNum in range(0, numRows):
            self.object.attributes.append(Attribute(self.object, gettext('Attribute'), Attribute.STRING_TYPE, ''))
        self.getGrid().ProcessTableMessage(wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED, numRows))
        self.ResetView()
        return True
        
        del self.object.attributes[startRow:startRow + numRows]
        self.getGrid().ProcessTableMessage(wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED, startRow, numRows))
        return True
    
    
        
        grid.ProcessTableMessage(wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES))
        self._rows = self.GetNumberRows()
    