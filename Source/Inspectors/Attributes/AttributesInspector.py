import os, sys
import wx, wx.grid
from wx.py import dispatcher
from Inspection.Inspector import Inspector
from Network.ObjectList import ObjectList
from Display.Visible import Visible
from Network.Attribute import Attribute
from AttributesTable import AttributesTable
from GridCellAttributeTypeEditor import GridCellAttributeTypeEditor
from GridCellAttributeTypeRenderer import GridCellAttributeTypeRenderer


class AttributesInspector(Inspector):
    
    @classmethod
    def name(cls):
        return gettext('Attributes')
    
    
    @classmethod
    def canInspectDisplay(cls, display):
        return len(display.selection()) == 0 or (len(display.selection()) == 1 and display.selection()[0].client is not None)
    
    
    def loadBitmap(self, fileName):
        # Check for an Icon.png in the same directory as this class's module's source file, otherwise return an empty bitmap.
        iconDir = os.path.dirname(sys.modules[self.__class__.__module__].__file__)
        try:
            image = wx.Image(iconDir + os.sep + fileName)
        except:
            image = None
        if image is not None and image.IsOk():
            image.Rescale(16, 16)
            return image.ConvertToBitmap()
        else:
            return wx.EmptyBitmap(16, 16)


    def window(self, parentWindow=None):
        if not hasattr(self, '_window'):
            self._window = wx.Window(parentWindow, wx.ID_ANY)
            
            self.label = wx.StaticText(self._window, wx.ID_ANY)
            
            self.grid = wx.grid.Grid(self._window, wx.ID_ANY, wx.DefaultPosition, wx.Size(300, 100))
            self.grid.SetColLabelSize(18)
            self.grid.SetRowLabelSize(0)
            self.grid.EnableGridLines(False)
            self.attributesTable = AttributesTable(self.grid)
            self.grid.SetTable(self.attributesTable)
            self.grid.SetSelectionMode(wx.grid.Grid.SelectRows)
            typeColAttr = wx.grid.GridCellAttr()            typeColAttr.SetEditor(GridCellAttributeTypeEditor(self))            typeColAttr.SetRenderer(GridCellAttributeTypeRenderer(self))            self.grid.SetColAttr(0, typeColAttr)
            nameColAttr = wx.grid.GridCellAttr()
            boldFont = self.grid.GetDefaultCellFont()
            boldFont.SetWeight(wx.FONTWEIGHT_BOLD)
            nameColAttr.SetFont(boldFont)            self.grid.SetColAttr(1, nameColAttr)
            self.grid.SetCellHighlightPenWidth(0)
            self._window.Bind(wx.EVT_SIZE, self.onResizeLastColumn)            self._window.Bind(wx.EVT_SIZE, self.onResizeLastColumn, self.grid)            self._window.Bind(wx.grid.EVT_GRID_COL_SIZE, self.onResizeLastColumn, self.grid)
            self._window.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.onCellSelected, self.grid)
                        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
            addButton = wx.BitmapButton(self._window, wx.ID_ANY, self.loadBitmap('Add.png'), wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT)
            addButton.SetSize(wx.Size(16, 16))
            addButton.SetMinSize(addButton.GetSize())
            self._window.Bind(wx.EVT_BUTTON, self.onAddAttribute, addButton)
            buttonSizer.Add(addButton)
            removeButton = wx.BitmapButton(self._window, wx.ID_ANY, self.loadBitmap('Remove.png'), wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT)
            removeButton.SetSize(wx.Size(16, 16))
            removeButton.SetMinSize(removeButton.GetSize())
            self._window.Bind(wx.EVT_BUTTON, self.onRemoveAttribute, removeButton)
            buttonSizer.Add(removeButton)
            
            mainSizer = wx.BoxSizer(wx.VERTICAL)
            mainSizer.Add(self.label, 0, wx.EXPAND | wx.LEFT | wx.TOP | wx.RIGHT, 5)
            mainSizer.Add(self.grid, 1, wx.EXPAND | wx.ALL, 5)
            mainSizer.Add(buttonSizer, 0, wx.LEFT | wx.BOTTOM | wx.RIGHT, 5)
            self._window.SetSizer(mainSizer)
            
            # Load the icons for each attribute type
            self.icons = {}
            for iconName in Attribute.TYPES:
                self.icons[iconName] = self.loadBitmap(iconName + '.png')
        
        return self._window
    
    
    def inspectDisplay(self, display):
        if len(display.selection()) == 0:
            object = display.network
            self.label.SetLabel(gettext('Attributes of the network:'))
        else:
            object = display.selection()[0].client
            if object.name is None:
                self.label.SetLabel(gettext('Attributes of unnamed %s:') % (object.__class__.displayName().lower()))
            else:
                self.label.SetLabel(gettext('Attributes of %s %s:') % (object.__class__.displayName().lower(), object.name))
        
        self.attributesTable.setObject(object)
        self.grid.SetGridCursor(self.grid.GetNumberCols() + 1, self.grid.GetNumberRows() + 1)
        self.grid.AutoSizeColumns()
        self.onResizeLastColumn(None)
        
        self._window.Layout()
    
    
    def onCellSelected(self, event):
        self.grid.SelectRow(event.Row)
        wx.CallAfter(self.enableCellEditControl)
        event.Skip()
    
    
    def enableCellEditControl(self):
        if self.grid.CanEnableCellControl():            self.grid.EnableCellEditControl()
        
    def onAddAttribute(self, event):
        self.grid.AppendRows(1)
        rowNum = self.grid.GetNumberRows() - 1
        self.grid.SelectRow(rowNum)
        self.grid.SetGridCursor(rowNum, 1)
        event.Skip()
    
    
    def onRemoveAttribute(self, event):
        rowNums = self.grid.GetSelectedRows()
        if len(rowNums) == 1:
            if self.grid.IsCellEditControlEnabled():                self.grid.DisableCellEditControl()
            self.grid.DeleteRows(rowNums[0], 1)
        event.Skip()
    
    
    def onResizeLastColumn(self, event):
        # We're showing the vertical scrollbar -> allow for scrollbar width        # NOTE: on GTK, the scrollbar is included in the client size, but on        # Windows it is not included
        gridWidth = self.grid.GetClientSize().width#        if wx.Platform != '__WXMSW__':#            if self.GetItemCount() > self.GetCountPerPage():#                scrollWidth = wx.SystemSettings_GetMetric(wx.SYS_VSCROLL_X)#                gridWidth = gridWidth - scrollWidth        totColWidth = self.grid.GetColSize(0) + self.grid.GetColSize(1)        resizeColWidth = self.grid.GetColSize(2)        if gridWidth - totColWidth > 100:            self.grid.SetColSize(2, gridWidth - totColWidth)
        
        if event is not None:
            event.Skip()
        
    
    def willBeClosed(self):
        # Make sure any active edit gets committed.
        # TODO: test this
        if self.grid.IsCellEditControlEnabled():            self.grid.DisableCellEditControl()
    
