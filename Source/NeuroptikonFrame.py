import wx
from wx.py import dispatcher
import os, platform, sys
import xml.etree.ElementTree as ElementTree
from xml.dom import minidom
import Display, Display.Display
from Network.Network import Network
from Search.Finder import Finder
import Layouts


class NeuroptikonFrame( wx.Frame ):
    def __init__(self, network = None, id = wx.ID_ANY):
        if network is None:
            title = Network().name()
        else:
            title = network.name()
        wx.Frame.__init__(self, None, id, title, size=(800,600), style=wx.DEFAULT_FRAME_STYLE|wx.FULL_REPAINT_ON_RESIZE)
        
        self.Bind(wx.EVT_ACTIVATE, self.onActivate)
        self.Bind(wx.EVT_CLOSE, self.onCloseWindow)
        
        self.splitter = wx.SplitterWindow(self, wx.ID_ANY, style = wx.SP_LIVE_UPDATE)
        
        self.display = Display.Display.Display(self.splitter)
        self.display.setNetwork(network)
        dispatcher.connect(self.networkDidChangeSavePath, ('set', 'savePath'), network)
        
        self._console = wx.py.shell.Shell(self.splitter, wx.ID_ANY, locals = self.scriptLocals(), introText=gettext('Welcome to Neuroptikon.'))
        
        self.splitter.SplitHorizontally(self.display, self._console)
        self.splitter.SetSashGravity(1.0)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.splitter, 1, wx.EXPAND)
        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        
        self.SetMenuBar(self.menuBar())
        self.displayChangedMenuState()
        dispatcher.connect(self.displayChangedMenuState, ('set', 'useMouseOverSelecting'), self.display)
        dispatcher.connect(self.displayChangedMenuState, ('set', 'showRegionNames'), self.display)
        dispatcher.connect(self.displayChangedMenuState, ('set', 'showNeuronNames'), self.display)
        dispatcher.connect(self.displayChangedMenuState, ('set', 'useGhosts'), self.display)
        
        self.finder = None
        
        toolbar = wx.ToolBar(self)
        self._view2DId = wx.NewId()
        toolbar.AddCheckLabelTool(self._view2DId, gettext('2D View'), self.loadBitmap("View2D.png"))
        self.Bind(wx.EVT_TOOL, self.display.onViewIn2D, id=self._view2DId)
        self._view3DId = wx.NewId()
        toolbar.AddCheckLabelTool(self._view3DId, gettext('3D View'), self.loadBitmap("View3D.png"))
        self.Bind(wx.EVT_TOOL, self.display.onViewIn3D, id=self._view3DId)
        toolbar.Realize()
        self.SetToolBar(toolbar)
        
        dispatcher.connect(self.viewDimensionsDidChange, ('set', 'viewDimensions'), self.display)
        self.viewDimensionsDidChange()
        
        self.Show(1)
        self.splitter.SetSashPosition(-100)
    
    
    def networkDidChangeSavePath(self, signal = None, sender = None):
        self.SetTitle(self.display.network.name())
    
    
    @classmethod
    def fromXMLElement(cls, xmlElement, network = None):
        frame = NeuroptikonFrame()
        
        # TODO: set frame position and size
        
        # Populate the display (can't use the fromXMLElement pattern here because it doesn't seem possible to re-parent a wx.GLCanvas.
        displayElement = xmlElement.find('Display')
        if displayElement is None:
            raise ValueError, gettext('Display windows must contain a display')
        frame.display.autoVisualize = False
        frame.display.setNetwork(network)
        frame.display.fromXMLElement(displayElement)
        frame.networkDidChangeSavePath()
        
        return frame
    
    
    def toXMLElement(self, parentElement):
        frameElement = ElementTree.SubElement(parentElement, 'DisplayWindow')
        displayElement = self.display.toXMLElement(frameElement)
        if displayElement is None:
            raise ValueError, gettext('Could not save display')
        # TODO: save frame position and size
        return frameElement
    
    
    def toScriptFile(self, scriptFile, networkScriptRefs):
        scriptFile.write('\n' + gettext('# Create a display') + '\n\n')

        displayNum = self.display.network.displays.index(self.display)
        if displayNum == 0:
            displayRef = 'display'
        else:
            displayRef = 'display' + str(displayNum)
            scriptFile.write(displayRef + ' = displayNetwork(network)\n')
        
        self.display.toScriptFile(scriptFile, networkScriptRefs, displayRef)
    
    
    def loadBitmap(self, fileName):
        image = wx.GetApp().loadImage(fileName)
        if image is None or not image.IsOk():
            image = wx.EmptyImage(32, 32)
        if platform.system() == 'Windows':
            image.Rescale(16, 16, wx.IMAGE_QUALITY_HIGH)
        return image.ConvertToBitmap()
    
    
    def menuBar(self):
        menuBar = wx.MenuBar()
        
        fileMenu = wx.Menu()
        self.Bind(wx.EVT_MENU, wx.GetApp().onNewNetwork, fileMenu.Append(wx.NewId(), gettext('New Network\tCtrl-N'), gettext('Open a new network window')))
        self.Bind(wx.EVT_MENU, wx.GetApp().onOpenNetwork, fileMenu.Append(wx.NewId(), gettext('Open Network...\tCtrl-O'), gettext('Open a previously saved network')))
        self.Bind(wx.EVT_MENU, self.onCloseWindow, fileMenu.Append(wx.ID_CLOSE, gettext('Close Network\tCtrl-W'), gettext('Close the current network window')))
        self.Bind(wx.EVT_MENU, self.onSaveNetwork, fileMenu.Append(wx.NewId(), gettext('Save Network...\tCtrl-S'), gettext('Save the current network')))
        self.Bind(wx.EVT_MENU, self.onSaveNetworkAs, fileMenu.Append(wx.NewId(), gettext('Save As...\tCtrl-Shift-S'), gettext('Save to a new file')))
        fileMenu.AppendSeparator()
        self.Bind(wx.EVT_MENU, self.onRunScript, fileMenu.Append(wx.NewId(), gettext('Run Script...\tCtrl-R'), gettext('Run a console script file')))
        self.Bind(wx.EVT_MENU, wx.GetApp().onBrowseLibrary, fileMenu.Append(wx.NewId(), gettext('Browse the Library\tCtrl-Alt-L'), gettext('Open the Library window')))
        self.Bind(wx.EVT_MENU, wx.GetApp().onOpenConsole, fileMenu.Append(wx.NewId(), gettext('Open the Console\tCtrl-Alt-O'), gettext('Open the Console window')))
        self.Bind(wx.EVT_MENU, wx.GetApp().onOpenPreferences, fileMenu.Append(wx.ID_PREFERENCES, gettext('Settings'), gettext('Change Neuroptikon preferences')))
        fileMenu.AppendSeparator()
        self.Bind(wx.EVT_MENU, wx.GetApp().onQuit, fileMenu.Append(wx.ID_EXIT, gettext('E&xit\tCtrl-Q'), gettext('Exit this simple sample')))
        menuBar.Append(fileMenu, gettext('&File'))
        
        editMenu = wx.Menu()
        self.Bind(wx.EVT_MENU, self.onUndo, editMenu.Append(wx.NewId(), gettext('Undo\tCtrl-Z'), gettext('Undo the last action')))
        self.Bind(wx.EVT_MENU, self.onRedo, editMenu.Append(wx.NewId(), gettext('Redo\tCtrl-Shift-Z'), gettext('Redo the last action')))
        editMenu.AppendSeparator()
        self.cutMenuItem = editMenu.Append(wx.NewId(), gettext('Cut\tCtrl-X'), gettext('Move the selected objects to the clipboard'))
        self.Bind(wx.EVT_MENU, self.onCut, self.cutMenuItem)
        self.copyMenuItem = editMenu.Append(wx.NewId(), gettext('Copy\tCtrl-C'), gettext('Copy the selected objects to the clipboard'))
        self.Bind(wx.EVT_MENU, self.onCopy, self.copyMenuItem)
        self.pasteMenuItem = editMenu.Append(wx.NewId(), gettext('Paste\tCtrl-V'), gettext('Paste the contents of the clipboard'))
        self.Bind(wx.EVT_MENU, self.onPaste, self.pasteMenuItem)
        self.Bind(wx.EVT_MENU, self.onSelectAll, editMenu.Append(wx.NewId(), gettext('Select All\tCtrl-A'), gettext('Select all objects in the window')))
        editMenu.AppendSeparator()
        self.pasteMenuItem = editMenu.Append(wx.NewId(), gettext('Find\tCtrl-F'), gettext('Find objects in the network'))
        self.Bind(wx.EVT_MENU, self.onFind, self.pasteMenuItem)
        menuBar.Append(editMenu, gettext('&Edit'))
        
        viewMenu = wx.Menu()
        self.Bind(wx.EVT_MENU, wx.GetApp().onOpenInspector, viewMenu.Append(wx.NewId(), gettext('Open Inspector Window\tCtrl-I'), gettext('Open the inspector window')))
        self.mouseOverSelectingItem = viewMenu.Append(wx.NewId(), gettext('Use Mouse-Over Highlighting'), gettext('Automatically select the object under the mouse'), True)
        self.Bind(wx.EVT_MENU, self.OnUseMouseOverSelecting, self.mouseOverSelectingItem)
        viewMenu.AppendSeparator()
        self.showRegionNamesMenuItem = viewMenu.Append(wx.NewId(), gettext('Show Region Names'), gettext('Show/hide the region names'), True)
        self.Bind(wx.EVT_MENU, self.onShowHideRegionNames, self.showRegionNamesMenuItem)
        self.showNeuronNamesMenuItem = viewMenu.Append(wx.NewId(), gettext('Show Neuron Names'), gettext('Show/hide the neuron names'), True)
        self.Bind(wx.EVT_MENU, self.onShowHideNeuronNames, self.showNeuronNamesMenuItem)
        self.labelsFloatOnTopMenuItem = viewMenu.Append(wx.NewId(), gettext('Float Labels On Top'), gettext('Always show object labels even when the object is behind another'), True)
        self.Bind(wx.EVT_MENU, self.onSetLabelsFloatOnTop, self.labelsFloatOnTopMenuItem)
        self.showFlowMenuItem = viewMenu.Append(wx.NewId(), gettext('Show Flow of Information'), gettext('Animate the connections between objects'), True)
        self.Bind(wx.EVT_MENU, self.onShowFlow, self.showFlowMenuItem)
        self.useGhostsMenuItem = viewMenu.Append(wx.NewId(), gettext('Use Ghosting'), gettext('Dim objects that are not currently selected'), True)
        self.Bind(wx.EVT_MENU, self.onUseGhosts, self.useGhostsMenuItem)
        viewMenu.AppendSeparator()
        for layoutId, layoutClass in Display.layoutClasses().iteritems():
            menuItem = viewMenu.Append(layoutId, gettext('%s Layout') % layoutClass.name())
            self.Bind(wx.EVT_MENU, self.display.onLayout, menuItem)
            self.Bind(wx.EVT_UPDATE_UI, self.onUpdateLayoutUI, menuItem)
        self.Bind(wx.EVT_MENU, self.display.onLayout, viewMenu.Append(wx.NewId(), gettext('Repeat Last Layout\tCtrl-L')))
        viewMenu.AppendSeparator()
        self.Bind(wx.EVT_MENU, self.display.onCenterView, viewMenu.Append(wx.NewId(), gettext('Center View'), gettext('Center the display on all objects')))
        viewMenu.AppendSeparator()
        self.Bind(wx.EVT_MENU, self.display.onSaveView, viewMenu.Append(wx.NewId(), gettext('Save View as...'), gettext('Save the current view to a file')))
        menuBar.Append(viewMenu, gettext('&View'))
        
        helpMenu = wx.Menu()
        self.Bind(wx.EVT_MENU, wx.GetApp().onAboutNeuroptikon, helpMenu.Append(wx.ID_ABOUT, gettext('About Neuroptikon'), gettext('Information about this program')))
        menuBar.Append(helpMenu, gettext('&Help'))
                return menuBar
    
    
    def displayChangedMenuState(self, sender = None, signal = None):
        self.mouseOverSelectingItem.Check(self.display.useMouseOverSelecting())
        self.showRegionNamesMenuItem.Check(self.display.showRegionNames())
        self.showNeuronNamesMenuItem.Check(self.display.showNeuronNames())
        self.labelsFloatOnTopMenuItem.Check(self.display.labelsFloatOnTop())
        self.useGhostsMenuItem.Check(self.display.useGhosts())
    
    
    def viewDimensionsDidChange(self, sender = None, signal = None):
        self.GetToolBar().ToggleTool(self._view2DId, self.display.viewDimensions == 2)
        self.GetToolBar().ToggleTool(self._view3DId, self.display.viewDimensions == 3)
    
    
    def onActivate(self, event):
        wx.GetApp().inspector.inspectDisplay(self.display)
        event.Skip()
    
    
    def scriptLocals(self):
        locals = wx.GetApp().scriptLocals()
        locals['network'] = self.display.network
        locals['display'] = self.display
        return locals
    
        
    def onRunScript(self, event):
        # TODO: It would be nice to provide progress for long running scripts.  Would need some kind of callback for scripts to indicate how far along they were.
        dlg = wx.FileDialog(None, 'Choose a script to run', './Scripts', '', '*.py', wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            locals = self.scriptLocals()
            locals['__file__'] = dlg.GetPath()
            try:
                execfile(dlg.GetPath(), locals)
            except:
                (exceptionType, exceptionValue, exceptionTraceback) = sys.exc_info()
                dialog = wx.MessageDialog(self, exceptionValue.message, gettext('An error occurred at line %d of the script:') % exceptionTraceback.tb_next.tb_lineno, style = wx.ICON_ERROR | wx.OK)
                dialog.ShowModal()
        dlg.Destroy()
        self.Refresh(False)
        self.Show(True)
    
    
    def onUndo(self, event):
        pass    # TODO
    
    
    def onRedo(self, event):
        pass    # TODO
    
    
    def onCut(self, event):
        pass    # TODO
    
    
    def onCopy(self, event):
        pass    # TODO
    
    
    def onPaste(self, event):
        pass    # TODO
    
    
    def onSelectAll(self, event):
        self.display.selectAll()
    
    
    def onFind(self, event):
        if self.finder is None:
            self.finder = Finder(self, -1, gettext('Finder'), pos=(-1,-1))
        
        if self.finder.ShowModal() == wx.ID_OK:
            self.display.selectObjectsMatching(self.finder.predicate)
    
    
    def OnUseMouseOverSelecting(self, event):
        self.display.setUseMouseOverSelecting(not self.display.useMouseOverSelecting())
    
    
    def onShowHideRegionNames(self, event):
        self.display.setShowRegionNames(not self.display.showRegionNames())
    
    
    def onShowHideNeuronNames(self, event):
        self.display.setShowNeuronNames(not self.display.showNeuronNames())
    
    
    def onSetLabelsFloatOnTop(self, event):
        self.display.setLabelsFloatOnTop(not self.display.labelsFloatOnTop())
    
    
    def onShowFlow(self, event):
        self.display.setShowFlow(not self.display.showFlow())
    
    
    def onUseGhosts(self, event):
        self.display.setUseGhosts(not self.display.useGhosts())
    
    
    def onUpdateLayoutUI(self, event):
        menuItem = self.GetMenuBar().FindItemById(event.GetId())
        layoutClass = Display.layoutClasses()[event.GetId()]
        menuItem.Enable(layoutClass.canLayoutDisplay(self.display))
    
    
    def onCloseWindow(self, event):
        self.Destroy()
        wx.GetApp().displayWasClosed(self)
    
    
    def indentXMLElement(self, element, level=0):
        i = "\n" + level*"\t"
        if len(element):
            if not element.text or not element.text.strip():
                element.text = i + "\t"
            if not element.tail or not element.tail.strip():
                element.tail = i
            for element in element:
                self.indentXMLElement(element, level+1)
            if not element.tail or not element.tail.strip():
                element.tail = i
        else:
            if level and (not element.tail or not element.tail.strip()):
                element.tail = i
    
    
    def saveNetworkAndDisplaysAsXML(self, savePath, saveDisplays = True):
        try:
            xmlRoot = ElementTree.Element('Neuroptikon')
            network = self.display.network
            
            # Serialize the network
            networkElement = network.toXMLElement(xmlRoot)
            if networkElement is None:
                raise ValueError, gettext('Could not save the network')
            
            if saveDisplays:
                # Serialize the display(s)
                for display in network.displays:
                    frameElement = display.GetTopLevelParent().toXMLElement(xmlRoot)
                    if frameElement is None:
                        raise ValueError, gettext('Could not save one of the windows')
            
            self.indentXMLElement(xmlRoot)
            xmlTree = ElementTree.ElementTree(xmlRoot)
            xmlTree.write(savePath)
            
            # To test the contents of the output use:
            # xmllint --noout --schema Source/Neuroptikon_v1.0.xsd Test.xml
        except:
            raise    # TODO: inform the user nicely
    
    
    def saveNetworkAndDisplaysAsScript(self, savePath, saveNetwork = True, saveDisplays = True):
        scriptRefs = {}
        network = self.display.network
        
        if saveDisplays:
            if len(network.displays) == 1:
                scriptRefs[self.display] = 'display'
            else:
                for display in network.displays:
                    scriptRefs[display] = 'display' + str(network.displays.index(display))
        
        if not saveNetwork:
            # Attempt to create script refs for all objects using the network.find* methods.
            objectNames = {}
            for object in network.objects:
                if object.includeInScript():
                    objectName = object.name
                    defaultName = object.defaultName()
                    
                    # Make sure the object has a name.
                    if not objectName and not defaultName:
                        for display in network.displays:
                            display.selectObject(object)
                        raise ValueError, gettext('The display of the selected object cannot be saved because it does not have a name.')
                    
                    # Make sure the name is unique.
                    if objectName:
                        nameKey = object.__class__.__name__ + ': ' + objectName
                        if nameKey in objectNames:
                            for display in network.displays:
                                display.selectObjects([object, objectNames[nameKey]])
                            raise ValueError, gettext('The display cannot be saved because there is more than one %s with the name \'%s\'.') % (object.__class__.__name__.lower(), objectName)
                    else:
                        nameKey = object.__class__.__name__ + ': ' + defaultName
                        if nameKey in objectNames:
                            for display in network.displays:
                                display.selectObjects([object, objectNames[nameKey]])
                            raise ValueError, gettext('The display cannot be saved because there is more than one %s with the default name \'%s\'.') % (object.__class__.__name__.lower(), defaultName)
                    
                    # Create the script ref.
                    objectNames[nameKey] = object
                    if 'find' + object.__class__.__name__ in dir(network):
                        prefix = 'network.find' + object.__class__.__name__ + '(\''
                    else:
                        prefix = 'network.findObject(' + object.__class__.__name__ + ', \''
                    if objectName:
                        scriptRefs[object.networkId] = prefix + objectName + '\')'
                    else:
                        scriptRefs[object.networkId] = prefix + defaultName + '\', default = True)'
        
        scriptFile = open(savePath, 'w')
        scriptFile.write('from datetime import datetime, date, time\n\n')
        
        try:
            # Serialize the network
            if saveNetwork:
                if saveDisplays:
                    for display in network.displays:
                        if not display.autoVisualize:
                            scriptFile.write(scriptRefs[display] + '.autoVisualize = False\n')
                    scriptFile.write('\n')
                network.toScriptFile(scriptFile, scriptRefs)
            
            if saveDisplays:
                # Serialize the display(s)
                for display in network.displays:
                    display.GetTopLevelParent().toScriptFile(scriptFile, scriptRefs)
            else:
                scriptFile.write('\n# Reveal the default visualization\ndisplay.centerView()\n')
        except:
            raise    # TODO: inform the user nicely
        finally:
            scriptFile.close()
    
    
    def onSaveNetwork(self, event):
        network = self.display.network
        if network.savePath() is None:
            dlg = wx.FileDialog(None, gettext('Save as:'), '', '', '*.xml', wx.SAVE)
            if dlg.ShowModal() == wx.ID_OK:
                network.setSavePath(dlg.GetPath())
        
        if network.savePath() is not None:
            self.saveNetworkAndDisplaysAsXML(network.savePath())
    
    
    def onSaveNetworkAs(self, event):
        fileTypes = ['XML File', 'XML File (network only)', 'Python Script', 'Python Script (network only)', 'Python Script (display only)']
        fileExtensions = ['xml', 'xml', 'py', 'py', 'py']
        wildcard = ''
        for index in range(0, len(fileTypes)):
            if wildcard != '':
                wildcard += '|'
            wildcard += fileTypes[index] + '|' + fileExtensions[index]
        fileDialog = wx.FileDialog(None, gettext('Save As:'), '', '', wildcard, wx.FD_SAVE)
        if fileDialog.ShowModal() == wx.ID_OK:
            filterIndex = fileDialog.GetFilterIndex()
            saveNetwork = (filterIndex != 4)
            saveDisplays = (filterIndex in [0, 2, 4])
            extension = fileExtensions[filterIndex]
            savePath = str(fileDialog.GetPath())
            if not savePath.endswith('.' + extension):
                savePath += '.' + extension
            try:
                if extension == 'xml':
                    self.display.network.setSavePath(savePath)
                    self.saveNetworkAndDisplaysAsXML(savePath, saveDisplays)
                else:
                    self.saveNetworkAndDisplaysAsScript(savePath, saveNetwork, saveDisplays)
            except:
                (exceptionType, exceptionValue, exceptionTraceback) = sys.exc_info()
                dialog = wx.MessageDialog(self, exceptionValue.message, gettext('The file could not be saved.'), style = wx.ICON_ERROR | wx.OK)
                dialog.ShowModal()
    
