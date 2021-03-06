#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

import os, sys
import wx, wx.grid
from pydispatch import dispatcher
from inspection.inspector import Inspector
from network.object_list import ObjectList
#from display.visible import Visible
from network.attribute import Attribute
from attributes_table import AttributesTable
from grid_cell_attribute_type_editor import GridCellAttributeTypeEditor
from grid_cell_attribute_type_renderer import GridCellAttributeTypeRenderer


class AttributesInspector(Inspector):
    
    @classmethod
    def name(cls):
        return gettext('Attributes')
    
    
    @classmethod
    def canInspectDisplay(cls, display):
        return display and (not any(display.selection()) or (len(display.selection()) == 1 and display.selection()[0].client is not None))
    
    
    def loadBitmap(self, fileName):
        # Check for an Icon.png in the same directory as this class's module's source file, otherwise return an empty bitmap.
        iconDir = os.path.dirname(sys.modules[self.__class__.__module__].__file__)
        try:
            image = wx.Image(iconDir + os.sep + fileName)
        except:
            image = None
        if image is not None and image.IsOk():
            image.Rescale(16, 16, wx.IMAGE_QUALITY_HIGH)
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
            typeColAttr = wx.grid.GridCellAttr()
            typeColAttr.SetEditor(GridCellAttributeTypeEditor(self))
            typeColAttr.SetRenderer(GridCellAttributeTypeRenderer(self))
            self.grid.SetColAttr(0, typeColAttr)
            nameColAttr = wx.grid.GridCellAttr()
            boldFont = self.grid.GetDefaultCellFont()
            boldFont.SetWeight(wx.FONTWEIGHT_BOLD)
            nameColAttr.SetFont(boldFont)
            self.grid.SetColAttr(1, nameColAttr)
            self.grid.SetCellHighlightPenWidth(0)
            self._window.Bind(wx.EVT_SIZE, self.onResizeLastColumn)
            self._window.Bind(wx.EVT_SIZE, self.onResizeLastColumn, self.grid)
            self._window.Bind(wx.grid.EVT_GRID_COL_SIZE, self.onResizeLastColumn, self.grid)
            self._window.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.onCellSelected, self.grid)
            
            self._typeRenderer = GridCellAttributeTypeRenderer(self)
            self._typeEditor = GridCellAttributeTypeEditor(self)
            self.grid.RegisterDataType('Attribute.Type', self._typeRenderer, self._typeEditor)
            self._stringRenderer = wx.grid.GridCellStringRenderer()
            self._stringEditor = wx.grid.GridCellTextEditor()
            self.grid.RegisterDataType(Attribute.STRING_TYPE, self._stringRenderer, self._stringEditor)
            self._intRenderer = wx.grid.GridCellNumberRenderer()
            self._intEditor = wx.grid.GridCellNumberEditor()
            self.grid.RegisterDataType(Attribute.INTEGER_TYPE, self._intRenderer, self._intEditor)
            self._floatRenderer = wx.grid.GridCellFloatRenderer(width = 1, precision = 1)
            self._floatEditor = wx.grid.GridCellFloatEditor()
            self.grid.RegisterDataType(Attribute.DECIMAL_TYPE, self._floatRenderer, self._floatEditor)
            self._boolRenderer = wx.grid.GridCellBoolRenderer()
            self._boolEditor = wx.grid.GridCellBoolEditor()
            self.grid.RegisterDataType(Attribute.BOOLEAN_TYPE, self._boolRenderer, self._boolEditor)
            self._dateTimeRenderer = wx.grid.GridCellDateTimeRenderer()
#            self._dateTimeEditor = wx.grid.GridCellDateTimeEditor()
            self.grid.RegisterDataType(Attribute.DATETIME_TYPE, self._dateTimeRenderer, self._stringEditor)
            self.grid.RegisterDataType(Attribute.DATE_TYPE, self._dateTimeRenderer, self._stringEditor)
            self.grid.RegisterDataType(Attribute.TIME_TYPE, self._dateTimeRenderer, self._stringEditor)
            
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
            attributedObject = display.network
            self.label.SetLabel(gettext('Attributes of the network:'))
        else:
            attributedObject = display.selection()[0].client
            if attributedObject.name is None:
                self.label.SetLabel(gettext('Attributes of unnamed %s:') % (attributedObject.__class__.displayName().lower()))
            else:
                self.label.SetLabel(gettext('Attributes of %s %s:') % (attributedObject.__class__.displayName().lower(), attributedObject.name))
        
        self.attributesTable.setObject(attributedObject)
        self.grid.SetGridCursor(self.grid.GetNumberCols() + 1, self.grid.GetNumberRows() + 1)
        self.grid.AutoSizeColumns()
        self.onResizeLastColumn(None)
        self.attributesTable.ResetView()
        
        dispatcher.connect(self.attributesDidChange, ('set', 'attributes'), attributedObject)
        
        self._window.Layout()
    
    
    def attributesDidChange(self):
        self.attributesTable.Reload()
    
    
    def onCellSelected(self, event):
        self.grid.SelectRow(event.Row)
        wx.CallAfter(self.enableCellEditControl)
        event.Skip()
    
    
    def enableCellEditControl(self):
        if self.grid.CanEnableCellControl():
            self.grid.EnableCellEditControl()
    
    
    def onAddAttribute(self, event):
        self.grid.AppendRows(1)
        rowNum = self.grid.GetNumberRows() - 1
        self.grid.SelectRow(rowNum)
        self.grid.SetGridCursor(rowNum, 1)
        event.Skip()
    
    
    def onRemoveAttribute(self, event):
        if self.grid.IsCellEditControlEnabled():
            self.grid.DisableCellEditControl()
        rowNums = set()
        for rowNum in self.grid.GetSelectedRows():
            rowNums.add(rowNum)
        blockTopLefts = self.grid.GetSelectionBlockTopLeft()
        blockBottomRights = self.grid.GetSelectionBlockBottomRight()
        for blockNum in range(len(blockTopLefts)):
            startRow = blockTopLefts[blockNum][0]
            endRow = blockBottomRights[blockNum][0]
            for rowNum in range(startRow, endRow + 1):
                rowNums.add(rowNum)
        rowNums = list(rowNums)
        rowNums.sort()
        rowNums.reverse()
        for rowNum in rowNums:
            self.grid.DeleteRows(rowNum, 1)
        event.Skip()
    
    
    def onResizeLastColumn(self, event):
        # We're showing the vertical scrollbar -> allow for scrollbar width
        # NOTE: on GTK, the scrollbar is included in the client size, but on
        # Windows it is not included
        gridWidth = self.grid.GetClientSize().width
#        if wx.Platform != '__WXMSW__':
#            if self.GetItemCount() > self.GetCountPerPage():
#                scrollWidth = wx.SystemSettings_GetMetric(wx.SYS_VSCROLL_X)
#                gridWidth = gridWidth - scrollWidth

        totColWidth = self.grid.GetColSize(0) + self.grid.GetColSize(1)
        resizeColWidth = self.grid.GetColSize(2)

        if gridWidth - totColWidth > 100:
            self.grid.SetColSize(2, gridWidth - totColWidth)
        
        if event is not None:
            event.Skip()
        
    
    def willBeClosed(self):
        # Make sure any active edit gets committed.
        if self.grid.IsCellEditControlEnabled():
            self.grid.DisableCellEditControl()
        self.label.SetLabel(gettext('Attributes:'))
        object = self.attributesTable.object
        if object:
            dispatcher.disconnect(self.attributesDidChange, ('set', 'attributes'), object)
        self.attributesTable.setObject(None)
