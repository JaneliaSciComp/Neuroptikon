import wx, wx.grid
import os, sys, weakref
from Network.Attribute import Attribute


class GridCellAttributeTypeRenderer(wx.grid.PyGridCellRenderer):
    
    def __init__(self, grid):
        self.gridRef = weakref.ref(grid)
        
        self.icons = {}
        iconDir = os.path.dirname(sys.modules['Inspectors.Attributes.AttributesInspector'].__file__)
        for iconName in Attribute.TYPES:
            try:
                image = wx.Image(iconDir + os.sep + iconName + '.png')
            except:
                image = None
            if image is not None and image.IsOk():
                image.Rescale(16, 16)
                self.icons[iconName] = image.ConvertToBitmap()
            else:
                self.icons[iconName] = wx.EmptyBitmap(16, 16)
            
        wx.grid.PyGridCellRenderer.__init__(self)
    
    
    def Draw(self, grid, attr, drawingContext, rect, row, col, isSelected):        drawingContext.SetClippingRegion( rect.x, rect.y, rect.width, rect.height )
        
        # Draw the background        if isSelected:            drawingContext.SetBrush(wx.Brush(wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHT), wx.SOLID))        else:            drawingContext.SetBrush(wx.Brush(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW), wx.SOLID))        try:            drawingContext.SetPen(wx.TRANSPARENT_PEN)            drawingContext.DrawRectangle(rect.x, rect.y, rect.width, rect.height)        finally:            drawingContext.SetPen(wx.NullPen)            drawingContext.SetBrush(wx.NullBrush)
        
        # Draw the appropriate icon        try:            value = grid.GetCellValue(row, col)            if value in self.icons:
                icon = self.icons[value]
                drawingContext.DrawBitmap(icon, rect.x + rect.width / 2 - 8, rect.y + rect.height / 2 - 8, True)        finally:            drawingContext.DestroyClippingRegion()
    
        def GetBestSize(self, grid, attr, drawingContext, row, col):        return wx.Size(16, 16)
    

    def Clone(self):
        return GridCellChoiceEditor(self.gridRef())

