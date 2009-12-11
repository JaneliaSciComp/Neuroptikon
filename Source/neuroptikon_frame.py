import neuroptikon
import wx, wx.py
from pydispatch import dispatcher
import datetime, os, platform, sys, traceback
import xml.etree.ElementTree as ElementTree
import display, display.display
from network.network import Network
from search.finder import Finder

if platform.system() == 'Darwin':
    import ctypes
    carbon = ctypes.CDLL('/System/Library/Carbon.framework/Carbon')


class NeuroptikonFrame( wx.Frame ):
    def __init__(self, network = None, wxId = wx.ID_ANY):
        if network is None:
            title = Network().name()
        else:
            title = network.name()
        wx.Frame.__init__(self, None, wxId, title, size=(800,600), style=wx.DEFAULT_FRAME_STYLE|wx.FULL_REPAINT_ON_RESIZE)
        
        self.Bind(wx.EVT_ACTIVATE, self.onActivate)
        self.Bind(wx.EVT_UPDATE_UI, self.onUpdateUI)
        self.Bind(wx.EVT_CLOSE, self.onCloseWindow)
        
        self.splitter = wx.SplitterWindow(self, wx.ID_ANY, style = wx.SP_LIVE_UPDATE)
        self.splitter.SetMinimumPaneSize(20)
        
        self._modified = False
        
        self.display = display.display.Display(self.splitter)
        self.display.setNetwork(network)
        dispatcher.connect(self.networkDidChange, ('set', 'network'), self.display)
        dispatcher.connect(self.networkDidChangeSavePath, ('set', 'savePath'), network)
        dispatcher.connect(self.displayDidChange, dispatcher.Any, self.display)
        
        self._scriptLocals = self.scriptLocals()
        self._console = wx.py.shell.Shell(self.splitter, wx.ID_ANY, locals = self._scriptLocals, introText=gettext('Welcome to Neuroptikon.'))
        self._console.autoCompleteIncludeSingle = False
        self._console.autoCompleteIncludeDouble = False
        
        self.splitter.SplitHorizontally(self.display, self._console)
        self.splitter.SetSashGravity(1.0)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.splitter, 1, wx.EXPAND)
        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        
        self.finder = None
        
        self.layoutClasses = {}
        
        self.SetMenuBar(self.menuBar())
        self.SetToolBar(self.toolBar())
        
        dispatcher.connect(self.onDisplayChangedHighlightOnlyWithinSelection, ('set', 'highlightOnlyWithinSelection'), self.display)
        
        if platform.system() == 'Darwin':
            # Have new windows cascade so they don't sit right on top of each other.
            carbon.RepositionWindow(self.MacGetTopLevelWindowRef(), 0, 4)   # 4 = kWindowCascadeOnMainScreen
        
        self.Show(1)
        self.splitter.SetSashPosition(-100)
    
    
    def networkDidChange(self):
        self._scriptLocals['network'] = self.display.network
    
    
    def networkDidChangeSavePath(self):
        self.SetTitle(self.display.network.name())
    
    
    def displayDidChange(self, signal = None):
        if isinstance(signal, tuple) and signal[0] == 'set':
            self.setModified(True)
    
    
    @classmethod
    def _fromXMLElement(cls, xmlElement, network = None):
        frame = NeuroptikonFrame()
        
        # TODO: set frame position and size
        
        # Populate the display (can't use the _fromXMLElement pattern here because it doesn't seem possible to re-parent a wx.GLCanvas.
        displayElement = xmlElement.find('Display')
        if displayElement is None:
            raise ValueError, gettext('Display windows must contain a display')
        frame.display.autoVisualize = False
        frame.display.setNetwork(network)
        if network:
            dispatcher.connect(frame.networkDidChangeSavePath, ('set', 'savePath'), network)
        frame.display._fromXMLElement(displayElement)
        frame.networkDidChangeSavePath()
        frame.setModified(False)
        wx.GetApp().inspector.inspectDisplay(frame.display)
        
        return frame
    
    
    def _toXMLElement(self, parentElement):
        frameElement = ElementTree.SubElement(parentElement, 'DisplayWindow')
        displayElement = self.display._toXMLElement(frameElement)
        if displayElement is None:
            raise ValueError, gettext('Could not save display')
        # TODO: save frame position and size
        return frameElement
    
    
    def _toScriptFile(self, scriptFile, networkScriptRefs):
        scriptFile.write('\n' + gettext('# Create a display') + '\n\n')

        displayNum = self.display.network.displays.index(self.display)
        if displayNum == 0:
            displayRef = 'display'
        else:
            displayRef = 'display' + str(displayNum)
            scriptFile.write(displayRef + ' = displayNetwork(network)\n')
        
        self.display._toScriptFile(scriptFile, networkScriptRefs, displayRef)
    
    
    def loadBitmap(self, fileName):
        image = neuroptikon.loadImage(fileName)
        if image is None or not image.IsOk():
            image = wx.EmptyImage(32, 32)
        if platform.system() == 'Windows':
            image.Rescale(16, 16, wx.IMAGE_QUALITY_HIGH)
        return image.ConvertToBitmap()
    
    
    def menuBar(self):
        menuBar = wx.GetApp().menuBar(self)
        
        # pylint: disable-msg=W0201
        
        editMenu = wx.Menu()
        self.Bind(wx.EVT_MENU, self.onUndo, editMenu.Append(wx.ID_UNDO, gettext('Undo\tCtrl-Z'), gettext('Undo the last action')))
        self.Bind(wx.EVT_MENU, self.onRedo, editMenu.Append(wx.ID_REDO, gettext('Redo\tCtrl-Shift-Z'), gettext('Redo the last action')))
        editMenu.AppendSeparator()
        self.cutMenuItem = editMenu.Append(wx.ID_CUT, gettext('Cut\tCtrl-X'), gettext('Move the selected objects to the clipboard'))
        self.Bind(wx.EVT_MENU, self.onCut, self.cutMenuItem)
        self.copyMenuItem = editMenu.Append(wx.ID_COPY, gettext('Copy\tCtrl-C'), gettext('Copy the selected objects to the clipboard'))
        self.Bind(wx.EVT_MENU, self.onCopy, self.copyMenuItem)
        self.pasteMenuItem = editMenu.Append(wx.ID_PASTE, gettext('Paste\tCtrl-V'), gettext('Paste the contents of the clipboard'))
        self.Bind(wx.EVT_MENU, self.onPaste, self.pasteMenuItem)
        self.Bind(wx.EVT_MENU, self.onSelectAll, editMenu.Append(wx.ID_SELECTALL, gettext('Select All\tCtrl-A'), gettext('Select all objects in the window')))
        editMenu.AppendSeparator()
        self.pasteMenuItem = editMenu.Append(wx.ID_FIND, gettext('Find\tCtrl-F'), gettext('Find objects in the network'))
        self.Bind(wx.EVT_MENU, self.onFind, self.pasteMenuItem)
        menuBar.Insert(menuBar.GetMenuCount() - 1, editMenu, gettext('&Edit'))
        
        viewMenu = wx.Menu()
        self.Bind(wx.EVT_MENU, wx.GetApp().onOpenInspector, viewMenu.Append(wx.NewId(), gettext('Open Inspector Window\tCtrl-I'), gettext('Open the inspector window')))
        self.mouseOverSelectingItem = viewMenu.Append(wx.NewId(), gettext('Use Mouse-Over Highlighting'), gettext('Automatically select the object under the mouse'), True)
        self.Bind(wx.EVT_MENU, self.OnUseMouseOverSelecting, self.mouseOverSelectingItem)
        self.highlightOnlyWithinSelectionItem = viewMenu.Append(wx.NewId(), gettext('Highlight Only Within Selection'), gettext('Only highlight connections to other selected objects'), True)
        self.Bind(wx.EVT_MENU, self.onHighlightOnlyWithinSelection, self.highlightOnlyWithinSelectionItem)
        viewMenu.AppendSeparator()  # -----------------
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
        viewMenu.AppendSeparator()  # -----------------
        for layoutClass in display.layout.layoutClasses():
            layoutId = wx.NewId()
            self.layoutClasses[layoutId] = layoutClass
            menuItem = viewMenu.Append(layoutId, gettext('%s Layout') % layoutClass.name())
            self.Bind(wx.EVT_MENU, self.display.onLayout, menuItem)
            self.Bind(wx.EVT_UPDATE_UI, self.onUpdateLayoutUI, menuItem)
        self.Bind(wx.EVT_MENU, self.display.onLayout, viewMenu.Append(wx.NewId(), gettext('Repeat Last Layout\tCtrl-L')))
        viewMenu.AppendSeparator()  # -----------------
        self.viewIn2DMenuItem = viewMenu.Append(wx.NewId(), gettext('View in 2D\tCtrl-2'), gettext('Show the objects in the xy, xz or zy plane'), True)
        self.Bind(wx.EVT_MENU, self.display.onViewIn2D, self.viewIn2DMenuItem)
        self.viewIn3DMenuItem = viewMenu.Append(wx.NewId(), gettext('View in 3D\tCtrl-3'), gettext('Show the objects in the three dimensional space'), True)
        self.Bind(wx.EVT_MENU, self.display.onViewIn3D, self.viewIn3DMenuItem)
        viewMenu.AppendSeparator()  # -----------------
        self.resetViewMenuItem = viewMenu.Append(wx.NewId(), gettext('Reset View'), gettext('Return to the default view'))
        self.Bind(wx.EVT_MENU, self.onResetView, self.resetViewMenuItem)
        self.zoomToFitMenuItem = viewMenu.Append(wx.ID_ZOOM_FIT, gettext('Zoom to Fit\tCtrl-0'), gettext('Fit all objects within the display'))
        self.Bind(wx.EVT_MENU, self.onZoomToFit, self.zoomToFitMenuItem)
        self.zoomToSelectionMenuItem = viewMenu.Append(wx.NewId(), gettext('Zoom to Selection\tCtrl-\\'), gettext('Fit all selected objects within the display'))
        self.Bind(wx.EVT_MENU, self.onZoomToSelection, self.zoomToSelectionMenuItem)
        self.zoomInMenuItem = viewMenu.Append(wx.ID_ZOOM_IN, gettext('Zoom In\tCtrl-+'), gettext('Make objects appear larger'))
        self.Bind(wx.EVT_MENU, self.onZoomIn, self.zoomInMenuItem)
        self.zoomOutMenuItem = viewMenu.Append(wx.ID_ZOOM_OUT, gettext('Zoom Out\tCtrl--'), gettext('Make objects appear smaller'))
        self.Bind(wx.EVT_MENU, self.onZoomOut, self.zoomOutMenuItem)
        viewMenu.AppendSeparator()  # -----------------
        self.Bind(wx.EVT_MENU, self.display.onSaveView, viewMenu.Append(wx.NewId(), gettext('Save View as...'), gettext('Save the current view to a file')))
        menuBar.Insert(menuBar.GetMenuCount() - 1, viewMenu, gettext('&View'))
        
        # pylint: enable-msg=W0201
        
        return menuBar
    
    
    def toolBar(self):
        toolBar = wx.ToolBar(self)
        toolBar.AddCheckLabelTool(self.viewIn2DMenuItem.GetId(), gettext('2D View'), self.loadBitmap("View2D.png"))
        self.Bind(wx.EVT_TOOL, self.display.onViewIn2D, id = self.viewIn2DMenuItem.GetId())
        toolBar.AddCheckLabelTool(self.viewIn3DMenuItem.GetId(), gettext('3D View'), self.loadBitmap("View3D.png"))
        self.Bind(wx.EVT_TOOL, self.display.onViewIn3D, id = self.viewIn3DMenuItem.GetId())
        toolBar.AddSeparator()
        toolBar.AddLabelTool(self.zoomToFitMenuItem.GetId(), gettext('Zoom To Fit'), self.loadBitmap("ZoomToFit.png"))
        toolBar.AddLabelTool(self.zoomToSelectionMenuItem.GetId(), gettext('Zoom To Selection'), self.loadBitmap("ZoomToSelection.png"))
        toolBar.AddLabelTool(self.zoomInMenuItem.GetId(), gettext('Zoom In'), self.loadBitmap("ZoomIn.png"))
        toolBar.AddLabelTool(self.zoomOutMenuItem.GetId(), gettext('Zoom Out'), self.loadBitmap("ZoomOut.png"))
        toolBar.AddSeparator()
        toolBar.AddCheckLabelTool(self.highlightOnlyWithinSelectionItem.GetId(), gettext('Highlight Only Within Selection'), self.loadBitmap("HighlightOnlyWithinSelectionOff.png"), shortHelp = gettext('Only highlight connections to other selected objects'))
        toolBar.Realize()
        return toolBar
    
    
    def onUpdateUI(self, event):
        focusedWindow = self.FindFocus()
        eventId = event.GetId() 
        if eventId == wx.ID_UNDO: 
            event.Enable(focusedWindow == self._console and self._console.CanUndo())
        elif eventId == wx.ID_REDO: 
            event.Enable(focusedWindow == self._console and self._console.CanRedo())
        elif eventId == wx.ID_CUT: 
            event.Enable(focusedWindow == self._console and self._console.CanCut())
        elif eventId == wx.ID_COPY: 
            event.Enable(focusedWindow == self._console and self._console.CanCopy())
        elif eventId == wx.ID_PASTE: 
            event.Enable(focusedWindow == self._console and self._console.CanPaste())
        elif eventId == self.mouseOverSelectingItem.GetId():
            event.Check(self.display.useMouseOverSelecting())
        elif eventId == self.highlightOnlyWithinSelectionItem.GetId():
            event.Check(self.display.highlightOnlyWithinSelection())
        elif eventId == self.showRegionNamesMenuItem.GetId():
            event.Check(self.display.showRegionNames())
        elif eventId == self.showNeuronNamesMenuItem.GetId():
            event.Check(self.display.showNeuronNames())
        elif eventId == self.labelsFloatOnTopMenuItem.GetId():
            event.Check(self.display.labelsFloatOnTop())
        elif eventId == self.useGhostsMenuItem.GetId():
            event.Check(self.display.useGhosts())
        elif eventId == self.viewIn2DMenuItem.GetId():
            event.Check(self.display.viewDimensions == 2)
        elif eventId == self.viewIn3DMenuItem.GetId():
            event.Check(self.display.viewDimensions == 3)
        elif eventId == self.resetViewMenuItem.GetId():
            event.Enable(self.display.viewDimensions == 3)
        elif eventId == self.zoomToFitMenuItem.GetId():
            event.Enable(self.display.viewDimensions == 2)
        elif eventId == self.zoomToSelectionMenuItem.GetId():
            event.Enable(self.display.viewDimensions == 2 and any(self.display.selection()))
        elif eventId == self.zoomOutMenuItem.GetId():
            event.Enable(self.display.viewDimensions == 3 or self.display.orthoZoom > 0)
    
    
    def onDisplayChangedHighlightOnlyWithinSelection(self):
        if self.display.highlightOnlyWithinSelection():
            bitmap = self.loadBitmap("HighlightOnlyWithinSelectionOn.png")
        else:
            bitmap = self.loadBitmap("HighlightOnlyWithinSelectionOff.png")
        self.GetToolBar().SetToolNormalBitmap(self.highlightOnlyWithinSelectionItem.GetId(), bitmap)
        
    
    def onActivate(self, event):
        wx.GetApp().inspector.inspectDisplay(self.display)
        event.Skip()
    
    
    def scriptLocals(self):
        scriptLocals = neuroptikon.scriptLocals()
        scriptLocals['network'] = self.display.network
        scriptLocals['display'] = self.display
        if 'DEBUG' in os.environ:
            scriptLocals['profileScript'] = self._profileScript
        return scriptLocals
    
        
    def runScript(self, scriptPath):
        # TODO: It would be nice to provide progress for long running scripts.  Would need some kind of callback for scripts to indicate how far along they were.
        if 'DEBUG' in os.environ:
            startTime = datetime.datetime.now()
        prevDir = os.getcwd()
        os.chdir(os.path.dirname(scriptPath))
        if 'DEBUG' in os.environ:
            self._console.redirectStdin(True)
            self._console.redirectStdout(True)
            self._console.redirectStderr(True)
        scriptLocals = self.scriptLocals()
        scriptLocals['__file__'] = scriptPath   # Let the script know where it is being run from.
        try:
            execfile(os.path.basename(scriptPath), scriptLocals)
            self.Refresh(False)
        finally:
            os.chdir(prevDir)
            if 'DEBUG' in os.environ:
                self._console.redirectStdin(False)
                self._console.redirectStdout(False)
                self._console.redirectStderr(False)
        if 'DEBUG' in os.environ:
            runTime = datetime.datetime.now() - startTime
            self._console.writeOut('# Ran ' + os.path.basename(scriptPath) + ' in ' + str(round(runTime.seconds + runTime.microseconds / 1000000.0, 2)) + ' seconds.\n')
    
        
    def _profileScript(self, scriptPath):
        import cProfile, pstats
        profilePath = scriptPath + '.profile'
        print 'Saving profile to ' + profilePath + ' ...'
        cProfile.runctx('self.runScript(' + repr(scriptPath) + ')', {}, {'self': self}, filename = profilePath)
        p = pstats.Stats(profilePath)
        p.strip_dirs().sort_stats('time').print_stats(30)
    
        
    def onRunScript(self, event_):
        dlg = wx.FileDialog(None, 'Choose a script to run', './Scripts', '', '*.py', wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            try:
                self.runScript(dlg.GetPath())
            except:
                (exceptionType, exceptionValue, exceptionTraceback) = sys.exc_info()
                frames = traceback.extract_tb(exceptionTraceback)[2:]
                dialog = wx.MessageDialog(self, str(exceptionValue) + ' (' + exceptionType.__name__ + ')' + '\n\nTraceback:\n' + ''.join(traceback.format_list(frames)), gettext('An error occurred while running the script:'), style = wx.ICON_ERROR | wx.OK)
                dialog.ShowModal()
        dlg.Destroy()
        self.Show(True)
    
    
    def onUndo(self, event_):
        self._console.Undo()
    
    
    def onRedo(self, event_):
        self._console.Redo()
    
    
    def onCut(self, event_):
        self._console.Cut()
    
    
    def onCopy(self, event_):
        self._console.Copy()
    
    
    def onPaste(self, event_):
        self._console.Paste()
    
    
    def onSelectAll(self, event_):
        self.display.selectAll()
    
    
    def onFind(self, event_):
        if self.finder is None:
            self.finder = Finder(self, -1, gettext('Finder'), pos=(-1,-1))
        
        if self.finder.ShowModal() == wx.ID_OK:
            self.display.selectObjectsMatching(self.finder.predicate)
            if not any(self.display.selection()):
                wx.Bell()
    
    
    def OnUseMouseOverSelecting(self, event_):
        self.display.setUseMouseOverSelecting(not self.display.useMouseOverSelecting())
    
    
    def onHighlightOnlyWithinSelection(self, event_):
        self.display.setHighlightOnlyWithinSelection(not self.display.highlightOnlyWithinSelection())
    
    
    def onShowHideRegionNames(self, event_):
        self.display.setShowRegionNames(not self.display.showRegionNames())
    
    
    def onShowHideNeuronNames(self, event_):
        self.display.setShowNeuronNames(not self.display.showNeuronNames())
    
    
    def onSetLabelsFloatOnTop(self, event_):
        self.display.setLabelsFloatOnTop(not self.display.labelsFloatOnTop())
    
    
    def onShowFlow(self, event_):
        self.display.setShowFlow(not self.display.showFlow())
    
    
    def onUseGhosts(self, event_):
        self.display.setUseGhosts(not self.display.useGhosts())
    
    
    def onUpdateLayoutUI(self, event):
        menuItem = self.GetMenuBar().FindItemById(event.GetId())
        layoutClass = self.layoutClasses[event.GetId()]
        menuItem.Enable(layoutClass.canLayoutDisplay(self.display))
    
    
    def onResetView(self, event_):
        self.display.resetView()
    
    
    def onZoomToFit(self, event_):
        self.display.zoomToFit()
    
    
    def onZoomToSelection(self, event_):
        self.display.zoomToSelection()
    
    
    def onZoomIn(self, event_):
        self.display.zoomIn()
    
    
    def onZoomOut(self, event_):
        self.display.zoomOut()
    
    
    def onCloseWindow(self, event):
        doClose = True
        
        if self._modified:
            if platform.system() == 'Windows':
                message = gettext('Your changes will be lost if you don\'t save them.') + '\n\n' + gettext('Do you want to save the changes you made to "%s"?') % (self.display.network.name())
                caption = gettext('Neuroptikon')
            else:
                message = gettext('Your changes will be lost if you don\'t save them.')
                caption = gettext('Do you want to save the changes you made to "%s"?') % (self.display.network.name())
            dialog = wx.MessageDialog(self, message, caption, style = wx.ICON_QUESTION | wx.YES_NO | wx.CANCEL)
            result = dialog.ShowModal()
            dialog.Destroy()
            if result == wx.ID_YES:
                doClose = self.onSaveNetwork()
            elif result == wx.ID_CANCEL:
                doClose = False
        
        if doClose:
            self.display.selectObjects([])
            wx.GetApp().inspector.inspectDisplay(None)
            network = self.display.network
            dispatcher.disconnect(self.networkDidChangeSavePath, ('set', 'savePath'), network)
            self.display.close()
            self.display = None
            self.Destroy()
            wx.GetApp().displayWasClosed(self)
            if not any(network.displays):
                wx.GetApp().releaseNetwork(network)
        elif event.GetEventType() == wx.wxEVT_CLOSE_WINDOW:
            event.Veto()
    
    
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
        xmlRoot = ElementTree.Element('Neuroptikon')
        network = self.display.network
        
        # Serialize the network
        networkElement = network._toXMLElement(xmlRoot)
        if networkElement is None:
            raise ValueError, gettext('Could not save the network')
        
        if saveDisplays:
            # Serialize the display(s)
            for display in network.displays:
                frameElement = display.GetTopLevelParent()._toXMLElement(xmlRoot)
                if frameElement is None:
                    raise ValueError, gettext('Could not save one of the windows')
        
        self.indentXMLElement(xmlRoot)
        xmlTree = ElementTree.ElementTree(xmlRoot)
        xmlTree.write(savePath)
        
        # To test the contents of the output use:
        # xmllint --noout --schema Source/Neuroptikon_v1.0.xsd Test.xml
    
    
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
            for networkObject in network.objects:
                if networkObject._includeInScript():
                    objectName = networkObject.name
                    defaultName = networkObject.defaultName()
                    
                    # Make sure the object has a name.
                    if not objectName and not defaultName:
                        for display in network.displays:
                            display.selectObject(networkObject)
                        raise ValueError, gettext('The display of the selected object cannot be saved because it does not have a name.')
                    
                    # Make sure the name is unique.
                    if objectName:
                        nameKey = networkObject.__class__.__name__ + ': ' + objectName
                        if nameKey in objectNames:
                            for display in network.displays:
                                display.selectObjects([networkObject, objectNames[nameKey]])
                            raise ValueError, gettext('The display cannot be saved because there is more than one %s with the name \'%s\'.') % (networkObject.__class__.__name__.lower(), objectName)
                    else:
                        nameKey = networkObject.__class__.__name__ + ': ' + defaultName
                        if nameKey in objectNames:
                            for display in network.displays:
                                display.selectObjects([networkObject, objectNames[nameKey]])
                            raise ValueError, gettext('The display cannot be saved because there is more than one %s with the default name \'%s\'.') % (networkObject.__class__.__name__.lower(), defaultName)
                    
                    # Create the script ref.
                    objectNames[nameKey] = networkObject
                    if 'find' + networkObject.__class__.__name__ in dir(network):
                        prefix = 'network.find' + networkObject.__class__.__name__ + '(\''
                    else:
                        prefix = 'network.findObject(' + networkObject.__class__.__name__ + ', \''
                    if objectName:
                        scriptRefs[networkObject.networkId] = prefix + objectName + '\')'
                    else:
                        scriptRefs[networkObject.networkId] = prefix + defaultName + '\', default = True)'
        
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
                network._toScriptFile(scriptFile, scriptRefs)
            
            if saveDisplays:
                # Serialize the display(s)
                for display in network.displays:
                    display.GetTopLevelParent()._toScriptFile(scriptFile, scriptRefs)
            else:
                scriptFile.write('\n# Reveal the default visualization\ndisplay.zoomToFit()\n')
        except:
            raise    # TODO: inform the user nicely
        finally:
            scriptFile.close()
    
    
    def onSaveNetwork(self, event_ = None):
        success = False
        
        network = self.display.network
        if network.savePath() is None:
            dlg = wx.FileDialog(None, gettext('Save as:'), '', 'Network.xml', '*.xml', wx.SAVE | wx.FD_OVERWRITE_PROMPT)
            if dlg.ShowModal() == wx.ID_OK:
                savePath = dlg.GetPath()
                if not savePath.endswith('.xml'):
                    savePath += '.xml'
                network.setSavePath(savePath)
        
        if network.savePath() is not None:
            try:
                self.saveNetworkAndDisplaysAsXML(network.savePath())
                self.display.network.setModified(False)
                for display in network.displays:
                    display.GetTopLevelParent().setModified(False)
                success = True
            except:
                (exceptionType, exceptionValue, exceptionTraceback) = sys.exc_info()
                dialog = wx.MessageDialog(self, str(exceptionValue) + ' (' + exceptionType.__name__ + ')', gettext('The file could not be saved.'), style = wx.ICON_ERROR | wx.OK)
                dialog.ShowModal()
        
        return success
    
    
    def onSaveNetworkAs(self, event_):
        network = self.display.network
        fileTypes = ['XML File', 'XML File (network only)', 'Python Script', 'Python Script (network only)', 'Python Script (display only)']
        fileExtensions = ['xml', 'xml', 'py', 'py', 'py']
        wildcard = ''
        for index in range(0, len(fileTypes)):
            if wildcard != '':
                wildcard += '|'
            wildcard += fileTypes[index] + '|' + fileExtensions[index]
        fileDialog = wx.FileDialog(None, gettext('Save As:'), '', '', wildcard, wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if network.savePath() == None:
            fileDialog.SetFilename('Network.xml')
        else:
            fileDialog.SetFilename(os.path.basename(network.savePath()))
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
                    network.setSavePath(savePath)
                    self.saveNetworkAndDisplaysAsXML(savePath, saveDisplays)
                    self.display.network.setModified(False)
                    for display in network.displays:
                        display.GetTopLevelParent().setModified(False)
                    # TODO: if only the network was saved and the diplay was changed then those changes could be lost...
                else:
                    self.saveNetworkAndDisplaysAsScript(savePath, saveNetwork, saveDisplays)
            except:
                (exceptionType, exceptionValue, exceptionTraceback) = sys.exc_info()
                dialog = wx.MessageDialog(self, exceptionType.__name__ + ": " + str(exceptionValue), gettext('The file could not be saved.'), style = wx.ICON_ERROR | wx.OK)
                dialog.ShowModal()
    
    
    def setModified(self, modified):
        if self._modified != modified:
            self._modified = modified
            if platform.system() == 'Darwin':
                # Use ctypes to call into the Carbon API to set the window's modified state.  When modified is True this causes the close button to be drawn with a dot inside it.
                # Use wx.CallAfter otherwise the dot won't show up until the window is resized, deactivated or the mouse hovers over the button.
                wx.CallAfter(carbon.SetWindowModified, self.MacGetTopLevelWindowRef(), modified)
            elif platform.system() == 'Windows':
                title = self.GetTitle()
                if modified and not title.endswith('*'):
                    self.SetTitle(title + '*')
                elif not modified and title.endswith('*'):
                    self.SetTitle(title[:-1])
    
    
    def isModified(self):
        return self._modified
    
