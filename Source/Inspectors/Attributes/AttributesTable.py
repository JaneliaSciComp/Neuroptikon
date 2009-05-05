import wx, wx.grid
import weakref
from Network.Attribute import Attribute


class AttributesTable(wx.grid.PyGridTableBase):

    def __init__(self, grid):
        wx.grid.PyGridTableBase.__init__(self)
        
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
        self.ResetView()
    

#    def GetAttr(self, row, col, kind):
#        attr = [self.even, self.odd][row % 2]
#        attr.IncRef()
#        return attr
    
    
    def GetNumberRows(self):
        if self.object is None:
            return 0
        else:
            return len(self.object.attributes)
    
    
    def GetNumberCols(self):
        return 3
    
    
    def GetColLabelValue(self, col):
        if col == 0:
            return gettext('Type')
        elif col == 1:
            return gettext('Name')
        else:
            return gettext('Value')
        
    
    def IsEmptyCell(self, row, col):
        return False
    
    
    def GetValue(self, row, col):
        attribute = self.object.attributes[row]
        if col == 0:
            return attribute.type
        elif col == 1:
            return attribute.name
        else:
            return attribute.value
    
    
    def GetTypeName(self, row, col):
        if col == 0:
            return 'Attribute.Type'
        elif col == 1:
            return Attribute.STRING_TYPE
        else:
            attribute = self.object.attributes[row]
            return attribute.type
    
    
    def SetValue(self, row, col, value):
        attribute = self.object.attributes[row]
        if col == 0:
            attribute.setType(value)
        elif col == 1:
            attribute.setName(value)
        else:
            attribute.setValue(value)
    
    
    def AppendRows(self, numRows):
        for rowNum in range(0, numRows):
            self.object.attributes.append(Attribute(self.object, gettext('Attribute'), Attribute.STRING_TYPE, ''))
        self.getGrid().ProcessTableMessage(wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED, numRows))
        self.ResetView()
        return True
        
    
    def DeleteRows(self, startRow, numRows):
        del self.object.attributes[startRow:startRow + numRows]
        self.getGrid().ProcessTableMessage(wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED, startRow, numRows))
        self.ResetView()
        return True
    
    
    def ResetView(self):
        grid = self.getGrid()
        
        grid.ProcessTableMessage(wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES))
        self._rows = self.GetNumberRows()

        grid.AdjustScrollbars()
        grid.ForceRefresh()
    
