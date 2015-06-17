#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

from __future__ import with_statement # This isn't required in Python 2.6

import neuroptikon
import wx.glcanvas
from pydispatch import dispatcher
import osg, osgDB, osgGA, osgManipulator, osgText, osgViewer
from math import log, pi
import os.path, platform, sys, cPickle
try:
    import xml.etree.cElementTree as ElementTree
except ImportError:
    import xml.etree.ElementTree as ElementTree

from gettext import gettext
from pick_handler import PickHandler
from dragger_cull_callback import DraggerCullCallback
from network.object import Object
from network.pathway import Pathway # pylint: disable=E0611,F0401
from network.arborization import Arborization
from network.stimulus import Stimulus
from network.object_list import ObjectList
from visible import Visible
import layout as layout_module
from shape import Shape
from library.texture import Texture
import time


# Navigation modes

PANNING_MODE = 0
ROTATING_MODE = 1
# TODO: DRAG_SELECTING_MODE = 2
# TODO: other modes?


class Display(wx.glcanvas.GLCanvas):
    
    def __init__(self, parent, network = None, wxId = wx.ID_ANY):
        """
        Displays allow the visualization of networks.
        
        Each display can visualize any number of objects from a single network.  By default all objects added to the network are visualized but this can be disabled by setting the display's autoVisualize attribute to False
        
        Multiple displays can visualize the same network at the same time.  By default the selection is synchronized between displays so selecting an object in one display will select the corresponding object in all other displays.  This can be disabled by calling setSynchronizeDisplays(False) on the network.
        
        You should never create an instance of this class directly.  Instances are automatically created when you open a new window either via File --> New Network or by calling displayNetwork() in a console or script.
        """
        
        style = wx.WANTS_CHARS | wx.FULL_REPAINT_ON_RESIZE | wx.HSCROLL | wx.VSCROLL
        attribList = [wx.glcanvas.WX_GL_RGBA, wx.glcanvas.WX_GL_DOUBLEBUFFER]
        if neuroptikon.config.ReadBool('Smooth All Objects') and hasattr(wx.glcanvas, 'WX_GL_SAMPLE_BUFFERS'):
            attribList += [wx.glcanvas.WX_GL_SAMPLE_BUFFERS, 1, wx.glcanvas.WX_GL_SAMPLES, 4]
        attribList += [wx.glcanvas.WX_GL_DEPTH_SIZE, 16, 0, 0]
        wx.glcanvas.GLCanvas.__init__(self, parent, wxId, attribList = attribList, pos = wx.DefaultPosition, size = (200,200), style = style, name = "")
        self.glContext = wx.glcanvas.GLContext(self)
        
        self._name = None
        self.network = network
        if self.network is not None:
            self.network.addDisplay(self)
        self.displayRules = []
        self.autoVisualize = True
        self.visibles = {}
        self._visibleIds = {}
        self.selectedVisibles = set()
        self.highlightedVisibles = set()
        self.animatedVisibles = set()
        self.selectConnectedVisibles = True
        self._showRegionNames = True
        self._showNeuronNames = False
        self._labelsFloatOnTop = False
        self._showFlow = False
        self._highlightOnlyWithinSelection = False
        self._useGhosts = True
        self._ghostingOpacity = 0.25
        self._primarySelectionColor = (0, 0, 1, .4)
        self._secondarySelectionColor = (0, 0, 1, .2)
        self._selectionHighlightDepth = 3
        self.viewDimensions = 2
        
        self._recomputeBounds = True
        self._recomputeBoundsScheduled = False
        self.visiblesMin = [-100, -100, -100]
        self.visiblesMax = [100, 100, 100]
        self.visiblesCenter = [0, 0, 0]
        self.visiblesSize = [200, 200, 200]
        
        self._navigationMode = PANNING_MODE
        self._previous3DNavMode = ROTATING_MODE
        
        self.orthoCenter = (0, 0)
        self.orthoViewPlane = 'xy'
        self.orthoXPlane = 0
        self.orthoYPlane = 1
        self.orthoZoom = 0
        self.zoomScale = 1
        self.rootNode = osg.MatrixTransform()
        self.rootStateSet = self.rootNode.getOrCreateStateSet()
        self.rootNode.setMatrix(osg.Matrixd.identity())
        self.rootStateSet.setMode(osg.GL_NORMALIZE, osg.StateAttribute.ON )
        if platform.system() == 'Windows':
            self.scrollWheelScale = 0.1
        else:
            self.scrollWheelScale = 1
        
        # TODO: only if pref set?
        # Not in osg 3.2.1?
        # osg.DisplaySettings.instance().setNumMultiSamples(4)
        
        self.trackball = osgGA.TrackballManipulator()
        self._previousTrackballMatrix = None
        self._previousTrackballCenter = None
        self._pickHandler = PickHandler(self)
        
        self.viewer = osgViewer.Viewer()
        self.viewer.setThreadingModel(osgViewer.ViewerBase.SingleThreaded)  # TODO: investigate multithreaded options
        self.viewer.addEventHandler(osgViewer.StatsHandler())
        self.viewer.setSceneData(self.rootNode)
        self.viewer.addEventHandler(self._pickHandler)
        
        light = self.viewer.getLight()
        light.setAmbient(osg.Vec4f(0.4, 0.4, 0.4, 1))
        light.setDiffuse(osg.Vec4f(0.5, 0.5, 0.5, 1))
        self.viewer.setLight(light)
        
        self._first3DView = True
        
        self.backgroundColor = None
        clearColor = (neuroptikon.config.ReadFloat("Color/Background/Red", 0.75), \
                      neuroptikon.config.ReadFloat("Color/Background/Green", 0.75), \
                      neuroptikon.config.ReadFloat("Color/Background/Blue", 0.75), \
                      neuroptikon.config.ReadFloat("Color/Background/Alpha", 0.0))
        self.setBackgroundColor(clearColor)
        
        self.Bind(wx.EVT_SIZE, self.onSize)
        self.Bind(wx.EVT_PAINT, self.onPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.onEraseBackground)
        self.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
        self.Bind(wx.EVT_KEY_UP, self.onKeyUp)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.onMouseEvent)  # TODO: factor this out into individual events
        self.Bind(wx.EVT_MOUSEWHEEL, self.onMouseWheel)
        self.Bind(wx.EVT_SCROLLWIN, self.onScroll)
        
        self.dragSelection = None
        self.draggerLOD = None
        self.simpleDragger = None
        self.compositeDragger = None
        self.activeDragger = None
        self.commandMgr = None
        self.draggerScale = 1.0
        self.draggerOffset = (0.0, 0.0, 0.0)
        
        self.selectionShouldExtend = False
        self.findShortestPath = False
        self._selectedShortestPath = False
        
        self._useMouseOverSelecting = False
        self.hoverSelect = True
        self.hoverSelecting = False
        self.hoverSelected = False  # set to True if the current selection was made by hovering
        
        width, height = self.GetClientSize()
        self.graphicsWindow = self.viewer.setUpViewerAsEmbeddedInWindow(0, 0, width, height)
        
        self.SetDropTarget(DisplayDropTarget(self))
    
        self._nextUniqueId = -1
        
        self._animationTimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onAnimate, self._animationTimer)
        self._suppressRefresh = False
        
        if neuroptikon.runningFromSource:
            shaderDir = os.path.join(neuroptikon.rootDir, 'display')
        else:
            shaderDir = neuroptikon.rootDir
        with open(os.path.join(shaderDir, 'flow_shader.vert')) as f:
            flowVertexShader = f.read()
        with open(os.path.join(shaderDir, 'flow_shader.frag')) as f:
            flowFragmentShader = f.read()
        self.flowProgram = osg.Program()
        self.flowProgram.addShader(osg.Shader(osg.Shader.VERTEX, flowVertexShader))
        self.flowProgram.addShader(osg.Shader(osg.Shader.FRAGMENT, flowFragmentShader))
        
        self.defaultFlowColor = (1.0, 1.0, 1.0, 1.0)
        self.defaultFlowToColorUniform = osg.Uniform('flowToColor', osg.Vec4f(*self.defaultFlowColor))
        self.rootStateSet.addUniform(self.defaultFlowToColorUniform)
        self.defaultFlowFromColorUniform = osg.Uniform('flowFromColor', osg.Vec4f(*self.defaultFlowColor))
        self.rootStateSet.addUniform(self.defaultFlowFromColorUniform)
        self.defaultFlowSpacing = 0.05   # Distance between pulses
        self.defaultFlowToSpacingUniform = osg.Uniform('flowToSpacing', self.defaultFlowSpacing)
        self.rootStateSet.addUniform(self.defaultFlowToSpacingUniform)
        self.defaultFlowFromSpacingUniform = osg.Uniform('flowFromSpacing', self.defaultFlowSpacing)
        self.rootStateSet.addUniform(self.defaultFlowFromSpacingUniform)
        self.defaultFlowSpeed = 0.05     # Pulse speed 
        self.defaultFlowToSpeedUniform = osg.Uniform('flowToSpeed', self.defaultFlowSpeed)
        self.rootStateSet.addUniform(self.defaultFlowToSpeedUniform)
        self.defaultFlowFromSpeedUniform = osg.Uniform('flowFromSpeed', self.defaultFlowSpeed)
        self.rootStateSet.addUniform(self.defaultFlowFromSpeedUniform)
        self.defaultFlowSpread = 0.5    # The pulse should cover 50% of the path
        self.defaultFlowToSpreadUniform = osg.Uniform('flowToSpread', self.defaultFlowSpread)
        self.rootStateSet.addUniform(self.defaultFlowToSpreadUniform)
        self.defaultFlowFromSpreadUniform = osg.Uniform('flowFromSpread', self.defaultFlowSpread)
        self.rootStateSet.addUniform(self.defaultFlowFromSpreadUniform)
        
        dispatcher.connect(self._onSelectionOrShowFlowChanged, ('set', 'selection'), self)
        dispatcher.connect(self._onSelectionOrShowFlowChanged, ('set', 'showFlow'), self)
        
        self.lastUsedLayout = None
        
        self._closing = False
        
        self._visibleBeingAdded = None
        
        self.compassCamera = None
        self._compassDrawables = {}
    
    
    def _fromXMLElement(self, xmlElement):
        self._suppressRefresh = True
        
        name = xmlElement.findtext('Name')
        if name is not None:
            self.setName(name)
        
        colorElement = xmlElement.find('BackgroundColor')
        if colorElement is None:
            colorElement = xmlElement.find('backgroundColor')
        if colorElement is not None:
            red = float(colorElement.get('r'))
            green = float(colorElement.get('g'))
            blue = float(colorElement.get('b'))
            alpha = float(colorElement.get('a'))
            self.setBackgroundColor((red, green, blue, alpha))
        
        flowAppearanceElement = xmlElement.find('DefaultFlowAppearance')
        if flowAppearanceElement is None:
            flowAppearanceElement = xmlElement.find('defaultFlowAppearance')
        if flowAppearanceElement is not None:
            colorElement = flowAppearanceElement.find('Color')
            if colorElement is None:
                colorElement = flowAppearanceElement.find('color')
            if colorElement is not None:
                red = float(colorElement.get('r'))
                green = float(colorElement.get('g'))
                blue = float(colorElement.get('b'))
                alpha = float(colorElement.get('a'))
                self.setDefaultFlowColor((red, green, blue))
            if flowAppearanceElement.get('spacing') is not None:
                self.setDefaultFlowSpacing(float(flowAppearanceElement.get('spacing')))
            if flowAppearanceElement.get('speed') is not None:
                self.setDefaultFlowSpeed(float(flowAppearanceElement.get('speed')))
            if flowAppearanceElement.get('spread') is not None:
                self.setDefaultFlowSpread(float(flowAppearanceElement.get('spread')))
            if self.defaultFlowSpacing == 1.0 and self.defaultFlowSpeed == 1.0 and self.defaultFlowSpread == 0.2:
                # Switch to new world-space relative defaults.
                self.setDefaultFlowSpacing(0.05)
                self.setDefaultFlowSpeed(0.05)
                
        
        visibleElements = xmlElement.findall('Visible')
        
        # Add all of the nodes
        for visibleElement in visibleElements:
            if visibleElement.find('Path') is None and visibleElement.find('path') is None:
                visible = Visible._fromXMLElement(visibleElement, self)
                if visible is None:
                    raise ValueError, gettext('Could not create visualized item')
                self.addVisible(visible)
                
        # Add all of the paths (must be done after nodes are added)
        for visibleElement in visibleElements:
            if visibleElement.find('Path') is not None or visibleElement.find('path') is not None:
                visible = Visible._fromXMLElement(visibleElement, self)
                if visible is None:
                    raise ValueError, gettext('Could not create visualized item')
                self.addVisible(visible)
        
        self.computeVisiblesBound()
        
        self.setViewDimensions(int(xmlElement.get('dimensions')))
        
        trueValues = ['true', 'True', 'TRUE', '1']
        if xmlElement.get('showRegionNames') is not None:
            self.setShowRegionNames(xmlElement.get('showRegionNames') in trueValues)
        if xmlElement.get('showNeuronNames') is not None:
            self.setShowNeuronNames(xmlElement.get('showNeuronNames') in trueValues)
        if xmlElement.get('showFlow') is not None:
            self.setShowFlow(xmlElement.get('showFlow') in trueValues)
        if xmlElement.get('useGhosting') is not None:
            self.setUseGhosts(xmlElement.get('useGhosting') in trueValues)
        if xmlElement.get('ghostingOpacity') is not None:
            self.setGhostingOpacity(float(xmlElement.get('ghostingOpacity')))
        if xmlElement.get('useMouseOverSelecting') is not None:
            self._useMouseOverSelecting = xmlElement.get('useMouseOverSelecting') in trueValues
        if xmlElement.get('autoVisualize') is not None:
            self.autoVisualize = xmlElement.get('autoVisualize') in trueValues
        if xmlElement.get('labelsFloatOnTop') is not None:
            self.setLabelsFloatOnTop(xmlElement.get('labelsFloatOnTop') in trueValues)
        if xmlElement.get('selectionHighlightDepth') is not None:
            self.setSelectionHighlightDepth(int(xmlElement.get('selectionHighlightDepth')))
        if xmlElement.get('highlightOnlyWithinSelection') is not None:
            self.setHighlightOnlyWithinSelection(xmlElement.get('highlightOnlyWithinSelection') in trueValues)
        if xmlElement.get('showCompass') is not None:
            self.setShowCompass(xmlElement.get('showCompass') in trueValues)
        
        selectedVisibleIds = xmlElement.get('selectedVisibleIds')
        visiblesToSelect = []
        if selectedVisibleIds is not None:
            for visibleId in selectedVisibleIds.split(','):
                if visibleId.isdigit() and int(visibleId) in self._visibleIds:
                    visiblesToSelect.append(self._visibleIds[int(visibleId)])
        self.selectVisibles(visiblesToSelect)
        
        self._suppressRefresh = False
        
        self._recomputeBounds = True
        if self.viewDimensions == 2:
            self.zoomToFit()
        else:
            self.resetView()
        self.Refresh()
    
    
    def _toXMLElement(self, parentElement):
        displayElement = ElementTree.SubElement(parentElement, 'Display')
        
        if self._name:
            ElementTree.SubElement(displayElement, 'Name').text = self._name
        
        # Add the background color
        colorElement = ElementTree.SubElement(displayElement, 'BackgroundColor')
        colorElement.set('r', str(self.backgroundColor[0]))
        colorElement.set('g', str(self.backgroundColor[1]))
        colorElement.set('b', str(self.backgroundColor[2]))
        colorElement.set('a', str(self.backgroundColor[3]))
        
        # Add the default flow appearance
        flowAppearanceElement = ElementTree.SubElement(displayElement, 'DefaultFlowAppearance')
        colorElement = ElementTree.SubElement(flowAppearanceElement, 'Color')
        colorElement.set('r', str(self.defaultFlowColor[0]))
        colorElement.set('g', str(self.defaultFlowColor[1]))
        colorElement.set('b', str(self.defaultFlowColor[2]))
        colorElement.set('a', str(self.defaultFlowColor[3]))
        flowAppearanceElement.set('spacing', str(self.defaultFlowSpacing))
        flowAppearanceElement.set('speed', str(self.defaultFlowSpeed))
        flowAppearanceElement.set('spread', str(self.defaultFlowSpread))
        
        # Add the display rules
        for displayRule in self.displayRules:
            ruleElement = displayRule._toXMLElement(displayElement)
            if ruleElement is None:
                raise ValueError, gettext('Could not save display rule')
        
        # Add the visibles
        for visibles in self.visibles.itervalues():
            for visible in visibles:
                if visible.parent is None:
                    visibleElement = visible._toXMLElement(displayElement)
                    if visibleElement is None:
                        raise ValueError, gettext('Could not save visualized item')
        
        displayElement.set('dimensions', str(self.viewDimensions))
        displayElement.set('showRegionNames', 'true' if self._showRegionNames else 'false')
        displayElement.set('showNeuronNames', 'true' if self._showNeuronNames else 'false')
        displayElement.set('showFlow', 'true' if self._showFlow else 'false')
        displayElement.set('useGhosting', 'true' if self._useGhosts else 'false')
        displayElement.set('ghostingOpacity', str(self._ghostingOpacity))
        displayElement.set('useMouseOverSelecting', 'true' if self._useMouseOverSelecting else 'false')
        displayElement.set('autoVisualize', 'true' if self.autoVisualize else 'false')
        displayElement.set('labelsFloatOnTop', 'true' if self._labelsFloatOnTop else 'false')
        displayElement.set('selectionHighlightDepth', str(self._selectionHighlightDepth))
        displayElement.set('highlightOnlyWithinSelection', 'true' if self._highlightOnlyWithinSelection else 'false')
        displayElement.set('showCompass', 'true' if self.isShowingCompass() else 'false')
        selectedVisibleIds = []
        for visible in self.selectedVisibles:
            selectedVisibleIds.append(str(visible.displayId))
        displayElement.set('selectedVisibleIds', ','.join(selectedVisibleIds))
        
        return displayElement
    
    
    def _toScriptFile(self, scriptFile, scriptRefs, displayRef, savingNetwork):
        if self._name != None:
            scriptFile.write(displayRef + '.setName(' + repr(self._name) + ')\n')
        scriptFile.write(displayRef + '.setBackgroundColor((' + ', '.join([str(component) for component in self.backgroundColor]) + '))\n')
        scriptFile.write(displayRef + '.setDefaultFlowColor(' + str(self.defaultFlowColor) + ')\n')
        scriptFile.write(displayRef + '.setDefaultFlowSpacing(' + str(self.defaultFlowSpacing) + ')\n')
        scriptFile.write(displayRef + '.setDefaultFlowSpeed(' + str(self.defaultFlowSpeed) + ')\n')
        scriptFile.write(displayRef + '.setDefaultFlowSpread(' + str(self.defaultFlowSpread) + ')\n')
        scriptFile.write(displayRef + '.setViewDimensions(' + str(self.viewDimensions) + ')\n')
        scriptFile.write(displayRef + '.setShowCompass(' + str(self.isShowingCompass()) + ')\n')
        scriptFile.write(displayRef + '.setShowRegionNames(' + str(self._showRegionNames) + ')\n')
        scriptFile.write(displayRef + '.setShowNeuronNames(' + str(self._showNeuronNames) + ')\n')
        scriptFile.write(displayRef + '.setShowFlow(' + str(self._showFlow) + ')\n')
        scriptFile.write(displayRef + '.setUseGhosts(' + str(self._useGhosts) + ')\n')
        scriptFile.write(displayRef + '.setGhostingOpacity(' + str(self._ghostingOpacity) + ')\n')
        scriptFile.write(displayRef + '.setUseMouseOverSelecting(' + str(self._useMouseOverSelecting) + ')\n')
        scriptFile.write(displayRef + '.setLabelsFloatOnTop(' + str(self._labelsFloatOnTop) + ')\n')
        scriptFile.write(displayRef + '.setSelectionHighlightDepth(' + str(self._selectionHighlightDepth) + ')\n')
        scriptFile.write(displayRef + '.setHighlightOnlyWithinSelection(' + str(self._highlightOnlyWithinSelection) + ')\n')
        scriptFile.write('\n')
        
        # First visualize all of the nodes.
        for visibles in self.visibles.itervalues():
            for visible in visibles:
                if not visible.isPath() and visible.parent is None and not isinstance(visible.client, Stimulus):
                    visible._toScriptFile(scriptFile, scriptRefs, displayRef, savingNetwork)
        # Next visualize all of the connections between the nodes.
        for visibles in self.visibles.itervalues():
            for visible in visibles:
                if visible.isPath():
                    visible._toScriptFile(scriptFile, scriptRefs, displayRef, savingNetwork)
        
        objectRefs = []
        visibleIds = []
        for visible in self.selectedVisibles:
            if visible.client:
                objectRefs.append(scriptRefs[visible.client.networkId])
            else:
                visibleIds += [visible.displayId]
        if any(objectRefs):
            scriptFile.write(displayRef + '.selectObjects([' + ', '.join(objectRefs) + '])\n')
        for visibleId in visibleIds:
            scriptFile.write(displayRef + '.selectVisibles([' + displayRef + '.visibleWithId(' + visibleId + ')], extend = True)')
        
        if self.viewDimensions == 2:
            scriptFile.write('\n' + displayRef + '.zoomToFit()\n')
        else:
            scriptFile.write('\n' + displayRef + '.resetView()\n')
    
    
    def setName(self, name):
        if name != self._name:
            self._name = name
            dispatcher.send(('set', 'name'), self)
    
    
    def name(self):
        return None if not self._name else str(self._name)
    
    
    def _generateUniqueId(self):
        self._nextUniqueId += 1
        return self._nextUniqueId
    
    
    def setViewDimensions(self, dimensions):
        """ Set the number of dimension in which to visualize the network.
        
        The argument must be either 2 or 3.
        """
        
        if dimensions not in (2, 3):
            raise ValueError, 'The dimensions argument passed to setViewDimensions() must be 2 or 3.'
         
        if dimensions != self.viewDimensions:
            self.viewDimensions = dimensions
            width, height = self.GetClientSize()
            
            self._clearDragger()
            
            if self.viewDimensions == 2:
                self._previous3DNavMode = self._navigationMode
                self.setNavigationMode(PANNING_MODE)
                self._previousTrackballMatrix = self.trackball.getMatrix()
                self._previousTrackballCenter = self.trackball.getCenter()
                self.viewer.setCameraManipulator(None)
                self.computeVisiblesBound()
                self._resetView()
            elif self.viewDimensions == 3:
                self.setNavigationMode(self._previous3DNavMode)
                # Hide the scroll bars before we get the size of the viewport.
                self.SetScrollbar(wx.HORIZONTAL, 0, width, width, True)
                self.SetScrollbar(wx.VERTICAL, 0, height, height, True)
                width, height = self.GetClientSize()
                self.graphicsWindow = self.viewer.setUpViewerAsEmbeddedInWindow(0, 0, width, height)
                self.viewer.getCamera().setProjectionMatrixAsPerspective(30.0, float(width)/height, 1.0, 1000.0)
                self.viewer.setCameraManipulator(self.trackball)
                if self._first3DView:
                    self.resetView()
                    self._first3DView = False
                else:
                    self.trackball.computeHomePosition()
                    self.viewer.home()
                    self.trackball.setByMatrix(self._previousTrackballMatrix)
                    #self.trackball.setCenter(self._previousTrackballCenter)
            
            if len(self.selectedVisibles) == 1:
                visible = list(self.selectedVisibles)[0]
                if visible._isDraggable():
                    self._addDragger(visible)
            
            # Call _updatePath on all path visibles so parallel edges are drawn correctly.
            for visibles in self.visibles.values():
                for visible in visibles:
                    if visible.isPath():
                        visible._updatePath()
            
            self._updateCompassAxes()
            
            self.Refresh()
            dispatcher.send(('set', 'viewDimensions'), self)
    
    
    def onViewIn2D(self, event_):
        self.setViewDimensions(2)
    
    
    def onViewIn3D(self, event_):
        self.setViewDimensions(3)
    
    
    def setOrthoViewPlane(self, plane):
        """
        Set which plane should be viewed in 2D.
        
        The argument must be one of 'xy', 'xz' or 'zy'.
        """
        
        if plane not in ('xy', 'xz', 'zy'):
            raise ValueError, "The plane argument passed to setOrthoViewPlane() must be one of 'xy', 'xz' or 'zy'"
       
        if plane != self.orthoViewPlane:
            self.orthoViewPlane = plane
            if self.orthoViewPlane == 'xy':
                self.orthoXPlane = 0
                self.orthoYPlane = 1
            elif self.orthoViewPlane == 'xz':
                self.orthoXPlane = 0
                self.orthoYPlane = 2
            elif self.orthoViewPlane == 'zy':
                self.orthoXPlane = 1
                self.orthoYPlane = 2
            self._resetView()
            
            # Call _updatePath on all path visibles so parallel edges are drawn correctly.
            for visibles in self.visibles.values():
                for visible in visibles:
                    if visible.isPath():
                        visible._updatePath()
            
            self._updateCompassAxes()
            
            self.Refresh()
            dispatcher.send(('set', 'orthoViewPlane'), self)
    
    
    def setShowCompass(self, showCompass):
        
        def _addCompassAxis(geode, text, position):
            # Add a line along the axis.
            axis = osg.Geometry()
            axis.setVertexArray(Shape.vectorArrayFromList([(0.0, 0.0, 0.0), (position[0] * 0.75, position[1] * 0.75, position[2] * 0.75)]))
            axis.addPrimitiveSet(Shape.primitiveSetFromList(osg.PrimitiveSet.LINE_STRIP, range(2)))
            axis.setNormalArray(Shape.vectorArrayFromList([(0.0, 0.0, 0.0)]))
            axis.setNormalBinding(osg.Geometry.BIND_OVERALL)
            axis.setColorArray(Shape.vectorArrayFromList([(0.5, 0.5, 0.5)]))
            axis.setColorBinding(osg.Geometry.BIND_OVERALL)
            geode.addDrawable(axis)
            
            # Add the axis label.
            label = osgText.Text()
            label.setCharacterSizeMode(osgText.Text.SCREEN_COORDS)
            if Visible.labelFont is None:
                label.setCharacterSize(48.0)
            else:
                label.setFont(Visible.labelFont)
                label.setCharacterSize(18.0)
            label.setAxisAlignment(osgText.Text.SCREEN)
            label.setAlignment(osgText.Text.CENTER_CENTER)
            label.setColor(osg.Vec4(0.25, 0.25, 0.25, 1.0))
            label.setBackdropColor(osg.Vec4(0.75, 0.75, 0.75, 0.25))
            label.setBackdropType(osgText.Text.OUTLINE)
            label.setPosition(osg.Vec3(*position))
            label.setText(text)
            geode.addDrawable(label)
            
            return (axis, label)
        
        if showCompass != (self.compassCamera != None):
            if showCompass:
                self.compassCamera = osg.Camera()
                self.compassCamera.setProjectionMatrixAsPerspective(30.0, 1.0, 1.0, 10000.0)
                self.compassCamera.setReferenceFrame(osg.Transform.ABSOLUTE_RF)
                self.compassCamera.setViewMatrixAsLookAt(osg.Vec3d(0, 0, 5), osg.Vec3d(0, 0, 0), osg.Vec3d(0, 1, 0))
                self.compassCamera.setClearMask(osg.GL_DEPTH_BUFFER_BIT)
                self.compassCamera.setRenderOrder(osg.Camera.POST_RENDER)
                self.compassCamera.setAllowEventFocus(False)
                self.compassCamera.setViewport(0, 0, 50, 50)
                        
                # Add the axes
                self._compassGeode = osg.Geode()
                self.compassTransform = osg.MatrixTransform()
                self.compassTransform.addChild(self._compassGeode)
                self.compassCamera.addChild(self.compassTransform)
                self._compassDrawables['X'] = _addCompassAxis(self._compassGeode, 'X', (1.0, 0.0, 0.0))
                self._compassDrawables['Y'] = _addCompassAxis(self._compassGeode, 'Y', (0.0, 1.0, 0.0))
                self._compassDrawables['Z'] = _addCompassAxis(self._compassGeode, 'Z', (0.0, 0.0, 1.0))
                self._updateCompassAxes()
                
                stateSet = self._compassGeode.getOrCreateStateSet() 
                stateSet.setMode(osg.GL_LIGHTING, osg.StateAttribute.OFF)
                stateSet.setMode(osg.GL_LINE_SMOOTH, osg.StateAttribute.ON)
                stateSet.setRenderingHint(osg.StateSet.TRANSPARENT_BIN)
                stateSet.setMode(osg.GL_BLEND, osg.StateAttribute.ON)
                
                self.rootNode.addChild(self.compassCamera)
            else:
                self.rootNode.removeChild(self.compassCamera)
                self._compassGeode = None
                self.compassCamera = None
            
            self.Refresh()
    
    
    def isShowingCompass(self):
        return self.compassCamera != None
    
    
    def _updateCompassAxes(self):
        # Show/hide the desired axes.
        
        if self.compassCamera:
            if self.viewDimensions == 2:
                if self.orthoViewPlane == 'xy':
                    axesToShow = ['X', 'Y']
                elif self.orthoViewPlane == 'xz':
                    axesToShow = ['X', 'Z']
                elif self.orthoViewPlane == 'zy':
                    axesToShow = ['Y', 'Z']
            else:
                axesToShow = ['X', 'Y', 'Z']
            
            for axis in ['X', 'Y', 'Z']:
                for drawable in self._compassDrawables[axis]:
                    if axis in axesToShow:
                        if not self._compassGeode.containsDrawable(drawable):
                            self._compassGeode.addDrawable(drawable)
                    else:
                        if self._compassGeode.containsDrawable(drawable):
                            self._compassGeode.removeDrawable(drawable)
    
    
    def _updateCompass(self):
        if self.viewDimensions == 2:
            if self.orthoViewPlane == 'xy':
                rotation = osg.Quat(0, osg.Vec3(1, 0, 0))
            elif self.orthoViewPlane == 'xz':
                rotation = osg.Quat(-pi / 2.0, osg.Vec3(1, 0, 0))
            elif self.orthoViewPlane == 'zy':
                rotation = osg.Quat(pi / 2.0, osg.Vec3(0, 1, 0))
        else:
            rotation = self.trackball.getRotation().inverse()
            
        self.compassTransform.setMatrix(osg.Matrixd.rotate(rotation))        
    
    
    def setUseStereo(self, useStereo):
        """
        Set whether the visualization should be viewable through red/blue 3D glasses.
        
        The argument should be either True or False.
        """
        
        settings = self.viewer.getDisplaySettings()
        
        if useStereo:
            if settings is None:
                settings = osg.DisplaySettings()
                self.viewer.setDisplaySettings(settings)
            settings.setStereo(True)
            settings.setStereoMode(osg.DisplaySettings.ANAGLYPHIC)
        elif settings is not None:
            settings.setStereo(False)
        
        self.Refresh()
    
    
    def _resetView(self):
        if self.viewDimensions == 2:
            width, height = self.GetClientSize()
            # TODO: if self.orthoZoom just changed to 0 then width and height will be too small by assuming the scroll bars are still there.
            zoom = 2.0 ** (self.orthoZoom / 10.0)
            self.viewer.getCamera().setProjectionMatrixAsOrtho2D(self.orthoCenter[0] - (width + 20) * self.zoomScale / 2.0 / zoom, 
                                                                 self.orthoCenter[0] + (width + 20) * self.zoomScale / 2.0 / zoom, 
                                                                 self.orthoCenter[1] - (height + 20) * self.zoomScale / 2.0 / zoom, 
                                                                 self.orthoCenter[1] + (height + 20) * self.zoomScale / 2.0 / zoom)
            if self.orthoViewPlane == 'xy':
                self.viewer.getCamera().setViewMatrix(osg.Matrixd.translate(osg.Vec3d(0.0, 0.0, self.visiblesMin[2] - 2.0)))
            elif self.orthoViewPlane == 'xz':
                self.viewer.getCamera().setViewMatrix(osg.Matrixd.translate(osg.Vec3d(0.0, self.visiblesMax[1] + 2.0, 0.0)) * \
                                                      osg.Matrixd.rotate(osg.Quat(pi / -2.0, osg.Vec3d(1, 0, 0))))
            elif self.orthoViewPlane == 'zy':
                self.viewer.getCamera().setViewMatrix(osg.Matrixd.translate(osg.Vec3d(self.visiblesMax[0] + 2.0, 0.0, 0.0)) * \
                                                      osg.Matrixd.rotate(osg.Quat(pi / 2.0, osg.Vec3d(0, 1, 0))))
            self.SetScrollbar(wx.HORIZONTAL, (self.orthoCenter[0] - self.visiblesMin[0]) / self.visiblesSize[0] * width - width / zoom / 2.0, width / zoom, width, True)
            self.SetScrollbar(wx.VERTICAL, (self.visiblesMax[1] - self.orthoCenter[1]) / self.visiblesSize[1] * height - height / zoom / 2.0, height / zoom, height, True)
    
    
    def computeVisiblesBound(self):
        if self._recomputeBounds:
            # This:
            #     boundingSphere = node.getBound()
            #     sphereCenter = boundingSphere.center()
            # computes a screwy center.  Because there's no camera?
            # Manually compute the bounding box instead.
            # TODO: figure out how to let the faster C++ code do this
            origBounds = (self.visiblesCenter, self.visiblesSize)
            self.visiblesMin = [100000, 100000, 100000]
            self.visiblesMax = [-100000, -100000, -100000]
            for visibles in self.visibles.values():
                for visible in visibles:
                    x, y, z = visible.worldPosition()
                    w, h, d = visible.worldSize()
                    if x - w / 2.0 < self.visiblesMin[0]:
                        self.visiblesMin[0] = x - w / 2.0
                    if x + w / 2.0 > self.visiblesMax[0]:
                        self.visiblesMax[0] = x + w / 2.0
                    if y - h / 2.0 < self.visiblesMin[1]:
                        self.visiblesMin[1] = y - h / 2.0
                    if y + h / 2.0 > self.visiblesMax[1]:
                        self.visiblesMax[1] = y + h / 2.0
                    if z - d / 2.0 < self.visiblesMin[2]:
                        self.visiblesMin[2] = z - d / 2.0
                    if z + d / 2.0 > self.visiblesMax[2]:
                        self.visiblesMax[2] = z + d / 2.0
                    if visible.isPath():
                        for x, y, z in visible.pathMidPoints():
                            if x < self.visiblesMin[0]:
                                self.visiblesMin[0] = x
                            if x > self.visiblesMax[0]:
                                self.visiblesMax[0] = x
                            if y < self.visiblesMin[1]:
                                self.visiblesMin[1] = y
                            if y > self.visiblesMax[1]:
                                self.visiblesMax[1] = y
                            if z < self.visiblesMin[2]:
                                self.visiblesMin[2] = z
                            if z > self.visiblesMax[2]:
                                self.visiblesMax[2] = z
            self.visiblesCenter = ((self.visiblesMin[0] + self.visiblesMax[0]) / 2.0, (self.visiblesMin[1] + self.visiblesMax[1]) / 2.0, (self.visiblesMin[2] + self.visiblesMax[2]) / 2.0)
            self.visiblesSize = (self.visiblesMax[0] - self.visiblesMin[0], self.visiblesMax[1] - self.visiblesMin[1], self.visiblesMax[2] - self.visiblesMin[2])
            self._recomputeBounds = False
            
            if origBounds != (self.visiblesCenter, self.visiblesSize):
                # The size of the glow effect is based on the bounding box of the whole display.
                # This is expensive so only do it if something actually changed.
                for visibles in self.visibles.itervalues():
                    for visible in visibles:
                        visible._updateGlow()
        
        width, height = self.GetClientSize()
        xZoom = self.visiblesSize[self.orthoXPlane] / (width - 10.0)
        yZoom = self.visiblesSize[self.orthoYPlane] / (height - 10.0)
        if xZoom > yZoom:
            self.zoomScale = xZoom
        else:
            self.zoomScale = yZoom
    
    
    def centerView(self):
        """
        Deprecated, use resetView or zoomToFit instead.
        """
        
        if self.viewDimensions == 2:
            self.zoomToFit()
        else:
            self.resetView()
    
    
    def resetView(self):
        """
        Reset the view point of the 3D view to the default distance and rotation.
        """
        
        if self.viewDimensions == 3:
            self.trackball.setNode(self.rootNode)
            self.trackball.computeHomePosition()
            self.viewer.home()
            self.trackball.setRotation(osg.Quat(0, 0, 0, 1))
            self.Refresh()
    
    
    def zoomToFit(self):
        """
        Change the magnification of the 2D view so that all objects are visible.
        """
        
        if self.viewDimensions == 2:
            self.computeVisiblesBound()
            self.orthoCenter = (self.visiblesCenter[self.orthoXPlane], self.visiblesCenter[self.orthoYPlane])
            self.orthoZoom = 0
            self._resetView()
            self.Refresh()
        
        #osgDB.writeNodeFile(self.rootNode, "test.osg");
    
    
    def zoomToSelection(self):
        """
        Change the magnification of the 2D view so that all selected or highlighted objects are visible.
        """
        
        minX, maxX = (1e300, -1e300)
        minY, maxY = (1e300, -1e300)
        for visible in self.selectedVisibles.union(self.highlightedVisibles).union(self.animatedVisibles):
            worldPos = visible.worldPosition()
            worldSize = visible.worldSize()
            minX = min(minX, worldPos[0] - worldSize[0] / 2.0) 
            maxX = max(maxX, worldPos[0] + worldSize[0] / 2.0) 
            minY = min(minY, worldPos[1] - worldSize[1] / 2.0) 
            maxY = max(maxY, worldPos[1] + worldSize[1] / 2.0) 
        self.orthoCenter = ((minX + maxX) / 2.0, (minY + maxY) / 2.0)
        width, height = self.GetClientSize()
        xZoom = (width - 20) * self.zoomScale / (maxX - minX)
        yZoom = (height - 20) * self.zoomScale / (maxY - minY)
        self.orthoZoom = log(min(xZoom, yZoom), 2) * 10.0
        self._resetView()
        self.Refresh()
    
    
    def _zoom(self, amount):
        if self.viewDimensions == 2:
            self.orthoZoom += 10 * amount
            if self.orthoZoom < 0:
                self.orthoZoom = 0
            
            # Alter orthoCenter if the new zoom level will cause any visibles to fall outside the reach of the scroll bars.
            width, height = self.GetClientSize()
            zoom = 2 ** (self.orthoZoom / 10.0)
            horScrollPos = (self.orthoCenter[0] - self.visiblesMin[0]) / self.visiblesSize[0] * width - width / zoom / 2.0
            maxHorScrollPos = width - width / zoom
            if horScrollPos < 0.0:
                self.orthoCenter = ((width / zoom / 2.0) / width * self.visiblesSize[0] + self.visiblesMin[0], self.orthoCenter[1])
            elif horScrollPos > maxHorScrollPos:
                self.orthoCenter = ((maxHorScrollPos + width / zoom / 2.0) / width * self.visiblesSize[0] + self.visiblesMin[0], self.orthoCenter[1])
            vertScrollPos = (self.visiblesMax[1] - self.orthoCenter[1]) / self.visiblesSize[1] * height - height / zoom / 2.0
            maxVertScrollPos = height - height / zoom
            if vertScrollPos < 0.0:
                self.orthoCenter = (self.orthoCenter[0], self.visiblesMax[1] - (height / zoom / 2.0) * self.visiblesSize[1] / height)
            elif vertScrollPos > maxVertScrollPos:
                self.orthoCenter = (self.orthoCenter[0], self.visiblesMax[1] - (maxVertScrollPos + height / zoom / 2.0) * self.visiblesSize[1] / height)
        elif self.viewDimensions == 3:
            self.computeVisiblesBound()
            self.trackball.setDistance(self.trackball.getDistance() - max(self.visiblesSize) * 0.2 * amount)
        self._resetView()
        self.Refresh()
    
    
    def zoomIn(self):
        """
        Increase the magnification of the view.
        """
        
        self._zoom(1.0)
    
    
    def zoomOut(self):
        """
        Decrease the magnification of the view.
        """
        
        self._zoom(-1.0)
    
    
    def onScroll(self, event):
        width, height = self.GetClientSize()
        zoom = 2 ** (self.orthoZoom / 10.0)
        if event.GetOrientation() == wx.HORIZONTAL:
            # Reverse the calculation in _resetView():
            # pos = (self.orthoCenter[0] - self.visiblesMin[0]) / self.visiblesSize[0] * width - width / zoom / 2
            # pos + width / zoom / 2 = (self.orthoCenter[0] - self.visiblesMin[0]) / self.visiblesSize[0] * width
            # (pos + width / zoom / 2) * self.visiblesSize[0] / width = self.orthoCenter[0] - self.visiblesMin[0]
            self.orthoCenter = ((event.GetPosition() + width / zoom / 2.0) / width * self.visiblesSize[0] + self.visiblesMin[0], self.orthoCenter[1])
        else:
            # Reverse the calculation in _resetView():
            # pos = (self.visiblesMax[1] - self.orthoCenter[1]) / self.visiblesSize[1] * height - height / zoom / 2
            # pos + height / zoom / 2 = (self.visiblesMax[1] - self.orthoCenter[1]) / self.visiblesSize[1] * height
            # (pos + height / zoom / 2) * self.visiblesSize[1] / height = self.visiblesMax[1] - self.orthoCenter[1]
            self.orthoCenter = (self.orthoCenter[0], self.visiblesMax[1] - (event.GetPosition() + height / zoom / 2.0) * self.visiblesSize[1] / height)
        self._resetView()
        self.Refresh()
    
    
    def setNavigationMode(self, mode):
        if mode != self._navigationMode:
            self._navigationMode = mode
    
    
    def navigationMode(self):
        return self._navigationMode
    
    
    def shiftView(self, dx, dy):
        if self.viewDimensions == 3:
            self._shiftView(dx, dy)
        elif self.orthoZoom > 0:
            # At least on the Mac the scroll bars don't update if set immediately.  Instead, queue the update to happen after all current events have cleared.
            wx.CallAfter(self._shiftView, dx, dy)
            
    
    def _shiftView(self, dx, dy):
        width, height = self.GetClientSize()
        if self.viewDimensions == 2:
            # Convert screen coordinates to world coordinates.
            dx = -dx / (width - 20.0) * width
            dy = -dy / (height - 20.0) * height
            zoom = 2.0 ** (self.orthoZoom / 10.0)
            self.orthoCenter = (self.orthoCenter[0] + dx * self.zoomScale / zoom, self.orthoCenter[1] + dy * self.zoomScale / zoom)
            self._resetView()
        else:
            # Mimic the panning code from OSG's trackball manipulator (in TrackballManipulator::calcMovement()).
            # It expects dx and dy to be normalized (-1.0 ... 1.0).
            dx /= width / 2.0
            dy /= height / 2.0
            scale = -0.3 * self.trackball.getDistance()
            rotation = osg.Matrixd()
            rotation.makeRotate(self.trackball.getRotation())
            shiftVector = osg.Vec3d(dx * scale, dy * scale, 0.0)
            center = self.trackball.getCenter()
            center += rotation.preMult(shiftVector)
            self.trackball.setCenter(center)
        self.Refresh()
   
   
    def setBackgroundColor(self, color):
        """
        Set the background color of the entire display.
        
        The color argument should be a tuple or list of four values between 0.0 and 1.0 indicating the red, green, blue and alpha values of the color.  For example:
        
        * (0.0, 0.0, 0.0, 1.0) -> black
        * (1.0, 0.0, 0.0, 1.0) -> red
        * (0.0, 1.0, 0.0, 1.0) -> green
        * (0.0, 0.0, 1.0, 1.0) -> blue
        * (1.0, 1.0, 1.0, 1.0) -> white
        * (1.0, 1.0, 1.0, 0.0) -> white, but clear if saved as image
        """
        
        if not isinstance(color, (list, tuple)) or len(color) != 4:
            raise ValueError, 'The color passed to setBackgroundColor() must be a tuple or list of four numbers.'
        for colorComponent in color:
            if not isinstance(colorComponent, (int, float)) or colorComponent < 0.0 or colorComponent > 1.0:
                raise ValueError, 'The components of the color passed to setBackgroundColor() must all be numbers between 0.0 and 1.0, inclusive.'
        
        if color != self.backgroundColor:
            self.viewer.getCamera().setClearColor(osg.Vec4f(color[0], color[1], color[2], color[3]))
            self.backgroundColor = color
            dispatcher.send(('set', 'backgroundColor'), self)
    
    
    def setUseMouseOverSelecting(self, useIt):
        """
        Set whether objects should be automatically selected as the mouse passes over them.
        
        This setting is ignored if a manual selection is already in place.
        """
         
        if useIt != self._useMouseOverSelecting:
            self._useMouseOverSelecting = useIt
            dispatcher.send(('set', 'useMouseOverSelecting'), self)
    
    
    def useMouseOverSelecting(self):
        return self._useMouseOverSelecting
    
        
    def onMouseEvent(self, event):
        if event.ButtonDown():
            self.selectionShouldExtend = event.CmdDown()
            self.findShortestPath = event.ShiftDown()
            self.graphicsWindow.getEventQueue().mouseButtonPress(event.GetX(), event.GetY(), event.GetButton())
        elif event.ButtonUp():
            self.graphicsWindow.getEventQueue().mouseButtonRelease(event.GetX(), event.GetY(), event.GetButton())
        elif event.Dragging():
            self.graphicsWindow.getEventQueue().mouseMotion(event.GetX(), event.GetY())
        elif event.Moving() and ((self._useMouseOverSelecting and self.hoverSelect) or self._visibleBeingAdded is not None):
            if self._visibleBeingAdded is None:
                self.hoverSelecting = True
            self.graphicsWindow.getEventQueue().mouseButtonPress(event.GetX(), event.GetY(), wx.MOUSE_BTN_LEFT)
            self.graphicsWindow.getEventQueue().mouseButtonRelease(event.GetX(), event.GetY(), wx.MOUSE_BTN_LEFT)
        self.Refresh()
        event.Skip()
    
    
    def onMouseWheel(self, event):
        if event.ShiftDown():
            self._zoom(event.GetWheelRotation() / 100.0 * self.scrollWheelScale)
        else:
            self._zoom(event.GetWheelRotation() / 10.0 * self.scrollWheelScale)
        event.Skip()
    
    
    def onEraseBackground(self, event):
        pass
    
    
    def onSize(self, event):
        w, h = self.GetClientSize()
        
        if self.IsShownOnScreen():
            self.SetCurrent(self.glContext)

            if self.graphicsWindow.valid():
                self.graphicsWindow.getEventQueue().windowResize(0, 0, w, h)
                self.graphicsWindow.resized(0, 0, w, h)
            
            self._resetView()
        
        event.Skip()
    
    
    def onPaint(self, event_):
        wx.PaintDC(self)
        
        if self.IsShownOnScreen():  #self.GetContext() != 0 and self.graphicsWindow.valid():
            self.SetCurrent(self.glContext)
            self.viewer.frame()
            self.SwapBuffers()
     
    
    def onAnimate(self, event):
        self.Refresh()
        event.Skip()
   
    
    def _getConvertedKeyCode(self, event):
        key = event.GetKeyCode()
        if key >= ord('A') and key <= ord('Z'):
            if not event.ShiftDown():
                key += 32
        return key
    
    
    def onKeyDown(self, event):
        key = self._getConvertedKeyCode(event)
        self.graphicsWindow.getEventQueue().keyPress(key)
        event.Skip()
    
    
    def onKeyUp(self, event):
        key = self._getConvertedKeyCode(event)
        self.graphicsWindow.getEventQueue().keyRelease(key)
        event.Skip()
    
    
    def visiblesForObject(self, networkObject):
        """
        Return the list of :class:`visible proxies <Display.Visible.Visible>` for the given object or an empty list if the object is not visualized.
        """
        
        return list(self.visibles[networkObject.networkId]) if networkObject and networkObject.networkId in self.visibles else []
    
    
    def Refresh(self, *args, **keywordArgs):    # pylint: disable=W0221
        if not self._suppressRefresh:
            if self.compassCamera:
                self._updateCompass()
            wx.glcanvas.GLCanvas.Refresh(self, *args, **keywordArgs)
    
    
    def _visibleChanged(self, signal):
        if signal[1] in ('position', 'size', 'rotation', 'path', 'pathMidPoints'):
            self._recomputeBounds = True
            if not self._recomputeBoundsScheduled:
                # Trigger a single recompute of the visibles bounds this pass through the event loop no matter how many visibles are updated.
                wx.CallAfter(self._resetViewAfterVisiblesChanged)
                self._recomputeBoundsScheduled = True
        elif signal[1] in ('positionIsFixed', 'sizeIsFixed') and any(self.selectedVisibles):
            self._clearDragger()
            visible = list(self.selectedVisibles)[0]
            if visible._isDraggable():
                self._addDragger(visible)
        
        self.Refresh()
        
        if signal[1] not in ('glowColor'):
            self.GetTopLevelParent().setModified(True)
    
    
    def _resetViewAfterVisiblesChanged(self):
        self.computeVisiblesBound()
        if self.orthoZoom == 0:
            self.orthoCenter = (self.visiblesCenter[self.orthoXPlane], self.visiblesCenter[self.orthoYPlane])
        self._resetView()
        self._recomputeBoundsScheduled = False
    
    
    def addVisible(self, visible, parentVisible = None):
        clientId = -1 if visible.client == None else visible.client.networkId
        if clientId in self.visibles:
            self.visibles[clientId].append(visible)
        else:
            self.visibles[clientId] = [visible]
        self._visibleIds[visible.displayId] = visible
        if parentVisible is None:
            self.rootNode.addChild(visible.sgNode)
        else:
            parentVisible.addChildVisible(visible)
        dispatcher.connect(self._visibleChanged, dispatcher.Any, visible)
    
    
    def visibleWithId(self, visibleId):
        if visibleId in self._visibleIds:
            return self._visibleIds[visibleId]
        else:
            return None
    
    
    def close(self):
        self._closing = True
        self.setNetwork(None)
        
    
    def removeVisible(self, visible):
        """
        Remove the indicated :class:`visual proxy <Display.Visible.Visible>` from the visualization.
        
        If the object has any nested objects or connections then they will be removed as well. 
        """
        
        if visible.displayId not in self._visibleIds:
            raise ValueError, 'The visible passed to removeVisible() is not part of the display.'
        
        # Remove any child visibles before removing this one.
        for childVisible in list(visible.children):
            self.removeVisible(childVisible)
        
        # Remove any dependent visibles before removing this one.  (like an arborization before its region) 
        for dependentVisible in list(visible.dependentVisibles):
            self.removeVisible(dependentVisible)
        
        # Remove the visible from the current selection if needed.
        if visible in self.selectedVisibles:
            self.selectVisibles([visible], extend = True)
        
        # Remove the visible's node from the scene graph.
        if visible.parent:
            visible.parent.removeChildVisible(visible)
        self.rootNode.removeChild(visible.sgNode)
        
        # Remove any dependencies.
        dispatcher.disconnect(self._visibleChanged, dispatcher.Any, visible)
        if visible.isPath():
            visible.setPathEndPoints(None, None)
        
        # Remove the visible from self._visibleIds and self.visibles.
        del self._visibleIds[visible.displayId]
        clientId = -1 if visible.client == None else visible.client.networkId
        visibles = self.visibles[clientId]
        visibles.remove(visible)
        if not any(visibles):
            del self.visibles[clientId]
        
        visible.display = None
        
        self.Refresh()
    
    
    def visualizeObject(self, networkObject = None, orphanClass = None, **keywordArgs):
        """
        Create a visual representation of the :class:`object <network.object.Object>`.
        
        If you want to have a purely visual object that does not represent any object in the biological network then pass None.
        
        You can customize the visualization of the object by passing additional parameters.  The parameters that would be used for automatic visualization can be obtained by calling :meth:`defaultVisualizationParams() <network.object.Object.defaultVisualizationParams>` on the object.
        
        Returns the :class:`visible proxy <Display.Visible.Visible>` of the object.
        """
        
        # TODO: document the list of possible params somewhere. 
        # TODO: replace this whole block with display rules.
        
        visible = Visible(self, networkObject)
        
        isStimulus = False
        
        # Start with the default params for this object, object class or dummy object and override with any supplied params.
        if orphanClass:
            visible.setOrphanClass(orphanClass)
            params = orphanClass._defaultVisualizationParams()
            if orphanClass == Stimulus:
                edgeVisible = visible
                nodeVisible = Visible(self, None)
                target = keywordArgs['target']
                del keywordArgs['target']
                isStimulus = True
        elif networkObject:
            params = networkObject.defaultVisualizationParams()
        else:
            params = Object._defaultVisualizationParams()
        for key, value in keywordArgs.iteritems():
            params[key] = value
            
        if isinstance(networkObject, Arborization):
            dispatcher.connect(self._arborizationChangedFlow, ('set', 'sendsOutput'), networkObject)
            dispatcher.connect(self._arborizationChangedFlow, ('set', 'receivesInput'), networkObject)
        elif isinstance(networkObject, Pathway):
            dispatcher.connect(self._pathwayChangedFlow, ('set', 'region1Projects'), networkObject)
            dispatcher.connect(self._pathwayChangedFlow, ('set', 'region2Projects'), networkObject)
        elif isinstance(networkObject, Stimulus):
            edgeVisible = visible
            nodeVisible = Visible(self, networkObject)
            target = networkObject.target
            isStimulus = True
        
        if 'color' in params:
            visible.setColor(params['color'])
        if 'shape' in params:
            if isinstance(params['shape'], str):
                shape = neuroptikon.shapeClass(params['shape'])()
            elif isinstance(params['shape'], type(self.__class__)):
                shape = params['shape']()
            else:
                shape = params['shape']
            visible.setShape(shape)
        if 'opacity' in params:
            visible.setOpacity(params['opacity'])
            if isStimulus:
                nodeVisible.setOpacity(params['opacity'])
        if 'sizeIsAbsolute' in params:
            visible.setSizeIsAbsolute(params['sizeIsAbsolute'])
        if 'texture' in params:
            visible.setTexture(params['texture'])
        if 'textureScale' in params:
            visible.setTextureScale(params['textureScale'])
        if 'weight' in params:
            visible.setWeight(params['weight'])
        
        # Label and position are applied to the node visible of a stimulus.
        if isStimulus:
            visible = nodeVisible
        
        if 'size' in params:
            visible.setSize(params['size'])
        if 'label' in params:
            visible.setLabel(params['label'])
        if 'labelColor' in params:
            visible.setLabelColor(params['labelColor'])
        if 'labelPosition' in params:
            visible.setLabelPosition(params['labelPosition'])
        if 'position' in params:
            visible.setPosition(params['position'])
        if 'positionIsFixed' in params:
            visible.setPositionIsFixed(params['positionIsFixed'])
        if 'rotation' in params:
            visible.setRotation(params['rotation'])
        
        if 'arrangedAxis' in params:
            visible.setArrangedAxis(params['arrangedAxis'])
        if 'arrangedSpacing' in params:
            visible.setArrangedSpacing(params['arrangedSpacing'])
        if 'arrangedWeight' in params:
            visible.setArrangedWeight(params['arrangedWeight'])
        
        if 'path' in params:
            params['pathMidPoints'] = params['path']
            del params['path']
        pathStart, pathEnd = params.get('pathEndPoints', (None, None))
        pathFlowsTo = params.get('flowTo', None)
        pathFlowsFrom = params.get('flowFrom', None)
        flowToColor = params.get('flowToColor', None)
        flowFromColor = params.get('flowFromColor', None)
        
        parentObject = params.get('parent', None)
        if isinstance(parentObject, Object):
            parentVisibles = self.visiblesForObject(parentObject)
            parentVisible = parentVisibles[0] if len(parentVisibles) == 1 else None
        else:
            parentVisible = parentObject
        self.addVisible(visible, parentVisible)
        
        if isStimulus:
            if isinstance(target, Object):
                targetVisibles = self.visiblesForObject(target)
                if len(targetVisibles) == 1:
                    target = targetVisibles[0]
            if target is not None:
                edgeVisible.setPathEndPoints(nodeVisible, target)
                edgeVisible.setPathIsFixed(True)
                edgeVisible.setFlowTo(True)
                if flowToColor:
                    edgeVisible.setFlowToColor(flowToColor)
                if self._showFlow:
                    edgeVisible.animateFlow()
            nodeVisible.setShape(None)
            edgeVisible.setPositionIsFixed(True)
            self.addVisible(edgeVisible)
        else:
            if pathStart is not None and pathEnd is not None:
                # The path start and end can either be objects or visibles.
                if isinstance(pathStart, Object):
                    pathStartVisibles = self.visiblesForObject(pathStart)
                else:
                    pathStartVisibles = [pathStart]
                if isinstance(pathEnd, Object):
                    pathEndVisibles = self.visiblesForObject(pathEnd)
                else:
                    pathEndVisibles = [pathEnd]
                if len(pathStartVisibles) == 1 and len(pathEndVisibles) == 1:
                    pathStartVisible = pathStartVisibles[0]
#                    if pathStartVisible.isPath():
#                        pathStartVisible = pathStartVisible._pathEnd
                    pathEndVisible = pathEndVisibles[0]
#                    if pathEndVisible.isPath():
#                        pathEndVisible = pathEndVisible._pathStart 
                    visible.setPathEndPoints(pathStartVisible, pathEndVisible)
                    visible.setPathMidPoints(params.get('pathMidPoints', []))
                    visible.setPathIsFixed(params.get('pathIsFixed', None))
                    visible.setFlowTo(pathFlowsTo)
                    if flowToColor:
                        visible.setFlowToColor(flowToColor)
                    visible.setFlowFrom(pathFlowsFrom)
                    if flowFromColor:
                        visible.setFlowFromColor(flowFromColor)
                    if self._showFlow:
                        visible.animateFlow()
            
            childObjects = params.get('children', [])
            for childObject in childObjects:
                subVisibles = self.visiblesForObject(childObject)
                if len(subVisibles) == 1:
                    # TODO: what if the subVisible is already a child?
                    self.rootNode.removeChild(subVisibles[0].sgNode)
                    visible.addChildVisible(subVisibles[0])
        
        # The visible may be outside of the previously computed bounds.
        _recomputeBounds = True

        return visible
    
    
    def removeObject(self, networkObject):
        """
        Remove the indicated :class:`network object <network.object.Object>` from the visualization.
        
        If the object has any nested objects or connections then they will be removed as well. 
        """
        
        while any(self.visiblesForObject(networkObject)):
            self.removeVisible(self.visiblesForObject(networkObject)[0])
    
    
    def clear(self):
        """
        Remove every :class:`network object <network.object.Object>` from the visualization.
        """
        
        while any(self.visibles):
            self.removeVisible(self.visibles.values()[0][0])
    
    
    def _arborizationChangedFlow(self, sender):
        arborizationVis = self.visiblesForObject(sender)
        if len(arborizationVis) == 1:
            arborizationVis[0].setFlowTo(sender.sendsOutput)
            arborizationVis[0].setFlowFrom(sender.receivesInput)
    
    
    def _pathwayChangedFlow(self, sender):
        pathwayVis = self.visiblesForObject(sender)
        if len(pathwayVis) == 1:
            pathwayVis[0].setFlowTo(sender.region1Projects)
            pathwayVis[0].setFlowFrom(sender.region2Projects)
    
        
    def setNetwork(self, network):
        if network != self.network:
            if self.network != None:
                self.network.removeDisplay(self)
                
                # TBD: are there situations where you wouldn't want to clear anonymous visibles?
                self.clear()
                
                # TODO: anything else?
            
            self.network = network
            
            if network is not None:
                self.network.addDisplay(self)
                
                if self.autoVisualize:
                    for networkObject in network.objects:
                        if not networkObject.parentObject():
                            self.visualizeObject(networkObject)
                
                dispatcher.connect(receiver=self._networkChanged, signal=dispatcher.Any, sender=self.network)
            
            dispatcher.send(('set', 'network'), self)
        
    
    
    def _networkChanged(self, affectedObjects=None, **arguments):
        signal = arguments['signal']
        if signal == 'addition' and self.autoVisualize:
            for addedObject in affectedObjects:
                if not addedObject.parentObject():
                    self.visualizeObject(addedObject)
            self.Refresh()
        elif signal == 'deletion':
            for removedObject in affectedObjects:
                self.removeObject(removedObject)
        else:
            pass    # TODO: anything?
        self.GetTopLevelParent().setModified(True)
    
    
    def _neuronRegionChanged(self, sender):
        # TODO: untested method
        visible = self.visiblesForObject(sender)
        if visible.parent is not None:
            visible.parent.removeChildVisible(visible)
        if sender.region is not None:
            newParent = self.visiblesForObject(sender.region)
            if newParent is not None:
                newParent.addChildVisible(visible)
    
    
    def setShowRegionNames(self, show):
        """
        Set whether the names of regions should be shown by default in the visualization.
        """
        
        if show != self._showRegionNames:
            self._showRegionNames = show
            dispatcher.send(('set', 'showRegionNames'), self)
            self.Refresh()
    
    
    def showRegionNames(self):
        """
        Return whether the names of regions should be shown by default in the visualization.
        """
        
        return self._showRegionNames
    
    
    def setShowNeuronNames(self, show):
        """
        Set whether the names of neurons should be shown by default in the visualization.
        """
        
        if show != self._showNeuronNames:
            self._showNeuronNames = show
            dispatcher.send(('set', 'showNeuronNames'), self)
            self.Refresh()
    
    
    def showNeuronNames(self):
        """
        Return whether the names of neurons should be shown by default in the visualization.
        """
        
        return self._showNeuronNames
    
    
    def setLabelsFloatOnTop(self, floatLabels):
        """
        Set whether labels should be rendered on top of all other objects in the visualization.
        """
        
        if floatLabels != self._labelsFloatOnTop:
            self._labelsFloatOnTop = floatLabels
            dispatcher.send(('set', 'labelsFloatOnTop'), self)
            self.Refresh()
    
    
    def labelsFloatOnTop(self):
        """
        Return whether labels should be rendered on top of all other objects in the visualization.
        """
        
        return self._labelsFloatOnTop
    
    
    def setShowFlow(self, showFlow):
        """
        Set whether the flow of information should be shown for all objects in the visualization.
        """
        
        if showFlow != self._showFlow:
            self._showFlow = showFlow
            dispatcher.send(('set', 'showFlow'), self)
    
    
    def showFlow(self):
        """
        Return whether the flow of information should be shown for all objects in the visualization.
        """
        
        return self._showFlow
    
    
    def setSelectionHighlightDepth(self, depth):
        """
        Set how far away objects connected to the current selection should be highlighted.
        """
        
        if depth != self._selectionHighlightDepth:
            self._selectionHighlightDepth = depth
            self._onSelectionOrShowFlowChanged()
            dispatcher.send(('set', 'selectionHighlightDepth'), self)
    
    
    def selectionHighlightDepth(self):
        """
        Return how far away objects connected to the current selection should be highlighted.
        """
        
        return self._selectionHighlightDepth
    
    
    def setHighlightOnlyWithinSelection(self, flag):
        """
        Set whether connections to objects outside of the selection should be highlighted when more than one object is selected.
        """
        
        if flag != self._highlightOnlyWithinSelection:
            self._highlightOnlyWithinSelection = flag
            self._onSelectionOrShowFlowChanged()
            dispatcher.send(('set', 'highlightOnlyWithinSelection'), self)
    
    
    def highlightOnlyWithinSelection(self):
        """
        Return whether connections to objects outside of the selection will be highlighted when more than one object is selected.
        """
        
        return self._highlightOnlyWithinSelection
    
    
    def setUseGhosts(self, useGhosts):
        """
        Set whether unselected objects should be dimmed in the visualization.
        """
        
        if useGhosts != self._useGhosts:
            self._useGhosts = useGhosts
            dispatcher.send(('set', 'useGhosts'), self)
            self.Refresh()
    
    
    def useGhosts(self):
        """
        Return whether unselected objects should be dimmed in the visualization.
        """
        
        return self._useGhosts
    
    
    def setGhostingOpacity(self, opacity):
        """
        Set the opacity to be used for unselected objects when ghosting is enabled.
        
        The opacity must be between 0.0 and 1.0, inclusive.
        """
        
        if not isinstance(opacity, (float, int)):
            raise TypeError, 'The value passed to setGhostingOpacity() must be a number.'
        elif opacity < 0.0 or opacity > 1.0:
            raise ValueError, 'The value passed to setGhostingOpacity() must be between 0.0 and 1.0, inclusive.'
        
        if opacity != self._ghostingOpacity:
            self._ghostingOpacity = opacity
            dispatcher.send(('set', 'ghostingOpacity'), self)
            self.Refresh()
    
    
    def ghostingOpacity(self):
        """
        Return the opacity to be used for unselected objects when ghosting is enabled.
        """
        
        return self._ghostingOpacity
    
    
    def setLabel(self, networkObject, label):
        """
        Set the label that adorns the visualization of the indicated :class:`network object <network.object.Object>`.
        
        The label argument should be a string value or None to indicate that the object's abbreviation or name should be used.  To have no label pass an empty string.
        """
        
        if not isinstance(networkObject, (Object, Visible)) or (isinstance(networkObject, Object) and networkObject.network != self.network) or (isinstance(networkObject, Visible) and networkObject.display != self):
            raise ValueError, 'The object argument passed to setLabel() must be an object from the network being visualized by this display.'
        if not isinstance(label, (str, type(None))):
            raise TypeError, 'The label argument passed to setLabel() must be a string or None.'
        
        visible = None
        if isinstance(networkObject, Object):
            visibles = self.visiblesForObject(networkObject)
            if len(visibles) == 1:
                visible = visibles[0]
            elif isinstance(networkObject, Stimulus):
                visible = visibles[0 if visibles[1].isPath() else 1]
        else:
            visible = networkObject
        if visible is not None:
            visible.setLabel(label)
    
    
    def setLabelColor(self, networkObject, color):
        """
        Set the color of the label of the indicated :class:`network object <network.object.Object>`.
         
        The color argument should be a tuple or list of three values between 0.0 and 1.0 indicating the red, green and blue values of the color.  For example:
        
        * (0.0, 0.0, 0.0) -> black
        * (1.0, 0.0, 0.0) -> red
        * (0.0, 1.0, 0.0) -> green
        * (0.0, 0.0, 1.0) -> blue
        * (1.0, 1.0, 1.0) -> white
        
        Any alpha value should be set independently using :meth:`setVisibleOpacity <Display.Display.Display.setVisibleOpacity>`.
        """
        
        if not isinstance(networkObject, (Object, Visible)) or (isinstance(networkObject, Object) and networkObject.network != self.network) or (isinstance(networkObject, Visible) and networkObject.display != self):
            raise ValueError, 'The object argument passed to setLabelColor() must be an object from the network being visualized by this display .'
        if (not isinstance(color, (tuple, list)) or len(color) != 3 or 
            not isinstance(color[0], (int, float)) or color[0] < 0.0 or color[0] > 1.0 or 
            not isinstance(color[1], (int, float)) or color[1] < 0.0 or color[1] > 1.0 or 
            not isinstance(color[2], (int, float)) or color[2] < 0.0 or color[2] > 1.0):
            raise ValueError, 'The color argument passed to setLabelColor() should be a tuple or list of three integer or floating point values between 0.0 and 1.0, inclusively.'
        
        visible = None
        if isinstance(networkObject, Object):
            visibles = self.visiblesForObject(networkObject)
            if len(visibles) == 1:
                visible = visibles[0]
            elif isinstance(networkObject, Stimulus):
                visible = visibles[0 if visibles[1].isPath() else 1]
        else:
            visible = networkObject
        if visible is not None:
            visible.setLabelColor(color)
    
    
    def setLabelPosition(self, networkObject, position):
        """
        Set the position of the label that adorns the visualization of the indicated :class:`network object <network.object.Object>`.
        
        The position argument should be a tuple or list indicating the position of the label.  The coordinates are local to the object with is usually a unit square centered at (0.0, 0.0).  For example:
        (0.0, 0.0) -> label at center of object
        (-0.5, -0.5) -> label at lower left corner of object
        (0.0, 0.5) -> label centered at top of object
        """
        
        if not isinstance(networkObject, (Object, Visible)) or (isinstance(networkObject, Object) and networkObject.network != self.network) or (isinstance(networkObject, Visible) and networkObject.display != self):
            raise ValueError, 'The object argument passed to setLabelPosition() must be an object from the network being visualized by this display .'
        if not isinstance(position, (tuple, list)):
            raise TypeError, 'The position argument passed to setLabelPosition() must be a tuple or list of numbers.'
        for dim in position:
            if not isinstance(dim, (int, float)):
                raise TypeError, 'The components of the position argument passed to setLabelPosition() must be numbers.'
        
        visible = None
        if isinstance(networkObject, Object):
            visibles = self.visiblesForObject(networkObject)
            if len(visibles) == 1:
                visible = visibles[0]
            elif isinstance(networkObject, Stimulus):
                visible = visibles[0 if visibles[1].isPath() else 1]
        else:
            visible = networkObject
        if visible is not None:
            visible.setLabelPosition(position)
    
    
    def setVisiblePosition(self, networkObject, position = None, fixed = None):
        """
        Set the position of the :class:`network object <network.object.Object>` within the display or within its visual container.
        
        The position parameter should be a tuple or list of numbers.  When setting the position of an object within another the coordinates are relative to a unit cube centered at (0.0, 0.0, 0.0).
        
        The fixed parameter indicates whether the user should be given GUI controls to manipulate the position of the object.
        """  
        
        if not isinstance(networkObject, (Object, Visible)) or (isinstance(networkObject, Object) and networkObject.network != self.network) or (isinstance(networkObject, Visible) and networkObject.display != self):
            raise ValueError, 'The object argument passed to setVisiblePosition() must be an object from the network being visualized by this display .'
        if position != None:
            if not isinstance(position, (tuple, list)) or len(position) != 3:
                raise TypeError, 'The position argument passed to setVisiblePosition() must be a tuple or list of three numbers.'
            for dim in position:
                if not isinstance(dim, (int, float)):
                    raise TypeError, 'The components of the position argument passed to setVisiblePosition() must be numbers.'
        
        visible = None
        if isinstance(networkObject, Object):
            visibles = self.visiblesForObject(networkObject)
            if len(visibles) == 1:
                visible = visibles[0]
            elif isinstance(networkObject, Stimulus):
                visible = visibles[0 if visibles[1].isPath() else 1]
        else:
            visible = networkObject
        if visible is not None:
            if position is not None:
                visible.setPosition(position)
            if fixed is not None:
                visible.setPositionIsFixed(fixed)
    
    
    def setVisibleRotation(self, networkObject, rotation):
        visibles = self.visiblesForObject(networkObject)
        if len(visibles) == 1:
            visibles[0].setRotation(rotation)
    
    
    def setVisibleSize(self, networkObject, size = None, fixed=True, absolute=False):
        """
        Set the size of the :class:`network object <network.object.Object>` within the display or within its visual container.
        
        The size parameter should be a tuple or list of numbers.  When setting the position of an object within another the coordinates are relative to a unit cube centered at (0.0, 0.0, 0.0).
        
        The fixed parameter indicates whether the user should be given GUI controls to manipulate the size of the object.
        
        The absolute parameter indicates whether the size should be considered relative to the entire display (True) or relative to the visual container (False).
        """  
        
        if not isinstance(networkObject, (Object, Visible)) or (isinstance(networkObject, Object) and networkObject.network != self.network) or (isinstance(networkObject, Visible) and networkObject.display != self):
            raise ValueError, 'The object argument passed to setVisibleSize() must be an object from the network being visualized by this display .'
        if not isinstance(size, (tuple, list)):
            raise TypeError, 'The size argument passed to setVisibleSize() must be a tuple or list of numbers.'
        for dim in size:
            if not isinstance(dim, (int, float)):
                raise TypeError, 'The components of the size argument passed to setVisibleSize() must be numbers.'
        
        visible = None
        if isinstance(networkObject, Object):
            visibles = self.visiblesForObject(networkObject)
            if len(visibles) == 1:
                visible = visibles[0]
        else:
            visible = networkObject
        if visible is not None:
            if size is not None:
                visible.setSize(size)
            visible.setSizeIsFixed(fixed)
            visible.setSizeIsAbsolute(absolute)
    
    
    def setVisibleColor(self, networkObject, color):
        """
        Set the color of the indicated :class:`network object <network.object.Object>`.
         
        The color argument should be a tuple or list of three values between 0.0 and 1.0 indicating the red, green and blue values of the color.  For example:
        
        * (0.0, 0.0, 0.0) -> black
        * (1.0, 0.0, 0.0) -> red
        * (0.0, 1.0, 0.0) -> green
        * (0.0, 0.0, 1.0) -> blue
        * (1.0, 1.0, 1.0) -> white
        
        Any alpha value should be set independently using :meth:`setVisibleOpacity <Display.Display.Display.setVisibleOpacity>`.
        """
        
        if not isinstance(networkObject, (Object, Visible)) or (isinstance(networkObject, Object) and networkObject.network != self.network) or (isinstance(networkObject, Visible) and networkObject.display != self):
            raise TypeError, 'The object argument passed to setVisibleColor() must be an object from the network being visualized by this display.'
        if (not isinstance(color, (tuple, list)) or len(color) != 3 or 
            not isinstance(color[0], (int, float)) or color[0] < 0.0 or color[0] > 1.0 or 
            not isinstance(color[1], (int, float)) or color[1] < 0.0 or color[1] > 1.0 or 
            not isinstance(color[2], (int, float)) or color[2] < 0.0 or color[2] > 1.0):
            raise ValueError, 'The color argument should be a tuple or list of three integer or floating point values between 0.0 and 1.0, inclusively.'
        
        visible = None
        if isinstance(networkObject, Object):
            visibles = self.visiblesForObject(networkObject)
            if len(visibles) == 1:
                visible = visibles[0]
            elif isinstance(networkObject, Stimulus):
                visible = visibles[0 if visibles[0].isPath() else 1]
        else:
            visible = networkObject
        if visible is not None:
            visible.setColor(color)
    
    
    def setVisibleTexture(self, networkObject, texture, scale = 1.0):
        """
        Set the :class:`texture <library.texture.Texture>` used to paint the surface of the visualized :class:`network object <network.object.Object>`.
        
        >>> display.setVisibleTexture(region1, library.texture('Stripes'))
        
        The texture parameter should be a :class:`texture <library.texture.Texture>` instance or None.
        
        The scale parameter can be used to reduce or enlarge the texture relative to the visualized object.
        """
        
        if not isinstance(networkObject, (Object, Visible)) or (isinstance(networkObject, Object) and networkObject.network != self.network) or (isinstance(networkObject, Visible) and networkObject.display != self):
            raise TypeError, 'The object argument passed to setVisibleTexture() must be an object from the network being visualized by this display.'
        if not isinstance(texture, (Texture, type(None))):
            raise TypeError, 'The texture argument passed to setVisibleTexture() must be a texture from the library or None.'
        if not isinstance(scale, (float, int)):
            raise TypeError, 'The scale argument passed to setVisibleTexture() must be a number.'
        
        visible = None
        if isinstance(networkObject, Object):
            visibles = self.visiblesForObject(networkObject)
            if len(visibles) == 1:
                visible = visibles[0]
            elif isinstance(networkObject, Stimulus):
                visible = visibles[0 if visibles[0].isPath() else 1]
        else:
            visible = networkObject
        if visible is not None:
            visible.setTexture(texture)
            visible.setTextureScale(scale)
    
    
    def setVisibleShape(self, networkObject, shape):
        """
        Set the shape of the :class:`network object's <network.object.Object>` visualization.
        
        >>> display.setVisibleShape(neuron1, shapes['Ball'])
        >>> display.setVisibleShape(muscle1, shapes['Ring'](startAngle = 0.0, endAngle = pi))
        
        The shape parameter should be one of the classes in the shapes dictionary, an instance of one of the classes or None.
        """
        
        if isinstance(shape, str):
            # Mapping for pre-0.9.4 scripts.
            shapeNameMap = {'ball': 'Ball', 'box': 'Box', 'capsule': 'Capsule', 'cone': 'Cone', 'tube': 'Cylinder'}
            if shape in shapeNameMap:
                shape = shapeNameMap[shape]
            shape = neuroptikon.shapeClass(shape) 
        
        if not isinstance(networkObject, (Object, Visible)) or (isinstance(networkObject, Object) and networkObject.network != self.network) or (isinstance(networkObject, Visible) and networkObject.display != self):
            raise TypeError, 'The object argument passed to setVisibleShape() must be an object from the network being visualized by this display.'
        if shape != None and not isinstance(shape, Shape) and (not type(shape) == type(self.__class__) or not issubclass(shape, Shape)):
            raise TypeError, 'The shape parameter must be an instance of one of the classes in the shapes dictionary, an instance of one of the classes or None.'
        
        visible = None
        if isinstance(networkObject, Object):
            visibles = self.visiblesForObject(networkObject)
            if len(visibles) == 1:
                visible = visibles[0]
            elif isinstance(networkObject, Stimulus):
                visible = visibles[0 if visibles[0].isPath() else 1]
        else:
            visible = networkObject
        if visible is not None:
            visible.setShape(shape)
    
    
    def setVisibleOpacity(self, networkObject, opacity):
        """
        Set the opacity of the :class:`network object's <network.object.Object>` visualization.
        
        The opacity parameter should be a number from 0.0 (fully transparent) to 1.0 (fully opaque).
        """
        
        if not isinstance(networkObject, (Object, Visible)) or (isinstance(networkObject, Object) and networkObject.network != self.network) or (isinstance(networkObject, Visible) and networkObject.display != self):
            raise TypeError, 'The object argument passed to setVisibleOpacity() must be an object from the network being visualized by this display.'
        if not isinstance(opacity, (int, float)) or opacity < 0.0 or opacity > 1.0:
            raise ValueError, 'The opacity argument passed to setVisibleOpacity() must be an number between 0.0 and 1.0, inclusive.'
        
        visible = None
        if isinstance(networkObject, Object):
            visibles = self.visiblesForObject(networkObject)
            if len(visibles) == 1:
                visible = visibles[0]
            elif isinstance(networkObject, Stimulus):
                visible = visibles[0 if visibles[0].isPath() else 1]
        else:
            visible = networkObject
        if visible is not None:
            visible.setOpacity(opacity)
    
    
    def setVisibleWeight(self, networkObject, weight):
        """
        Set the weight of the :class:`network object's <network.object.Object>` visualization.
        
        The weight parameter should be a float value with 1.0 being a neutral weight.  Currently this only applies to visualized connections.
        """
        
        if not isinstance(networkObject, (Object, Visible)) or (isinstance(networkObject, Object) and networkObject.network != self.network) or (isinstance(networkObject, Visible) and networkObject.display != self):
            raise TypeError, 'The object argument passed to setVisibleWeight() must be an object from the network being visualized by this display.'
        if not isinstance(weight, (int, float)):
            raise TypeError, 'The weight argument passed to setVisibleWeight() must be an number.'
        
        visible = None
        if isinstance(networkObject, Object):
            visibles = self.visiblesForObject(networkObject)
            if len(visibles) == 1:
                visible = visibles[0]
            elif isinstance(networkObject, Stimulus):
                visible = visibles[0 if visibles[0].isPath() else 1]
        else:
            visible = networkObject
        if visible is not None:
            visible.setWeight(weight)
    
    
    def setVisiblePath(self, networkObject, startObject, endObject, midPoints = None, fixed = None):
        """
        Set the start and end points of a connecting :class:`object <network.object.Object>` and any additional mid-points.
        
        The start and end object should be from the same network and the mid-points should be a list of coordinates, e.g. [(0.1, 0.3), (0.1, 0.5), (0.2, 0.5)].
        
        If the start or end objects are moved, resized, etc. then the connecting object's visualization will be adjusted to maintain the connection.
        """
        
        if isinstance(startObject, list):
            # Versions 0.9.4 and prior put the midPoints first.
            swap = startObject
            startObject = endObject
            endObject = midPoints
            midPoints = swap
        
        if ((not isinstance(networkObject, (Object, Visible)) or (isinstance(networkObject, Object) and networkObject.network != self.network) or (isinstance(networkObject, Visible) and networkObject.display != self)) or 
            not isinstance(startObject, (Object, Visible)) or (isinstance(startObject, Object) and startObject.network != self.network) or 
            not isinstance(endObject, (Object, Visible)) or (isinstance(endObject, Object) and endObject.network != self.network)):
            raise ValueError, 'The object, startObject and endObject arguments passed to setVisiblePath() must be objects from the network being visualized by this display.'
        if midPoints != None:
            if not isinstance(midPoints, (list, tuple)):
                raise TypeError, 'The midPoints argument passed to setVisiblePath() must be a list, a tuple or None.'
            for midPoint in midPoints:
                if not isinstance(midPoint, (list, tuple)) or len(midPoint) not in (2, 3):
                    raise ValueError, 'The mid-points passed to setVisiblePath() must be a list or tuple of numbers.'
                for midPointDim in midPoint:
                    if not isinstance(midPointDim, (int, float)):
                        raise ValueError, 'Each list or tuple mid-point passed to setVisiblePath() must contain only numbers.'
        if fixed != None:
            if not isinstance(fixed, bool):
                raise TypeError, 'The fixed argument passed to setVisiblePath() must be True, False or None'
        
        visible = None
        if isinstance(networkObject, Object):
            visibles = self.visiblesForObject(networkObject)
            if len(visibles) == 1:
                visible = visibles[0]
            elif isinstance(networkObject, Stimulus):
                visible = visibles[0 if visibles[0].isPath() else 1]
        else:
            visible = networkObject
        if visible is not None:
            if isinstance(startObject, Object):
                startVisibles = self.visiblesForObject(startObject)
                if len(startVisibles) != 1:
                    raise ValueError, 'The starting object of the path is not visualized.'
            else:
                startVisibles = [startObject]
            if isinstance(endObject, Object):
                endVisibles = self.visiblesForObject(endObject)
                if len(endVisibles) != 1:
                    raise ValueError, 'The ending object of the path is not visualized.'
            else:
                endVisibles = [endObject]
            visible.setPathEndPoints(startVisibles[0], endVisibles[0])
            if midPoints != None:
                visible.setPathMidPoints(midPoints)
            if fixed != None:
                visible.setPathIsFixed(fixed)
    
    
    def setVisibleFlowTo(self, networkObject, show = True, color = None, spacing = None, speed = None, spread = None):
        """
        Set the visualization style for the flow of information from the :class:`path object <network.object.Object>` start to its end.
        
        The color argument should be a tuple containing red, green and blue values.  For example:
        
        * (0.0, 0.0, 0.0) -> black
        * (1.0, 0.0, 0.0) -> red
        * (0.0, 1.0, 0.0) -> green
        * (0.0, 0.0, 1.0) -> blue
        * (1.0, 1.0, 1.0) -> white
        
        The spacing argument determines how far apart the pulses are placed and the speed argument determines how fast they move.  Both arguments should be in world space coordinates.
          
        The spread argument determines how far the tail of the pulse reaches, from 0.0 (no tail) to 1.0 (the tail reaches all the way to the next pulse).
        """
        
        if not isinstance(networkObject, (Object, Visible)) or (isinstance(networkObject, Object) and networkObject.network != self.network) or (isinstance(networkObject, Visible) and networkObject.display != self):
            raise TypeError, 'The object argument passed to setVisibleFlowTo() must be an object from the network being visualized by this display.'
        
        visible = None
        if isinstance(networkObject, Object):
            visibles = self.visiblesForObject(networkObject)
            if len(visibles) == 1:
                visible = visibles[0]
            elif isinstance(networkObject, Stimulus):
                visible = visibles[0 if visibles[0].isPath() else 1]
        else:
            visible = networkObject
        if visible is not None:
            visible.setFlowTo(show)
            if color is not None:
                if len(color) == 3:
                    color = (color[0], color[1], color[2], 1.0)
                visible.setFlowToColor(color)
            if spacing is not None:
                visible.setFlowToSpacing(spacing)
            if speed is not None:
                visible.setFlowToSpeed(speed)
            if spread is not None:
                visible.setFlowToSpread(spread)
    
    
    def setVisibleFlowFrom(self, networkObject, show = True, color = None, spacing = None, speed = None, spread = None):
        """
        Set the visualization style for the flow of information from the :class:`path object's <network.object.Object>` end back to its start.
        
        The color argument should be a tuple containing red, green and blue values.  For example:
        
        * (0.0, 0.0, 0.0) -> black
        * (1.0, 0.0, 0.0) -> red
        * (0.0, 1.0, 0.0) -> green
        * (0.0, 0.0, 1.0) -> blue
        * (1.0, 1.0, 1.0) -> white
        
        The spacing argument determines how far apart the pulses are placed and the speed argument determines how fast they move.  Both arguments should be in world space coordinates.
          
        The spread argument determines how far the tail of the pulse reaches, from 0.0 (no tail) to 1.0 (the tail reaches all the way to the next pulse).
        """
        
        if not isinstance(networkObject, (Object, Visible)) or (isinstance(networkObject, Object) and networkObject.network != self.network) or (isinstance(networkObject, Visible) and networkObject.display != self):
            raise TypeError, 'The object argument passed to setVisibleFlowFrom() must be an object from the network being visualized by this display.'
        
        visible = None
        if isinstance(networkObject, Object):
            visibles = self.visiblesForObject(networkObject)
            if len(visibles) == 1:
                visible = visibles[0]
            elif isinstance(networkObject, Stimulus):
                visible = visibles[0 if visibles[0].isPath() else 1]
        else:
            visible = networkObject
        if visible is not None:
            visible.setFlowFrom(show)
            if color is not None:
                if len(color) == 3:
                    color = (color[0], color[1], color[2], 1.0)
                visible.setFlowFromColor(color)
            if spacing is not None:
                visible.setFlowFromSpacing(spacing)
            if speed is not None:
                visible.setFlowFromSpeed(speed)
            if spread is not None:
                visible.setFlowFromSpread(color)
    
    
    def setArrangedAxis(self, networkObject, axis = 'largest', recurse = False):
        """
        Automatically arrange the visible children of the indicated :class:`network object <network.object.Object>` along the specified axis.
        
        The axis value should be one of 'largest', 'X', 'Y', 'Z' or None.  When 'largest' is indicated the children will be arranged along whichever axis is longest at any given time.  Resizing the parent object therefore can change which axis is used.
        
        If recurse is True then all descendants will have their axes set as well.
        """
        
        if not isinstance(networkObject, (Object, Visible)) or (isinstance(networkObject, Object) and networkObject.network != self.network) or (isinstance(networkObject, Visible) and networkObject.display != self):
            raise ValueError, 'The object argument passed to setArrangedAxis() must be an object from the network being visualized by this display .'
        if axis not in [None, 'largest', 'X', 'Y', 'Z']:
            raise ValueError, 'The axis argument passed to setArrangedAxis() must be one of \'largest\', \'X\', \'Y\', \'Z\' or None.'
        
        visible = None
        if isinstance(networkObject, Object):
            visibles = self.visiblesForObject(networkObject)
            if len(visibles) == 1:
                visible = visibles[0]
        else:
            visible = networkObject
        if visible is not None:
            visible.setArrangedAxis(axis = axis, recurse = recurse)
    
    
    def setArrangedSpacing(self, networkObject, spacing = .02, recurse = False):
        """
        Set the visible spacing between the children of the indicated :class:`network object <network.object.Object>`.
        
        The spacing is measured as a fraction of the whole.  So a value of .02 uses 2% of the parent's size for the spacing between each object.
         
        If recurse is True then all descendants will have their spacing set as well.
        """
        
        if not isinstance(networkObject, (Object, Visible)) or (isinstance(networkObject, Object) and networkObject.network != self.network) or (isinstance(networkObject, Visible) and networkObject.display != self):
            raise ValueError, 'The object argument passed to setArrangedSpacing() must be an object from the network being visualized by this display .'
        if not isinstance(spacing, (int, float)):
            raise TypeError, 'The spacing argument passed to setArrangedSpacing() must be an integer or floating point value.'
        
        visible = None
        if isinstance(networkObject, Object):
            visibles = self.visiblesForObject(networkObject)
            if len(visibles) == 1:
                visible = visibles[0]
        else:
            visible = networkObject
        if visible is not None:
            visible.setArrangedSpacing(spacing = spacing, recurse = recurse)
    
    
    def setArrangedWeight(self, networkObject, weight):
        """
        Set the amount of its parent's space the indicated :class:`network object <network.object.Object>` should use compared to its siblings.
        
        Larger weight values will result in more of the parent's space being used.
         
        If recurse is True then all descendants will have their spacing set as well.
        """
        
        if not isinstance(networkObject, (Object, Visible)) or (isinstance(networkObject, Object) and networkObject.network != self.network) or (isinstance(networkObject, Visible) and networkObject.display != self):
            raise ValueError, 'The object argument passed to setArrangedWeight() must be an object from the network being visualized by this display .'
        if not isinstance(weight, (int, float)):
            raise TypeError, 'The weight argument passed to setArrangedWeight() must be an integer or floating point value.'
        
        visible = None
        if isinstance(networkObject, Object):
            visibles = self.visiblesForObject(networkObject)
            if len(visibles) == 1:
                visible = visibles[0]
        else:
            visible = networkObject
        if visible is not None:
            visible.setArrangedWeight(weight)
    
    
    def selectObjectsMatching(self, predicate):
        matchingVisibles = []
        for networkObject in self.network.objects:
            if predicate.matches(networkObject):
                for visible in self.visiblesForObject(networkObject):
                    matchingVisibles.append(visible)
        self.selectVisibles(matchingVisibles)
    
    
    def selectObjects(self, objects, extend = False, findShortestPath = False):
        """
        Select the indicated :class:`network objects <network.object.Object>`.
        
        If extend is True then the objects will be added to the current selection, otherwise the objects will replace the current selection.
        
        If findShortestPath is True then the shortest path between the currently selected object(s)s and the indicated object(s) will be found and all will be selected.
        """
        
        if not isinstance(objects, (list, tuple, set)):
            raise TypeError, 'The objects argument passed to selectObjects must be a list, tuple or set.'
        
        visibles = []
        for networkObject in objects:
            visibles.extend(self.visiblesForObject(networkObject))
        self.selectVisibles(visibles, extend, findShortestPath)
    
    
    def selectObject(self, networkObject, extend = False, findShortestPath = False):
        """
        Select the indicated :class:`network object <network.object.Object>`.
        
        If extend is True then the object will be added to the current selection, otherwise the object will replace the current selection.
        
        If findShortestPath is True then the shortest path between the currently selected object(s)s and the indicated object will be found and all will be selected.
        """
        
        for visible in self.visiblesForObject(networkObject):
            self.selectVisibles([visible], extend, findShortestPath)
    
    
    def objectIsSelected(self, networkObject):
        """
        Return whether the indicated :class:`network object <network.object.Object>` is part of the current selection.
        """
        
        for visible in self.visiblesForObject(networkObject):
            if visible in self.selectedVisibles:
                return True
        return False
    
    
    def selectVisibles(self, visibles, extend = False, findShortestPath = False):
        """
        Select the indicated :class:`visible proxies <display.visible.Visible>`.
        
        If extend is True then the visible will be added to the current selection, otherwise the visible will replace the current selection.
        
        If findShortestPath is True then the shortest path between the currently selected visible(s) and the indicated visible will be found and all will be selected.
        """
        time1 = time.time()
        if (extend or findShortestPath) and not self.hoverSelected:
            newSelection = set(self.selectedVisibles)
        else:
            newSelection = set()
        
        if findShortestPath:
            # Add the visibles that exist along the path to the selection.
            pathWasFound = False
            #TODO Slow
            for visible in visibles:
                for startVisible in self.selectedVisibles:
                    for pathObject in self.network.shortestPath(startVisible.client, visible.client):
                        for pathVisible in self.visiblesForObject(pathObject):
                            pathWasFound = True
                            newSelection.add(pathVisible)
            if not pathWasFound:
                wx.Bell()
        elif extend and len(visibles) == 1 and visibles[0] in newSelection:
            # Remove the visible from the selection
            newSelection.remove(visibles[0])
        else:
            # Add the visibles to the new selection.
            for visible in visibles:
                # Select the root of the object if appropriate.
                rootObject = visible.client.rootObject()
                if rootObject and not self.objectIsSelected(rootObject) and not self.visiblesForObject(rootObject)[0] in visibles:
                    visibles = self.visiblesForObject(rootObject)
                    if any(visibles):
                        visible = visibles[0]
                newSelection.add(visible)
        
        self._selectedShortestPath = findShortestPath
        
        if newSelection != self.selectedVisibles or (self.hoverSelected and not self.hoverSelecting):
            self._clearDragger()
            
            self.selectedVisibles = newSelection
            
            if len(self.selectedVisibles) == 0:
                # There is no selection so hover selecting should be enabled.
                self.hoverSelecting = False
                self.hoverSelect = True
            elif not self.hoverSelecting:
                # An explicit selection has been made via the GUI or console.
                
                self.hoverSelect = False    # disable hover selecting
                # TODO Dragging doesn't work so this just takes time
                if len(self.selectedVisibles) == 1:
                    pass
                    # Add a dragger to the selected visible.
                    # visible = list(self.selectedVisibles)[0]
                    # if visible._isDraggable():
                    #     self._addDragger(visible)
            
            dispatcher.send(('set', 'selection'), self)
        
        self.hoverSelected = self.hoverSelecting
        self.hoverSelecting = False
        self.Refresh()
        time2 = time.time()
        print 'FINAL It took %0.3f ms' % ((time2-time1)*1000.0)
    
    def selection(self):
        return ObjectList(self.selectedVisibles)
    
    
    def selectedObjects(self):
        """
        Return the list of :class:`network objects <network.object.Object>` that are currently selected.
        """
        
        selection = set()
        for visible in self.selectedVisibles:
            if visible.client is not None:
                selection.add(visible.client)
        return list(selection)
    
    
    def selectAll(self):
        """
        Select all :class:`network objects <network.object.Object>` in the visualization.
        """
        
        visiblesToSelect = []
        for visibles in self.visibles.itervalues():
            for visible in visibles:
                visiblesToSelect.append(visible)
        self.selectVisibles(visiblesToSelect)
    
    
    def _onSelectionOrShowFlowChanged(self):
        # Update the highlighting, animation and ghosting based on the current selection.
        # TODO: this should all be handled by display rules
        time1 = time.time()
        
        refreshWasSupressed = self._suppressRefresh
        self._suppressRefresh = True
        
        def _highlightObject(networkObject):
            highlightedSomething = False
            
            # Highlight/animate all visibles for this object.
            for visible in self.visiblesForObject(networkObject):
                if visible.isPath():
                    if visible not in visiblesToAnimate:
                        visiblesToAnimate.add(visible)
                        visiblesToHighlight.add(visible)
                        highlightedSomething = True
                elif visible not in visiblesToHighlight:
                    visiblesToHighlight.add(visible)
                    highlightedSomething = True
            # Highlight to the root of the object if appropriate.
            networkObject = networkObject.parentObject()
            while networkObject:
                if _highlightObject(networkObject):
                    networkObject = networkObject.parentObject()
                else:
                    networkObject = None
            
            return highlightedSomething  
        
        # TODO: selecting neuron X in Morphology.py doesn't highlight neurites
        
        def _highlightConnectedObjects(rootObjects, maxDepth, highlightWithinSelection):
            # Do a breadth-first search on the graph of objects.
            queue = [[rootObject] for rootObject in rootObjects]
            # TBD: needed? visitedObjects = []
            print queue
            highlightedObjects = [rootObject.rootObject() for rootObject in rootObjects]
            count = 0
            # while any(queue):
            #     count += 1
            #     curPath = queue.pop(0)
            #     curObject = curPath[-1]
            #     curObjectRoot = curObject.rootObject()
            #
            #     # If we've reached a highlighted object or the maximum depth then highlight the objects in the current path.
            #     if curObjectRoot in highlightedObjects or (not highlightWithinSelection and len(curPath) == maxDepth + 1):
            #         for pathObject in curPath:
            #             _highlightObject(pathObject)
            #
            #     # If we haven't reached the maximum depth then add the next layer of connections to the end of the queue.
            #     if len(curPath) < maxDepth + 1:
            #         for connectedObject in curObjectRoot.connections():
            #             if connectedObject not in curPath and connectedObject.rootObject() not in curPath:
            #                 queue += [curPath + [connectedObject]]
            print count
        
        visiblesToHighlight = set()
        visiblesToAnimate = set()
        if self._selectedShortestPath or not self.selectConnectedVisibles:
            isSingleSelection = (len(self.selectedVisibles) == 1) or not self._highlightOnlyWithinSelection
            for selectedVisible in self.selectedVisibles:
                if isinstance(selectedVisible.client, Object):
                    _highlightObject(selectedVisible.client)
                else:
                    # The selected visible has no network counterpart so highlight/animate connected visibles purely based on connectivity in the visualization.
                    visiblesToHighlight.add(selectedVisible)
                    if selectedVisible.isPath() and (selectedVisible.flowTo() or selectedVisible.flowFrom()):
                        visiblesToAnimate.add(selectedVisible)
                        visiblesToHighlight.add(selectedVisible)
                    if selectedVisible.isPath():
                        # Highlight the visibles at each end of the path.
                        if selectedVisible.flowTo() or selectedVisible.flowFrom():
                            visiblesToAnimate.add(selectedVisible)
                            visiblesToHighlight.add(selectedVisible)
                        [visiblesToHighlight.add(endPoint) for endPoint in selectedVisible.pathEndPoints()] 
                    elif self.selectConnectedVisibles and not self._selectedShortestPath:
                        # Animate paths connecting to this non-path visible and highlight the other end of the paths.
                        for pathVisible in selectedVisible.connectedPaths:
                            otherVis = pathVisible._pathCounterpart(selectedVisible)
                            if isSingleSelection or otherVis in self.selectedVisibles:
                                visiblesToAnimate.add(pathVisible)
                                visiblesToHighlight.add(pathVisible)
                                visiblesToHighlight.add(otherVis)
        else:
            # TODO: handle object-less visibles
            # SLOW for selecting object, no time for deselecting objects
            _highlightConnectedObjects(self.selectedObjects(), self._selectionHighlightDepth, len(self.selectedVisibles) > 1 and self._highlightOnlyWithinSelection)
            time2 = time.time()
            print 'B It took %0.3f ms' % ((time2-time1)*1000.0)
        if len(self.selectedVisibles) == 0 and self._showFlow:
            for visibles in self.visibles.itervalues():
                for visible in visibles:
                    if visible.isPath() and (visible.flowTo() or visible.flowFrom()):
                        visiblesToAnimate.add(visible)
        
        # Turn off highlighting/animating for visibles that shouldn't have it anymore.
        for highlightedNode in self.highlightedVisibles:
            if highlightedNode not in visiblesToHighlight:
                highlightedNode.setGlowColor(None)
        for animatedEdge in self.animatedVisibles:
            animatedEdge.boldWeight(1.0)
            if animatedEdge not in visiblesToAnimate:
                animatedEdge.animateFlow(False)

        
        # Highlight/animate the visibles that should have it now.
        for visibleToHighlight in visiblesToHighlight:
            if visibleToHighlight in self.selectedVisibles:
                visibleToHighlight.setGlowColor(self._primarySelectionColor)
            elif not self._useGhosts:
                visibleToHighlight.setGlowColor(self._secondarySelectionColor)
            else:
                visibleToHighlight.setGlowColor(None)
        # SLOW
        s = []
        for visibleToAnimate in visiblesToAnimate:
            visibleToAnimate.boldWeight(5.0)
            visibleToAnimate.animateFlow()
            s.append(visibleToAnimate)
        print len(s)
        time2 = time.time()
        print 'G It took %0.3f ms' % ((time2-time1)*1000.0)
        
        self.highlightedVisibles = visiblesToHighlight
        self.animatedVisibles = visiblesToAnimate
        # SLOWISH not the main culprit
        if self._useGhosts:
            # Dim everything that isn't selected, highlighted or animated.
            for visibles in self.visibles.itervalues():
                for visible in visibles:
                    visible._updateOpacity()
        time2 = time.time()
        print 'H It took %0.3f ms' % ((time2-time1)*1000.0)
        
        if any(self.animatedVisibles):
            # Start the animation timer and cap the frame rate at 60 fps.
            if not self._animationTimer.IsRunning():
                self._animationTimer.Start(1000.0 / 60.0)
        elif self._animationTimer.IsRunning():
            # Don't need to redraw automatically if nothing is animated. 
            self._animationTimer.Stop()
        time2 = time.time()
        print 'EOM It took %0.3f ms' % ((time2-time1)*1000.0)
        
        self._suppressRefresh = refreshWasSupressed
    
    
    def _addDragger(self, visible):
        if visible.parent is None:
            rootNode = self.rootNode
        else:
            rootNode = visible.parent.childGroup
        
        lodBound = visible.sgNode.getBound()
        rootNode.removeChild(visible.sgNode)
        
        self.dragSelection = osgManipulator.Selection()
        self.dragSelection.addChild(visible.sgNode)
        rootNode.addChild(self.dragSelection)
        
        self.compositeDragger = None
        pixelCutOff = 200.0
        if self.viewDimensions == 2:
            self.draggerScale = 1.0
            self.simpleDragger = osgManipulator.TranslatePlaneDragger()
            if not visible.sizeIsFixed():
                self.compositeDragger = osgManipulator.TabPlaneDragger()
            if self.orthoViewPlane == 'xy':
                if visible.parent is None or not visible.sizeIsAbsolute():
                    self.draggerOffset = (0.0, 0.0, visible.size()[2])
                else:
                    self.draggerOffset = (0.0, 0.0, visible.size()[2] / visible.parent.worldSize()[2])
                    pixelCutOff /= visible.parent.worldSize()[0]
                draggerMatrix = osg.Matrixd.rotate(pi / 2.0, osg.Vec3d(1, 0, 0)) * \
                                visible.sgNode.getMatrix() * \
                                osg.Matrixd.translate(*self.draggerOffset)
            elif self.orthoViewPlane == 'xz':
                if visible.parent is None or not visible.sizeIsAbsolute():
                    self.draggerOffset = (0.0, visible.size()[1], 0.0)
                else:
                    self.draggerOffset = (0.0, visible.size()[1] / visible.parent.worldSize()[1], 0.0)
                    pixelCutOff /= visible.parent.worldSize()[0]
                draggerMatrix = visible.sgNode.getMatrix() * \
                                osg.Matrixd.translate(*self.draggerOffset)
            elif self.orthoViewPlane == 'zy':
                if visible.parent is None or not visible.sizeIsAbsolute():
                    self.draggerOffset = (visible.size()[0], 0.0, 0.0)
                else:
                    self.draggerOffset = (visible.size()[0] / visible.parent.worldSize()[0], 0.0, 0.0)
                    pixelCutOff /= visible.parent.worldSize()[1]
                draggerMatrix = osg.Matrixd.rotate(pi / 2.0, osg.Vec3d(1, 0, 0)) * \
                                osg.Matrixd.rotate(pi / 2.0, osg.Vec3d(0, 1, 0)) * \
                                visible.sgNode.getMatrix() * \
                                osg.Matrixd.translate(*self.draggerOffset)
        elif self.viewDimensions == 3:
            self.draggerOffset = (0.0, 0.0, 0.0)
            self.draggerScale = 1.02
            self.simpleDragger = osgManipulator.TranslateAxisDragger()
            if not visible.sizeIsFixed():
                self.compositeDragger = osgManipulator.TabBoxDragger()
                if visible.parent is not None and visible.sizeIsAbsolute():
                    pixelCutOff /= visible.parent.worldSize()[0]
            draggerMatrix = osg.Matrixd.rotate(pi / 2.0, osg.Vec3d(1, 0, 0)) * \
                            osg.Matrixd.scale(self.draggerScale, self.draggerScale, self.draggerScale) * \
                            visible.sgNode.getMatrix()
        self.simpleDragger.setMatrix(draggerMatrix)
        self.simpleDragger.setupDefaultGeometry()
        self.commandMgr = osgManipulator.CommandManager()
        self.commandMgr.connect(self.simpleDragger, self.dragSelection)
        if visible.sizeIsFixed():
            rootNode.addChild(self.simpleDragger)
            self.activeDragger = self.simpleDragger
        else:
            self.commandMgr.connect(self.compositeDragger, self.dragSelection)
            self.compositeDragger.setMatrix(draggerMatrix)
            self.compositeDragger.setupDefaultGeometry()
            
            self.draggerLOD = osg.LOD()
            self.draggerLOD.setRangeMode(osg.LOD.PIXEL_SIZE_ON_SCREEN)
            self.draggerLOD.addChild(self.simpleDragger, 0.0, pixelCutOff)
            self.draggerLOD.addChild(self.compositeDragger, pixelCutOff, 10000.0)
            self.draggerLOD.setCenter(lodBound.center())
            self.draggerLOD.setRadius(lodBound.radius())
            rootNode.addChild(self.draggerLOD)
            
            # TODO: This is a serious hack.  The existing picking code in PickHandler doesn't handle the dragger LOD correctly.  It always picks the composite dragger.  Cull callbacks are added here so that we can know which dragger was most recently rendered.
            self.activeDragger = None
            self.simpleDragger.setCullCallback(DraggerCullCallback(self, self.simpleDragger).__disown__())
            self.compositeDragger.setCullCallback(DraggerCullCallback(self, self.compositeDragger).__disown__())
        
        # TODO: observe the visible's 'positionIsFixed' attribute and add/remove the draggers as needed
    
    
    def _visibleWasDragged(self):
        # TODO: It would be nice to constrain dragging if the visible has a parent.  "Resistance" would be added when the child reached the parent border so that dragging slowed or stopped but if dragged far enough the child could force its way through.
        visible = list(self.selectedVisibles)[0]
        if self.activeDragger is not None:
            matrix = self.activeDragger.getMatrix()
            position = matrix.getTrans()
            size = matrix.getScale()
            if visible.parent is None or not visible.sizeIsAbsolute():
                parentSize = (1.0, 1.0, 1.0)
            else:
                parentSize = visible.parent.worldSize()
            visible.setPosition((position.x() - self.draggerOffset[0], position.y() - self.draggerOffset[1], position.z() - self.draggerOffset[2]))
            visible.setSize((size.x() * parentSize[0] / self.draggerScale, size.y() * parentSize[1] / self.draggerScale, size.z() * parentSize[2] / self.draggerScale))
            visible._updateTransform()
    
    
    def _clearDragger(self):
        if self.dragSelection != None:
            visible = list(self.selectedVisibles)[0]
            
            if visible.parent is None:
                rootNode = self.rootNode
            else:
                rootNode = visible.parent.childGroup
            
            self.commandMgr.disconnect(self.simpleDragger)
            if self.compositeDragger is not None:
                self.commandMgr.disconnect(self.compositeDragger)
            self.commandMgr = None
            
            self.dragSelection.removeChild(visible.sgNode)
            rootNode.removeChild(self.dragSelection)
            self.dragSelection = None
            
            rootNode.addChild(visible.sgNode)
            self._visibleWasDragged()
            
            if self.draggerLOD is not None:
                rootNode.removeChild(self.draggerLOD)
            else:
                rootNode.removeChild(self.simpleDragger)
            
            self.simpleDragger.setCullCallback(None)
            self.simpleDragger = None
            if self.compositeDragger is not None:
                self.compositeDragger.setCullCallback(None)
                self.compositeDragger = None
            self.draggerLOD = None
    
    
    def onLayout(self, event):
        layoutClasses = self.GetTopLevelParent().layoutClasses
        layoutId = event.GetId()
        if layoutId in layoutClasses:
            layout = layoutClasses[layoutId]()
            self.lastUsedLayout = layout
        else:
            layout = None
        self.performLayout(layout)
    
    
    def autoLayout(self, method = None):
        # Backwards compatibility method, new code should use performLayout() instead.
        
        if (method == 'graphviz' or method is None) and self.viewDimensions == 2:
            from Layouts.force_directed import ForceDirectedLayout
            self.performLayout(ForceDirectedLayout())
        elif (method == 'spectral' or method is None) and self.viewDimensions == 3:
            from Layouts.spectral import SpectralLayout
            self.performLayout(SpectralLayout())
    
    
    def performLayout(self, layout = None, **kwargs):
        """ Perform an automatic layout of the :class:`network objects <network.object.Object>` in the visualization.
        
        >>> display.performLayout(layouts['Force Directed'])
        
        The layout parameter should be one of the classes in layouts, an instance of one of the classes or None to re-execute the previous or default layout.
        """
        
        if layout != None and not isinstance(layout, layout_module.Layout) and (not type(layout) == type(self.__class__) or not issubclass(layout, layout_module.Layout)):
            raise TypeError, 'The layout parameter passed to performLayout() should be one of the classes in layouts, an instance of one of the classes or None.'
        
        self.beginProgress('Laying out the network...')
        try:
            if layout == None:
                # Fall back to the last layout used.
                layout = self.lastUsedLayout
            else:
                # If a layout class was passed in then create a default instance.
                if isinstance(layout, type(self.__class__)):
                    layout = layout(**kwargs)
                
                if not layout.__class__.canLayoutDisplay(self):
                    raise ValueError, gettext('The supplied layout cannot be used.')
            
            if layout == None or not layout.__class__.canLayoutDisplay(self):   # pylint: disable=E1103
                layouts = neuroptikon.scriptLocals()['layouts']
                if 'Graphviz' in layouts:
                    layout = layouts['Graphviz'](**kwargs)
                elif 'Force Directed' in layouts:
                    layout = layouts['Force Directed'](**kwargs)
                elif 'Spectral' in layouts:
                    layout = layouts['Spectral'](**kwargs)
                else:
                    # Pick the first layout class capable of laying out the display.
                    for layoutClass in layouts.itervalues():
                        if layoutClass.canLayoutDisplay(self):
                            layout = layoutClass(**kwargs)
                            break
            
            refreshWasSuppressed = self._suppressRefresh
            self._suppressRefresh = True
            layout.layoutDisplay(self)
            self.lastUsedLayout = layout
        except:
            (exceptionType, exceptionValue) = sys.exc_info()[0:2]
            wx.MessageBox(str(exceptionValue) + ' (' + exceptionType.__name__ + ')', gettext('An error occurred while performing the layout:'), parent = self, style = wx.ICON_ERROR | wx.OK)
        finally:
            self._suppressRefresh = refreshWasSuppressed
            if self.viewDimensions == 2:
                self.zoomToFit()
            else:
                self.resetView()
            self.endProgress()
    
    
    def saveViewAsImage(self, path):
        """
        Save a snapshot of the current visualization to an image file.
        
        The path parameter should indicate where the snapshot should be saved.  The extension included in the path will determine the format of the image.  Currently, bmp, jpg, png and tiff extensions are supported.
        
        If the background color of the display has an alpha value less than 1.0 then the image saved will have a transparent background for formats that support it.
        """
        
        width, height = self.GetClientSize()
        image = osg.Image()
        self.SetCurrent(self.glContext)
        image.readPixels(0, 0, width, height, osg.GL_RGBA, osg.GL_UNSIGNED_BYTE)
        osgDB.writeImageFile(image, path)
    
    
    def onSaveView(self, event_):
        fileTypes = ['JPG', 'Microsoft BMP', 'PNG', 'TIFF']
        fileExtensions = ['jpg', 'bmp', 'png', 'tiff']
        wildcard = ''
        for index in range(0, len(fileTypes)):
            if wildcard != '':
                wildcard += '|'
            wildcard += fileTypes[index] + '|' + fileExtensions[index]
        fileDialog = wx.FileDialog(None, gettext('Save As:'), '', '', wildcard, wx.SAVE | wx.FD_OVERWRITE_PROMPT)
        if fileDialog.ShowModal() == wx.ID_OK:
            extension = fileExtensions[fileDialog.GetFilterIndex()]
            savePath = str(fileDialog.GetPath())
            if not savePath.endswith('.' + extension):
                savePath += '.' + extension
            self.saveViewAsImage(savePath)
        fileDialog.Destroy()
    
    
    def setDefaultFlowColor(self, color):
        """
        Set the default color of the pulses in paths showing the flow of information.
        
        The color argument should be a tuple or list of three values between 0.0 and 1.0 indicating the red, green and blue values of the color.  For example:
        
        * (0.0, 0.0, 0.0) -> black
        * (1.0, 0.0, 0.0) -> red
        * (0.0, 1.0, 0.0) -> green
        * (0.0, 0.0, 1.0) -> blue
        * (1.0, 1.0, 1.0) -> white
        """
        
        if not isinstance(color, (list, tuple)):    # or len(color) != 3:
            raise ValueError, 'The color passed to setDefaultFlowColor() must be a tuple or list of three numbers.'
        for colorComponent in color:
            if not isinstance(colorComponent, (int, float)) or colorComponent < 0.0 or colorComponent > 1.0:
                raise ValueError, 'The components of the color passed to setDefaultFlowColor() must all be numbers between 0.0 and 1.0, inclusive.'
        
        if len(color) == 3:
            color = (color[0], color[1], color[2], 1.0)
        
        if color != self.defaultFlowColor:
            self.defaultFlowColor = color
            vec4color = osg.Vec4f(color[0], color[1], color[2], color[3])
            self.defaultFlowToColorUniform.set(vec4color)
            self.defaultFlowFromColorUniform.set(vec4color)
            dispatcher.send(('set', 'defaultFlowColor'), self)
    
    
    def setDefaultFlowSpacing(self, spacing):
        """
        Set the default spacing between pulses in paths showing the flow of information.
        
        The spacing argument is measured in world-space coordinates.
        """
        
        if not isinstance(spacing, (int, float)):
            raise TypeError, 'The spacing passed to setDefaultFlowSpacing() must be a number.'
        
        if spacing != self.defaultFlowSpacing:
            self.defaultFlowSpacing = float(spacing)
            self.defaultFlowToSpacingUniform.set(self.defaultFlowSpacing)
            self.defaultFlowFromSpacingUniform.set(self.defaultFlowSpacing)
            dispatcher.send(('set', 'defaultFlowSpacing'), self)
    
    
    def setDefaultFlowSpeed(self, speed):
        """
        Set the default speed of the pulses in paths showing the flow of information.
        
        The speed argument is measured in world-space coordinates per second.
        """
        
        if not isinstance(speed, (int, float)):
            raise TypeError, 'The speed passed to setDefaultFlowSpeed() must be a number.'
        
        if speed != self.defaultFlowSpeed:
            self.defaultFlowSpeed = float(speed)
            self.defaultFlowToSpeedUniform.set(self.defaultFlowSpeed)
            self.defaultFlowFromSpeedUniform.set(self.defaultFlowSpeed)
            dispatcher.send(('set', 'defaultFlowSpeed'), self)
    
    
    def setDefaultFlowSpread(self, spread):
        """
        Set the length of the pulse tails in paths showing the flow of information.
        
        The spread argument should be a number from 0.0 (no tail) to 1.0 (tail extends all the way to the next pulse). 
        """
        
        if not isinstance(spread, (int, float)):
            raise TypeError, 'The spread passed to setDefaultFlowSpread() must be a number.'
        
        if spread != self.defaultFlowSpread:
            self.defaultFlowSpread = float(spread)
            self.defaultFlowToSpreadUniform.set(self.defaultFlowSpread)
            self.defaultFlowFromSpreadUniform.set(self.defaultFlowSpread)
            dispatcher.send(('set', 'defaultFlowSpread'), self)
    
    
    def beginProgress(self, message = None, visualDelay = 1.0):
        """
        Display a message that a lengthy task has begun.
        
        Each call to this method must be balanced by a call to :meth:`endProgress <display.display.Display.endProgress>`.  Any number of :meth:`updateProgress <display.display.Display.updateProgress>` calls can be made in the interim.  Calls to this method can be nested as long as the right number of :meth:`endProgress <display.display.Display.endProgress>` calls are made.
        
        The visualDelay argument indicates how many seconds to wait until the progress user interface is shown.  This avoids flashing the interface open and closed for tasks that end up running quickly.
        """
        
        return self.GetTopLevelParent().beginProgress(message, visualDelay)
    
    
    def updateProgress(self, message = None, fractionComplete = None):
        """
        Update the message and/or completion fraction during a lengthy task.
        
        If the user has pressed the Cancel button then this method will return False and the task should be aborted.
        """
        
        return self.GetTopLevelParent().updateProgress(message, fractionComplete)
    
    
    def endProgress(self):
        """
        Indicate that the lengthy task has ended.
        """
        
        return self.GetTopLevelParent().endProgress()
    
    
    def addObjectOfClass(self, objectClass):
        self._visibleBeingAdded = self.visualizeObject(None, **objectClass._defaultVisualizationParams())
        self._visibleBeingAdded.objectClass = objectClass
    
    
    def objectClassBeingAdded(self):
        return self._visibleBeingAdded.objectClass if self._visibleBeingAdded else None
            

class DisplayDropTarget(wx.PyDropTarget):
    
    def __init__(self, display):
        wx.PyDropTarget.__init__(self)
        self.display = display

        # specify the type of data we will accept
        self.dropData = wx.CustomDataObject("Neuroptikon Ontology Term")
        self.SetDataObject(self.dropData)
    
    
    def OnData(self, x_, y_, dragType):
        if self.GetData():
            termData = self.dropData.GetData()
            termDict = cPickle.loads(termData)
            ontologyId = termDict['Ontology']
            termId = termDict['Term']
            
            ontology = neuroptikon.library.ontology(ontologyId)
            if ontology is not None:
                term = ontology[termId]
                if term is not None:
                    self.display.network.createRegion(ontologyTerm = term, addSubTerms = wx.GetKeyState(wx.WXK_ALT))
                    if len(self.display.visibles) == 1:
                        self.display.zoomToFit()
            
        return dragType
    
