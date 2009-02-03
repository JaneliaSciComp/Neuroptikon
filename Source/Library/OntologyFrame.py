import wx
import cPickle
import Library

class OntologyFrame( wx.Frame ):
    
    def __init__(self, ontology):
        
        wx.Frame.__init__(self, None, -1, gettext('Ontology: %s') % (ontology.name or ontology.identifier), size=(300, 400), style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_TOOL_WINDOW)
        self.Bind(wx.EVT_CLOSE, self.Close)
        
        self.ontology = ontology
        
        self.treeCtrl = wx.TreeCtrl(self, wx.ID_ANY)
        for rootTerm in self.ontology.rootTerms:
            rootItem = self.treeCtrl.AddRoot(rootTerm.name)
            self.treeCtrl.SetPyData(rootItem, rootTerm)
            if rootTerm.obsolete:
                self.treeCtrl.SetItemTextColour(rootItem, wx.NamedColor('GRAY'))
            if len(rootTerm.parts) > 0:
                self.treeCtrl.SetItemHasChildren(rootItem, True)
        self.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.onItemExpanding, self.treeCtrl)
        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.onBeginDrag, self.treeCtrl)
        
        # TODO: display attributes of the selected term
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.treeCtrl, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)
    
    
    def onItemExpanding(self, event):
        item = event.GetItem()
        if item is not None:
            term = self.treeCtrl.GetPyData(item)
            if len(term.parts) > 0 and self.treeCtrl.GetChildrenCount(item) == 0:
                for childTerm in term.parts:
                    childItem = self.treeCtrl.AppendItem(item, childTerm.name)
                    self.treeCtrl.SetPyData(childItem, childTerm)
                    if childTerm.obsolete:
                        self.treeCtrl.SetItemTextColour(childItem, wx.NamedColor('GRAY'))
                    if len(childTerm.parts) > 0:
                        self.treeCtrl.SetItemHasChildren(childItem, True)
    
    
    def onBeginDrag(self, event):
        item = event.GetItem()
        if item is not None:
            term = self.treeCtrl.GetPyData(item)
            
            termData = wx.CustomDataObject("Neuroptikon Ontology Term")
            termData.SetData(cPickle.dumps({'Ontology': term.ontology.identifier, 'Term': term.identifier}, 1))
            dragData = wx.DataObjectComposite()
            dragData.Add(termData)
            dragData.Add(wx.TextDataObject(term.name))

            # Create the drop source and begin the drag and drop opperation
            dropSource = wx.DropSource(self)
            dropSource.SetData(dragData)
            dropSource.DoDragDrop(wx.Drag_CopyOnly)
    
    
    def exposeTerm(self, term):
        termItem = None
        
        if term.partOf is None:
            termItem = self.treeCtrl.GetRootItem()
        else:
            parentItem = self.exposeTerm(term.partOf)
        
            self.treeCtrl.Expand(parentItem)
            
            (curItem, cookie) = self.treeCtrl.GetFirstChild(parentItem)
            while curItem.IsOk():
                itemTerm = self.treeCtrl.GetPyData(curItem)
                if itemTerm == term:
                    termItem = curItem
                    break
                else:
                    curItem = self.treeCtrl.GetNextSibling(curItem)
        
        return termItem
    
    
    def selectTerm(self, term = None):
        if term is None:
            self.treeCtrl.UnselectAll()
        else:
            termItem = self.exposeTerm(term)
            
            if termItem is not None:
                self.treeCtrl.SelectItem(termItem)
    
    
    def Close(self, event=None):
        self.Hide()
        return True
    
