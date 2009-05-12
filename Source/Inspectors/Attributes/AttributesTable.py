import wx, wx.grid
from wx.py import dispatcher
import sys, weakref
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
    
    
    def CanGetValueAs(self, row, col, type):
        if col == 2:
            attribute = self.object.attributes[row]
            if type == wx.grid.GRID_VALUE_NUMBER:
                return attribute.type == Attribute.INTEGER_TYPE
            elif type == wx.grid.GRID_VALUE_FLOAT:
                return attribute.type == Attribute.DECIMAL_TYPE
            elif type == wx.grid.GRID_VALUE_BOOL:
                return attribute.type == Attribute.BOOLEAN_TYPE
            elif type == wx.grid.GRID_VALUE_DATETIME:
                return attribute.type == Attribute.DATETIME_TYPE
        return False
    
    
    def GetValue(self, row, col):
        attribute = self.object.attributes[row]
        dispatcher.connect(self.attributeDidChange, ('set', 'type'), attribute)
        dispatcher.connect(self.attributeDidChange, ('set', 'name'), attribute)
        dispatcher.connect(self.attributeDidChange, ('set', 'value'), attribute)
        if col == 0:
            return attribute.type
        elif col == 1:
            return attribute.name
        else:
            return attribute.value
    
    
    def attributeDidChange(self, signal, sender):
        self.ResetView()
    
    
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
            try:
                if attribute.type == Attribute.BOOLEAN_TYPE:
                    value = value == 1
                elif attribute.type == Attribute.DATETIME_TYPE:
                    try:
                        value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                    except:
                        raise ValueError, gettext('Date time values must be in YYYY-MM-DD HH:MM:SS format')
                elif attribute.type == Attribute.DATE_TYPE:
                    try:
                        value = datetime.strptime(value, '%Y-%m-%d').date()
                    except:
                        raise ValueError, gettext('Date values must be in YYYY-MM-DD format')
                elif attribute.type == Attribute.TIME_TYPE:
                    try:
                        value = datetime.strptime(value, '%H:%M:%S').time()
                    except:
                        raise ValueError, gettext('Time values must be in HH:MM:SS format')
                attribute.setValue(value)
            except:
                (exceptionType, exceptionValue, exceptionTraceback) = sys.exc_info()
                dialog = wx.MessageDialog(self.gridRef().GetTopLevelParent(), exceptionValue.message, gettext('Could not set the value of the attribute:'), style = wx.ICON_ERROR | wx.OK)
                dialog.ShowModal()
    
    
    def CanSetValueAs(self, row, col, type):
        if col == 2:
            attribute = self.object.attributes[row]
            if type == wx.grid.GRID_VALUE_NUMBER:
                return attribute.type == Attribute.INTEGER_TYPE
            elif type == wx.grid.GRID_VALUE_FLOAT:
                return attribute.type == Attribute.DECIMAL_TYPE
            elif type == wx.grid.GRID_VALUE_BOOL:
                return attribute.type == Attribute.BOOLEAN_TYPE
            elif type == wx.grid.GRID_VALUE_DATETIME:
                return attribute.type == Attribute.DATETIME_TYPE
        return False
    
    
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
        
        if grid is not None:
            grid.ProcessTableMessage(wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES))
            self._rows = self.GetNumberRows()

            grid.AdjustScrollbars()
            grid.ForceRefresh()
    
