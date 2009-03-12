import wx
import wx.glcanvas
import osg, osgDB, osgFX, osgGA, osgManipulator, osgViewer
from PickHandler import PickHandler
from DraggerCullCallback import DraggerCullCallback
from Network.Network import Network
from Network.Region import Region
from Network.Pathway import Pathway
from Network.Neuron import Neuron
from Network.Neurite import Neurite
from Network.Arborization import Arborization
from Network.Synapse import Synapse
from Network.GapJunction import GapJunction
from Network.Stimulus import Stimulus
from Network.Muscle import Muscle
from Network.Innervation import Innervation
from Network.ObjectList import ObjectList
from Visible import Visible
from DisplayRule import DisplayRule
from wx.py import dispatcher
from networkx import *
from math import pi, fabs
from datetime import datetime
from numpy import diag, mat, sign, inner, isinf, zeros
from numpy.linalg import pinv, eigh
import os, platform, cPickle
import xml.etree.ElementTree as ElementTree

try:
    import pygraphviz
except ImportError:
    pygraphviz = None
    try:
        import pydot
    except ImportError:
        pydot = None


class Display(wx.glcanvas.GLCanvas):
    
    def __init__(self, parent, network = None, id = wx.ID_ANY):
        style = wx.WANTS_CHARS | wx.FULL_REPAINT_ON_RESIZE | wx.HSCROLL | wx.VSCROLL
        if not hasattr(wx.glcanvas, "WX_GL_SAMPLE_BUFFERS"):
            wx.glcanvas.WX_GL_SAMPLE_BUFFERS = wx.glcanvas.WX_GL_MIN_ACCUM_ALPHA + 1
        attribList = [wx.glcanvas.WX_GL_RGBA, wx.glcanvas.WX_GL_DOUBLEBUFFER, wx.glcanvas.WX_GL_SAMPLE_BUFFERS, 1, wx.glcanvas.WX_GL_DEPTH_SIZE, 16, 0, 0]
        wx.glcanvas.GLCanvas.__init__(self, parent, id, wx.DefaultPosition, wx.DefaultSize, style, "", attribList)

        self.network = network
        if self.network is not None:
            self.network.addDisplay(self)
        self.displayRules = []
        self.autoVisualize = True
        self.visibles = {}
        self.visibleIds = {}
        self.selectedVisibles = []
        self.highlightedVisibles = []
        self.animatedVisibles = []
        self.selectConnectedVisibles = True
        self._showRegionNames = True
        self._showNeuronNames = False
        self._showFlow = False
        self._useGhosts = False
        self._primarySelectionColor = (0, 0, 1, .25)
        self._secondarySelectionColor = (0, 0, 1, .125)
        self.viewDimensions = 2
        self.visiblesMin = [-100, -100, -100]
        self.visiblesMax = [100, 100, 100]
        self.visiblesCenter = [0, 0, 0]
        self.visiblesSize = [200, 200, 200]
        self.orthoCenter = (0, 0)
        self.zoomScale = 1
        self.orthoZoom = 0
        self.rootNode = osg.MatrixTransform()
        self.rootNode.setMatrix(osg.Matrixd.identity())
        self.rootNode.getOrCreateStateSet().setMode(osg.GL_NORMALIZE, osg.StateAttribute.ON )
        if platform.system() == 'Windows':
            self.scrollWheelScale = 0.1
        else:
            self.scrollWheelScale = 1
        
        osg.DisplaySettings.instance().setNumMultiSamples(4);
        
        self.trackball = osgGA.TrackballManipulator()
        self._pickHandler = PickHandler(self)
        
        self.viewer2D = osgViewer.Viewer()
        self.viewer2D.setThreadingModel(self.viewer2D.SingleThreaded)
        self.viewer2D.addEventHandler(osgViewer.StatsHandler())
        self.viewer2D.setSceneData(self.rootNode)
        self.viewer2D.addEventHandler(self._pickHandler)
        light = self.viewer2D.getLight()
        light.setAmbient(osg.Vec4f(0.4, 0.4, 0.4, 1))
        light.setDiffuse(osg.Vec4f(0.5, 0.5, 0.5, 1))
        
        self.viewer3D = osgViewer.Viewer()
        self.viewer3D.setThreadingModel(self.viewer3D.SingleThreaded)
        self.viewer3D.addEventHandler(osgViewer.StatsHandler())
        self.viewer3D.setSceneData(self.rootNode)
        self.viewer3D.setCameraManipulator(self.trackball)
        self.viewer3D.addEventHandler(self._pickHandler)
        self.viewer3D.setLight(light)
        
        config = wx.Config("Neuroptikon")
        clearColor = (config.ReadFloat("Color/Background/Red", 0.7), \
                      config.ReadFloat("Color/Background/Green", 0.8), \
                      config.ReadFloat("Color/Background/Blue", 0.7), \
                      config.ReadFloat("Color/Background/Alpha", 1.0))
        self.setBackgroundColor(clearColor)
        
        self.Bind(wx.EVT_SIZE, self.onSize)
        self.Bind(wx.EVT_PAINT, self.onPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.onEraseBackground)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.onMouseEvent)  # TODO: factor this out into individual events
        self.Bind(wx.EVT_MOUSEWHEEL, self.onMouseWheel)
        self.Bind(wx.EVT_SCROLLWIN, self.onScroll)
        
        self._motionTexture1 = self.textureFromImage('texture.png')
        self._motionTexture2 = self.textureFromImage('texture.png')
        self._pathwayTexture = self.textureFromImage('pathway.jpg')
        self._textureTransform = osg.Matrixd.scale(10 / 5000.0,  10 / 5000.0,  10 / 5000.0)
        self.animationPhaseUniform = osg.Uniform('animationPhase', 0.0)
        self.rootNode.getOrCreateStateSet().addUniform(self.animationPhaseUniform)
        
        self.dragSelection = None
        self.draggerLOD = None
        self.simpleDragger = None
        self.compositeDragger = None
        self.activeDragger = None
        
        self.selectionShouldExtend = False
        self.findShortestPath = False
        
        self.useHoverSelect = False
        self.hoverSelect = True
        self.hoverSelecting = False
        self.hoverSelected = False  # set to True if the current selection was made by hovering
        
        width, height = self.GetClientSize()
        self.graphicsWindow = self.viewer2D.setUpViewerAsEmbeddedInWindow(0, 0, width, height)
        
        self.SetDropTarget(DisplayDropTarget(self))
    
        self._nextUniqueId = -1
        
        dispatcher.connect(self.onSelectionChanged, ('set', 'selection'), self)
    
    
    def fromXMLElement(self, xmlElement):
        visibleElements = xmlElement.findall('Visible')
        
        # Add all of the nodes
        for visibleElement in visibleElements:
            if visibleElement.find('path') is None:
                visible = Visible.fromXMLElement(visibleElement, self)
                if visible is None:
                    raise ValueError, gettext('Could not create visualized item')
                self.addVisible(visible)
                
        # Add all of the paths (must be done after nodes are added)
        for visibleElement in visibleElements:
            if visibleElement.find('path') is not None:
                visible = Visible.fromXMLElement(visibleElement, self)
                if visible is None:
                    raise ValueError, gettext('Could not create visualized item')
                self.addVisible(visible)
        
        self.computeVisiblesBound()
        
        self.setViewDimensions(int(xmlElement.get('dimensions')))
        
        showRegionNames = xmlElement.get('showRegionNames')
        if showRegionNames is not None:
            self.setShowRegionNames(showRegionNames == 'true')
        showNeuronNames = xmlElement.get('showNeuronNames')
        if showNeuronNames is not None:
            self.setShowNeuronNames(showNeuronNames == 'true')
        showFlow = xmlElement.get('showFlow')
        if showFlow is not None:
            self.setShowFlow(showFlow == 'true')
        
        selectedVisibleIds = xmlElement.get('selectedVisibleIds')
        if selectedVisibleIds is not None:
            for visibleId in selectedVisibleIds.split(','):
                if visibleId in self.visibleIds:
                    self.selectVisible(visibleId, extend = True)
        
        self.resetView()
        
        # TODO: all other display attributes
    
    
    def toXMLElement(self, parentElement):
        displayElement = ElementTree.SubElement(parentElement, 'Display')
        for displayRule in self.displayRules:
            ruleElement = displayRule.toXMLElement(displayElement)
            if ruleElement is None:
                raise ValueError, gettext('Could not save display rule')
        for visibles in self.visibles.itervalues():
            for visible in visibles:
                if visible.parent is None:
                    visibleElement = visible.toXMLElement(displayElement)
                    if visibleElement is None:
                        raise ValueError, gettext('Could not save visualized item')
        displayElement.set('dimensions', str(self.viewDimensions))
        # TODO: it would be nice to save the console command history
        return displayElement
    
    
    def nextUniqueId(self):
        self._nextUniqueId += 1
        return self._nextUniqueId
    
    
    def textureFromImage(self, imageName):
        image = osgDB.readImageFile("Display" + os.sep + imageName)
        texture = osg.Texture2D()
        texture.setFilter(osg.Texture2D.MIN_FILTER, osg.Texture2D.LINEAR);
        texture.setFilter(osg.Texture2D.MAG_FILTER, osg.Texture2D.LINEAR);
        texture.setImage(image)
        texture.setWrap(osg.Texture2D.WRAP_S,  osg.Texture2D.REPEAT)
        texture.setWrap(osg.Texture2D.WRAP_T,  osg.Texture2D.REPEAT)
        texture.setWrap(osg.Texture2D.WRAP_R,  osg.Texture2D.REPEAT)
        return texture
    
    
    def setViewDimensions(self, dimensions):
        if dimensions != self.viewDimensions:
            self.viewDimensions = dimensions
            width, height = self.GetClientSize()
#            self.deselectAll()
            if self.viewDimensions == 2:
                # TODO: approximate the 3D settings?
                self.graphicsWindow = self.viewer2D.setUpViewerAsEmbeddedInWindow(0, 0, width, height)
                self.viewer2D.setCameraManipulator(None)
                self.resetView()
            elif self.viewDimensions == 3:
                # TODO: approximate the 2D settings
#                self.viewer3D.getCamera().setViewport(osg.Viewport(0, 0, width, height))
                self.graphicsWindow = self.viewer3D.setUpViewerAsEmbeddedInWindow(0, 0, width, height)
                self.viewer3D.getCamera().setProjectionMatrixAsPerspective(30.0, width / height, 1.0, 10000.0)
                self.centerView()
            self.Refresh()
    
    
    def onViewIn2D(self, event):
        self.setViewDimensions(2)
    
    
    def onViewIn3D(self, event):
        self.setViewDimensions(3)
    
    
    def setUseStereo(self, useStereo):
        settings = self.viewer3D.getDisplaySettings()
        
        if useStereo:
            if settings is None:
                settings = osg.DisplaySettings()
                self.viewer3D.setDisplaySettings(settings)
            settings.setStereo(True)
            settings.setStereoMode(osg.DisplaySettings.ANAGLYPHIC)
        elif settings is not None:
            settings.setStereo(False)
    
    
    def resetView(self):
        if self.viewDimensions == 2:
            width, height = self.GetClientSize()
            zoom = 2.0 ** (self.orthoZoom / 10.0)
            self.viewer2D.getCamera().setProjectionMatrixAsOrtho2D(self.orthoCenter[0] - width * self.zoomScale / 2.0 / zoom, 
                                                                   self.orthoCenter[0] + width * self.zoomScale / 2.0 / zoom, 
                                                                   self.orthoCenter[1] - height * self.zoomScale / 2.0 / zoom, 
                                                                   self.orthoCenter[1] + height * self.zoomScale / 2.0 / zoom)
            self.viewer2D.getCamera().setViewMatrix(osg.Matrixd.translate(osg.Vec3d(0, 0, -2.0)))
            self.SetScrollbar(wx.HORIZONTAL, (self.orthoCenter[0] - self.visiblesMin[0]) / self.visiblesSize[0] * width - width / zoom / 2.0, width / zoom, width, True)
            self.SetScrollbar(wx.VERTICAL, (self.visiblesMax[1] - self.orthoCenter[1]) / self.visiblesSize[1] * height - height / zoom / 2.0, height / zoom, height, True)
    
    
    def computeVisiblesBound(self):
        # This:
        #     boundingSphere = node.getBound()
        #     sphereCenter = boundingSphere.center()
        # computes a screwy center.  Because there's no camera?
        # Manually compute the bounding box instead.
        # TODO: figure out how to let the faster C++ code do this
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
        self.visiblesCenter = ((self.visiblesMin[0] + self.visiblesMax[0]) / 2.0, (self.visiblesMin[1] + self.visiblesMax[1]) / 2.0, (self.visiblesMin[2] + self.visiblesMax[2]) / 2.0)
        self.visiblesSize = (self.visiblesMax[0] - self.visiblesMin[0], self.visiblesMax[1] - self.visiblesMin[1], self.visiblesMax[2] - self.visiblesMin[2])
            
        width, height = self.GetClientSize()
        xZoom = self.visiblesSize[0] / (width - 10.0)
        yZoom = self.visiblesSize[1] / (height - 10.0)
        if xZoom > yZoom:
            self.zoomScale = xZoom
        else:
            self.zoomScale = yZoom
    
    
    def centerView(self, visible=None):
        if visible is None:
            node = self.rootNode
        else:
            node = visible.sgNode
        
        self.computeVisiblesBound()
        
        if self.viewDimensions == 2:
            self.orthoCenter = (self.visiblesCenter[0], self.visiblesCenter[1])
            self.orthoZoom = 0
            self.resetView()
        elif self.viewDimensions == 3:
            self.trackball.setNode(node)
            self.trackball.computeHomePosition()
            self.viewer3D.home()
            self.trackball.setRotation(osg.Quat(0, 0, 0, 1))
        
        #osgDB.writeNodeFile(self.rootNode, "test.osg");
    
        
    def onCenterView(self, event):
        self.centerView()
    
    
    def onScroll(self, event):
        width, height = self.GetClientSize()
        zoom = 2 ** (self.orthoZoom / 10.0)
        if event.GetOrientation() == wx.HORIZONTAL:
            # Reverse the calculation in resetView():
            # pos = (self.orthoCenter[0] - self.visiblesMin[0]) / self.visiblesSize[0] * width - width / zoom / 2
            # pos + width / zoom / 2 = (self.orthoCenter[0] - self.visiblesMin[0]) / self.visiblesSize[0] * width
            # (pos + width / zoom / 2) * self.visiblesSize[0] / width = self.orthoCenter[0] - self.visiblesMin[0]
            self.orthoCenter = ((event.GetPosition() + width / zoom / 2.0) / width * self.visiblesSize[0] + self.visiblesMin[0], self.orthoCenter[1])
        else:
            # Reverse the calculation in resetView():
            # pos = (self.visiblesMax[1] - self.orthoCenter[1]) / self.visiblesSize[1] * height - height / zoom / 2
            # pos + height / zoom / 2 = (self.visiblesMax[1] - self.orthoCenter[1]) / self.visiblesSize[1] * height
            # (pos + height / zoom / 2) * self.visiblesSize[1] / height = self.visiblesMax[1] - self.orthoCenter[1]
            self.orthoCenter = (self.orthoCenter[0], self.visiblesMax[1] - (event.GetPosition() + height / zoom / 2.0) * self.visiblesSize[1] / height)
        self.resetView()
        self.Refresh()
   
   
    def setBackgroundColor(self, color):
        self.viewer2D.getCamera().setClearColor(osg.Vec4(*color))
        self.viewer3D.getCamera().setClearColor(osg.Vec4(*color))
        self.backgroundColor = color
    
        
    def onMouseEvent(self, event):
        if event.ButtonDown():
            self.selectionShouldExtend = event.ShiftDown()
            self.findShortestPath = event.AltDown()
            self.graphicsWindow.getEventQueue().mouseButtonPress(event.GetX(), event.GetY(), event.GetButton())
        elif event.ButtonUp():
            self.graphicsWindow.getEventQueue().mouseButtonRelease(event.GetX(), event.GetY(), event.GetButton())
        elif event.Dragging():
            self.graphicsWindow.getEventQueue().mouseMotion(event.GetX(), event.GetY())
        elif event.Moving() and self.useHoverSelect and self.hoverSelect:
            self.hoverSelecting = True
            self.graphicsWindow.getEventQueue().mouseButtonPress(event.GetX(), event.GetY(), wx.MOUSE_BTN_LEFT)
            self.graphicsWindow.getEventQueue().mouseButtonRelease(event.GetX(), event.GetY(), wx.MOUSE_BTN_LEFT)
        self.Refresh()
    
    
    def onMouseWheel(self, event):
        if self.viewDimensions == 2:
            if event.ShiftDown():
                self.orthoCenter = (self.orthoCenter[0] + event.GetWheelRotation() * .002, self.orthoCenter[1])
            elif event.AltDown():
                self.orthoCenter = (self.orthoCenter[0], self.orthoCenter[1] - event.GetWheelRotation() * 10.0)
            else:
                self.orthoZoom += event.GetWheelRotation() * self.scrollWheelScale
                if self.orthoZoom < 0:
                    self.orthoZoom = 0
                # TODO: alter orthoCenter to keep visibles in view
            self.resetView()
        elif self.viewDimensions == 3:
            self.trackball.setDistance(self.trackball.getDistance() - event.GetWheelRotation() * .02 * self.scrollWheelScale)
        self.Refresh()
    
    
    def onIdle(self, event):
        # TODO: limit this to 30 fps
        
        # TODO: does setting the animation phase this way limit the slowest speed an animation can be?
        self.animationPhaseUniform.set(datetime.now().microsecond / 1000000.0)
        
        self.Refresh()
        event.RequestMore()
    
    
    def onEraseBackground(self, event):
        pass
    
    
    def onSize(self, event):
        w, h = self.GetClientSize()
        
        if self.GetParent().IsShown():
            self.SetCurrent()

        if self.graphicsWindow.valid():
            self.graphicsWindow.getEventQueue().windowResize(0, 0, w, h)
            self.graphicsWindow.resized(0, 0, w, h)
        
        self.resetView()
            
        event.Skip()
    
    
    def onPaint(self, event):
        wx.PaintDC(self)
        
        if self.GetContext() != 0 and self.graphicsWindow.valid():
            self.SetCurrent()
            if self.viewDimensions == 2:
                self.viewer2D.frame()
            else:
                self.viewer3D.frame()
            self.SwapBuffers()
    
    
    def GetConvertedKeyCode(self,evt):
        """in wxWidgets, key is always an uppercase
           if shift is not pressed convert to lowercase
        """
        key = evt.GetKeyCode()
        if key >=ord('A') and key <= ord('Z'):
            if not evt.ShiftDown():
                key += 32
        return key
    
    
    def OnKeyDown(self, event):
        key = self.GetConvertedKeyCode(event)
        self.graphicsWindow.getEventQueue().keyPress(key)
        event.Skip()
    
    
    def OnKeyUp(self, event):
        key = self.GetConvertedKeyCode(event)
        self.graphicsWindow.getEventQueue().keyRelease(key)
        event.Skip()
    
    
    def visiblesForObject(self, object):
        return self.visibles[object.networkId] if object and object.networkId in self.visibles else []
    
    
    def addVisible(self, visible, parentVisible = None):
        if visible.client is not None:
            if visible.client.networkId in self.visibles:
                self.visibles[visible.client.networkId].append(visible)
            else:
                self.visibles[visible.client.networkId] = [visible]
        self.visibleIds[visible.displayId] = visible
        if parentVisible is None:
            self.rootNode.addChild(visible.sgNode)
        else:
            parentVisible.addChildVisible(visible)
    
    
    def visualizeObject(self, object):
        # TODO: replace this whole block with display rules
        neuralTissueColor = (0.85, 0.75, 0.6)
        if isinstance(object, Region):
            visible = Visible(self, object)
            visible.setShape("box")
            visible.setSize((0.1, 0.1, 0.01))
            visible.setColor(neuralTissueColor)
            if self._showRegionNames:
                visible.setLabel(object.abbreviation or object.name)
            parentVisibles = self.visiblesForObject(object.parentRegion)
            self.addVisible(visible, parentVisibles[0] if len(parentVisibles) == 1 else None)
            for subRegion in object.subRegions:
                subVisibles = self.visiblesForObject(subRegion)
                if len(subVisibles) == 1:
                    self.rootNode.removeChild(subVisibles[0].sgNode)
                    visible.addChildVisible(subVisibles[0])
            for neuron in object.neurons:
                neuronVisibles = self.visiblesForObject(neuron)
                if len(neuronVisibles) == 1:
                    self.rootNode.removeChild(neuronVisibles[0].sgNode)
                    visible.addChildVisible(neuronVisibles[0])
        elif isinstance(object, Pathway):
            region1 = self.visiblesForObject(object.terminus1.region)
            region2 = self.visiblesForObject(object.terminus2.region)
            if len(region1) == 1 and len(region2) == 1:
                visible = Visible(self, object)
                visible.setShape("tube")
                visible.setWeight(5.0)
                visible.setColor(neuralTissueColor)
                visible.setTexture(self._pathwayTexture)
                visible.setTextureTransform(osg.Matrixd.scale(-10,  10,  1))
                visible.setFlowDirection(region1[0], region2[0], False, False)
                visible.setPath([], region1[0], region2[0])
                self.addVisible(visible)
        elif isinstance(object, Neuron):
            visible = Visible(self, object)
            visible.setShape("ball")
            visible.setSize((.01, .01, .01))
            visible.setSizeIsAbsolute(True)
            visible.setColor(neuralTissueColor)
            if self._showNeuronNames:
                visible.setLabel(object.abbreviation or object.name)
            regionVisibles = self.visiblesForObject(object.region)
            self.addVisible(visible, regionVisibles[0] if len(regionVisibles) == 1 else None)
            #TODO: dispatcher.connect(self.neuronRegionChanged, ('set', 'region'), object)
        elif isinstance(object, Muscle):
            visible = Visible(self, object)
            visible.setShape('capsule')
            visible.setSize((.1, .2, .02))
            visible.setColor((0.5, 0, 0))
            visible.setTexture(self._pathwayTexture)
            visible.setTextureTransform(osg.Matrixd.scale(-10,  10,  1))
            visible.setLabel(object.name)
            self.addVisible(visible)
        elif isinstance(object, Arborization):
            neuronVis = self.visiblesForObject(object.neurite.neuron())
            regionVis = self.visiblesForObject(object.region)
            if len(neuronVis) == 1 and len(regionVis) == 1:
                visible = Visible(self, object)
                visible.setShape("tube")
                visible.setColor(neuralTissueColor)
                visible.setFlowDirection(neuronVis[0], regionVis[0], object.sendsOutput, object.receivesInput)
                visible.setPath([], neuronVis[0], regionVis[0])
                if self._showFlow:
                    visible.animateFlow()
                dispatcher.connect(self.arborizationChangedFlow, ('set', 'sendsOutput'), object)
                dispatcher.connect(self.arborizationChangedFlow, ('set', 'receivesInput'), object)
                self.addVisible(visible)
        elif isinstance(object, Synapse):
            preNeuronVis = self.visiblesForObject(object.preSynapticNeurite.neuron())
            if len(preNeuronVis) == 1:
                for neurite in object.postSynapticNeurites:
                    postNeuronVis = self.visiblesForObject(neurite.neuron())
                    if len(preNeuronVis) == 1:
                        visible = Visible(self, object)
                        visible.setShape("tube")
                        visible.setColor(neuralTissueColor)
                        visible.setFlowDirection(preNeuronVis[0], postNeuronVis[0])
                        visible.setPath([], preNeuronVis[0], postNeuronVis[0])
                        if self._showFlow:
                            visible.animateFlow()
                        self.addVisible(visible)
        elif isinstance(object, GapJunction):
            neurites = list(object.neurites)
            neuron1 = self.visiblesForObject(neurites[0].neuron())
            neuron2 = self.visiblesForObject(neurites[1].neuron())
            if len(neuron1) == 1 and len(neuron2) == 1:
                visible = Visible(self, object)
                visible.setShape("tube")
                visible.setColor((.65, 0.75, 0.4))
                visible.setFlowDirection(neuron1[0], neuron2[0], True, True)
                visible.setPath([], neuron1[0], neuron2[0])
                self.addVisible(visible)
        elif isinstance(object, Innervation):
            neuronVis = self.visiblesForObject(object.neurite.neuron())
            muscleVis = self.visiblesForObject(object.muscle)
            if len(neuronVis) == 1 and len(muscleVis) == 1:
                visible = Visible(self, object)
                visible.setShape("tube")
                visible.setColor((0.55, 0.35, 0.25))
                visible.setFlowDirection(neuronVis[0], muscleVis[0])
                visible.setPath([], neuronVis[0], muscleVis[0])
                if self._showFlow:
                    visible.animateFlow()
                self.addVisible(visible)
        elif isinstance(object, Stimulus):
            targetVis = self.visiblesForObject(object.target)
            if len(targetVis) == 1:
                nodeVis = Visible(self, object)
                nodeVis.setSize((.02, .02, .02)) # so the label is in front (hacky...)
                nodeVis.setLabel(object.abbreviation or object.name)
                self.addVisible(nodeVis)
                edgeVis = Visible(self, object)
                edgeVis.setShape("cone")
                edgeVis.setWeight(5)
                edgeVis.setColor((0.5, 0.5, 0.5))
                edgeVis.setFlowDirection(nodeVis, targetVis[0])
                edgeVis.setPath([], nodeVis, targetVis[0])
                if self._showFlow:
                    edgeVis.animateFlow()
                self.addVisible(edgeVis)
    
    
    def arborizationChangedFlow(self, signal, sender):
        arborizationVis = self.visiblesForObject(sender)
        neuronVis = self.visiblesForObject(sender.neurite.neuron())
        regionVis = self.visiblesForObject(sender.region)
        if len(arborizationVis) == 1 and len(neuronVis) == 1 and len(regionVis == 1):
            arborizationVis.setFlowDirection(neuronVis[0], regionVis[0], sender.sendsOutput, sender.receivesInput)
    
        
    def setNetwork(self, network):
        if self.network != None:
            self.network.removeDisplay(self)
            # TODO: anything else?
        
        self.network = network
        
        if network is not None:
            self.network.addDisplay(self)
            
            if self.autoVisualize:
                for object in network.objects:
                    self.visualizeObject(object)
            
            try:
                dispatcher.connect(receiver=self.networkChanged, signal=dispatcher.Any, sender=self.network)
            except DispatcherTypeError:
                raise    #TODO
    
    
    def networkChanged(self, affectedObjects=None, **arguments):
        signal = arguments["signal"]
        if signal == 'addition' and self.autoVisualize:
            for object in affectedObjects:
                self.visualizeObject(object)
            self.Refresh()
        elif signal == 'deletion':
            # TODO: untested
            for object in affectedObjects:
                visibles = self.visiblesForObject(object)
                # TODO: remove the visibles from the scene graph
        else:
            pass    # TODO: anything?
    
    
    def neuronRegionChanged(self, signal, sender):
        # TODO: untested method
        visible = self.visibleForObject(sender)
        if visible.parent is not None:
            visible.parent.removeChildVisible(visible)
        if neuron.region is not None:
            newParent = self.visibleForObject(neuron.region)
            if newParent is not None:
                newParent.addChildVisible(visible)
    
    
    def setShowRegionNames(self, flag):
        if flag != self._showRegionNames:
            for visibles in self.visibles.itervalues():
                for visible in visibles:
                    if isinstance(visible, Visible) and isinstance(visible.client, Region):
                        if flag:
                            visible.setLabel(visible.client.name)
                        else:
                            visible.setLabel(None)
            self._showRegionNames = flag
    
    
    def showRegionNames(self):
        return self._showRegionNames
    
    
    def setShowNeuronNames(self, flag):
        if flag != self._showNeuronNames:
            for visibles in self.visibles.itervalues():
                for visible in visibles:
                    if isinstance(visible, Visible) and isinstance(visible.client, Neuron):
                        if flag:
                            visible.setLabel(visible.client.name)
                        else:
                            visible.setLabel(None)
            self._showNeuronNames = flag
    
    
    def showNeuronNames(self):
        return self._showNeuronNames
    
    
    def setShowFlow(self, flag):
        if flag != self._showFlow:
            for visibles in self.visibles.itervalues():
                for visible in visibles:
                    if visible.flowTo or visible.flowFrom:
                        visible.animateFlow(flag)
            self._showFlow = flag
    
    
    def showFlow(self):
        return self._showFlow
    
    
    def setUseGhosts(self, flag):
        if flag != self._useGhosts:
            self._useGhosts = flag
            if len(self.selectedVisibles) > 0:
                for visibles in self.visibles.itervalues():
                    for visible in visibles:
                        if self._useGhosts and visible not in self.highlightedVisibles and visible not in self.animatedVisibles:
                            visible.setOpacity(0.1)
                        else:
                            visible.setOpacity(1)
    
    
    def useGhosts(self):
        return self._useGhosts
    
    
    def setLabel(self, object, label):
        visibles = self.visiblesForObject(object)
        if len(visibles) == 1:
            visibles[0].setLabel(label)
    
    
    def setVisiblePosition(self, object, position, fixed=False):
        visibles = self.visiblesForObject(object)
        if len(visibles) == 1:
            visibles[0].setPosition(position)
            visibles[0].setPositionIsFixed(fixed)
    
    
    def setVisibleSize(self, object, size, fixed=True, absolute=False):
        visibles = self.visiblesForObject(object)
        if len(visibles) == 1:
            visibles[0].setSize(size)
            visibles[0].setSizeIsFixed(fixed)
            visibles[0].setSizeIsAbsolute(absolute)
    
    
    def setVisibleColor(self, object, color):
        visibles = self.visiblesForObject(object)
        if len(visibles) == 1:
            visibles[0].setColor(color)
    
    
    def setArrangedAxis(self, object, axis = 'largest', recurse = False):
        visibles = self.visiblesForObject(object)
        if len(visibles) == 1:
            visibles[0].setArrangedAxis(axis = axis, recurse = recurse)
    
    
    def setArrangedSpacing(self, object, spacing = .02, recurse = False):
        visibles = self.visiblesForObject(object)
        if len(visibles) == 1:
            visibles[0].setArrangedSpacing(spacing = spacing, recurse = recurse)
    
    
    def setArrangedWeight(self, object, weight):
        visibles = self.visiblesForObject(object)
        if len(visibles) == 1:
            visibles[0].setArrangedWeight(weight)
    
    
    def visibleChild(self, object, index):
        visibles = self.visiblesForObject(object)
        if len(visibles) == 1:
            if index < len(visibles[0].children):
                visible = visibles[0].children[index]
            else:
                visible = None
        if visible is None:
            return None
        else:
            return visible.client
        # TODO: should probably be returning the visible itself...
    
    
    def setVisiblePath(self, object, path, startVisible, endVisible):
        visibles = self.visiblesForObject(object)
        if len(visibles) == 1:
            visibles[0].setPath(path, startVisible, endVisible)
    
    
    def selectObjectsMatching(self, predicate):
        self.deselectAll(False)
        for object in self.network.objects:
            if predicate.matches(object):
                for visible in self.visiblesForObject(object):
                    self.selectVisible(visible, extend = True)
    
    
    def selectObject(self, object, extend = False, findShortestPath = False):
        for visible in self.visiblesForObject(object):
            self.selectVisible(visible, extend, findShortestPath)
    
    
    def objectIsSelected(self, object):
        for visible in self.visiblesForObject(object):
            if visible in self.selectedVisibles:
                return True
        return False
    
    
    def selectVisible(self, visible, extend = False, findShortestPath = False):
        self.clearDragger()
        if visible is None:
            self.deselectAll(report = False)
        else:
            if extend and findShortestPath and len(self.selectedVisibles) == 1:
                # Add the visibles that exist along the path to the selection.
                for pathObject in self.selectedVisibles[0].client.shortestPathTo(visible.client):
                    pathVisibles = self.visiblesForObject(pathObject)
                    if len(pathVisibles) == 1:
                        self.selectVisible(pathVisible[0], extend = True)
                return
            
            if not extend or visible not in self.selectedVisibles or (self.hoverSelected and not self.hoverSelecting):
                # Alter the visible to be selected in certain cases
                if visible.isPath():
                    if isinstance(visible.client, Stimulus):
                        # Always select the stimulus's node visible, not its path visible.
                        visible = visible.pathStart
                    elif visible not in self.highlightedVisibles and visible not in self.animatedVisibles:
                        # Select an arborization's, gap junction's or synapse's neuron instead, unless the neuron is already selected.
                        if isinstance(visible.client, Arborization) or isinstance(visible.client, GapJunction):
                            if isinstance(visible.pathStart.client, Neuron):
                                visible = visible.pathStart
                            elif isinstance(visible.pathEnd.client, Neuron):
                                visible = visible.pathEnd
                        elif isinstance(visible.client, Synapse):
                            preSynapticNeuron = visible.client.preSynapticNeurite.neuron()
                            if visible.pathStart.client == preSynapticNeuron:
                                visible = visible.pathStart
                            elif visible.pathEnd.client == preSynapticNeuron:
                                visible = visible.pathEnd
                
                if not extend:
                    self.deselectAll(report = False)
                
                self.hoverSelected = self.hoverSelecting
                self.hoverSelecting = False
                
                # Strongly highlight the selected visible.
                # TODO: highlighting should be done via display filters
                self.selectedVisibles.append(visible)
                visible.setGlowColor(self._primarySelectionColor)
                
                # Make sure the selected visible does not look ghosted.
                if self._useGhosts:
                    visible.setOpacity(1)
                
            elif extend and visible in self.selectedVisibles:
                # Remove the visible from the selection
                self.selectedVisibles.remove(visible)
        
        dispatcher.send(('set', 'selection'), self)
        
        if len(self.selectedVisibles) == 0:
            self.hoverSelect = True
            self.hoverSelected = False
        else:
            if not self.hoverSelected:
                self.hoverSelect = False
            if len(self.selectedVisibles) == 1:
                if not self.hoverSelected:
                    # Add a dragger to the selected visible.
                    visible = self.selectedVisibles[0]
                    if visible.isDraggable():
                        self.addDragger(visible)
    
    
    def selection(self):
        selection = ObjectList()
        for visible in self.selectedVisibles:
            selection.append(visible)
        return selection
    
    
    def selectedObjects(self):
        selection = set()
        for visible in self.selectedVisibles:
            if visible.client is not None:
                selection.add(visible.client)
        return list(selection)
    
    
    def selectAll(self, report = True):
        self.deselectAll(report = False)
        for visibles in self.visibles.itervalues():
            for visible in visibles:
                self.selectedVisibles.append(visible)
        dispatcher.send(('set', 'selection'), self)
        
    
    def deselectAll(self, report = True):
        self.clearDragger()
        self.selectedVisibles = []
        
        self.hoverSelected = False
        self.hoverSelect = True
        
        if report:
            dispatcher.send(('set', 'selection'), self)
    
    
    def onSelectionChanged(self, signal, sender):
        # Update the highlighting, animation and ghosting based on the current selection.
        # TODO: this should all be handled by display rules which will also keep ghosting from blowing away opacity settings
        
        wasAnimating = (len(self.animatedVisibles) > 0)
        
        visiblesToHighlight = set()
        visiblesToAnimate = set()
        for visible in self.selectedVisibles:
            visiblesToHighlight.add(visible)
            if visible.isPath():
                # Highlight the visibles at each end of the path.
                if visible.flowTo or visible.flowFrom:
                    visiblesToAnimate.add(visible)
                visiblesToHighlight.add(visible.pathStart) 
                visiblesToHighlight.add(visible.pathEnd)
            else:
                singleSelection = (len(self.selectedVisibles) == 1)
                if self.selectConnectedVisibles:
                    # Animate paths connecting to this non-path visible and highlight the other end of the paths.
                    for pathVisible in visible.connectedPaths:
                        otherVis = pathVisible.pathEnd if pathVisible.pathStart == visible else pathVisible.pathStart
                        if singleSelection or otherVis in self.selectedVisibles:
                            visiblesToAnimate.add(pathVisible)
                            visiblesToHighlight.add(otherVis)
                        
                        # If a single region is selected then extend the highlight to include the arborized regions of any neuron that arborizes this region.
                        if isinstance(visible.client, Region) and isinstance(otherVis.client, Neuron):
                            for pathVisible2 in otherVis.connectedPaths:
                                if pathVisible2 != pathVisible and isinstance(pathVisible2.client, Arborization):
                                    region2Vis = pathVisible2.pathEnd if pathVisible2.pathStart == otherVis else pathVisible2.pathStart
                                    if region2Vis.client == pathVisible2.client.region and (singleSelection or region2Vis in self.selectedVisibles) and ((pathVisible.flowTo and pathVisible2.flowFrom) or (pathVisible.flowFrom and pathVisible2.flowTo)):
                                        visiblesToHighlight.add(otherVis)
                                        visiblesToAnimate.add(pathVisible2)
                                        visiblesToHighlight.add(region2Vis)
        
        # Turn off highlighting/animating for visibles that shouldn't have it anymore.
        for highlightedNode in self.highlightedVisibles:
            if highlightedNode not in visiblesToHighlight:
                highlightedNode.setGlowColor(None)
        for animatedEdge in self.animatedVisibles:
            if animatedEdge not in visiblesToAnimate:
                animatedEdge.animateFlow(False)
        
        # Highlight/animate the visibles that should have it now.
        for visibleToHighlight in visiblesToHighlight:
            if visibleToHighlight in self.selectedVisibles:
                visibleToHighlight.setGlowColor(self._primarySelectionColor)
            else:
                visibleToHighlight.setGlowColor(self._secondarySelectionColor)
            visibleToHighlight.setOpacity(1)
        for visibleToAnimate in visiblesToAnimate:
            visibleToAnimate.animateFlow()
            visibleToAnimate.setOpacity(1)
        self.highlightedVisibles = visiblesToHighlight
        self.animatedVisibles = visiblesToAnimate
        
        if self._useGhosts:
            if len(self.selectedVisibles) > 0:
                # Dim everything that isn't selected, highlighted or animated.
                for visibles in self.visibles.itervalues():
                    for visible in visibles:
                        ghost = True
                        ancestors = [visible]
                        ancestors.extend(visible.ancestors())
                        for ancestor in ancestors:
                            if ancestor in self.highlightedVisibles or ancestor in self.animatedVisibles:
                                ghost = False
                        if ghost:
                            visible.setOpacity(0.1)
            else:
                # Restore all visibles to full opacity.
                for visibles in self.visibles.itervalues():
                    for visible in visibles:
                        visible.setOpacity(1)
        
        # Turn idle callbacks on when any visible is animated and off otherwise.
        if len(self.animatedVisibles) > 0 and not wasAnimating:
            self.Bind(wx.EVT_IDLE, self.onIdle)
        elif len(self.animatedVisibles) == 0 and wasAnimating:
            self.Unbind(wx.EVT_IDLE)
    
    
    def addDragger(self, visible):
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
        if self.viewDimensions == 2:
            self.draggerZOffset = visible.size()[2]
            self.draggerScale = 1.0
            self.simpleDragger = osgManipulator.TranslatePlaneDragger()
            if not visible.sizeIsFixed():
                self.compositeDragger = osgManipulator.TabPlaneDragger()
                if visible.parent is not None and visible.sizeIsAbsolute:
                    self.draggerZOffset /= visible.parent.worldSize()[2]
                    pixelCutOff = 200.0 / visible.parent.worldSize()[0]
                else:
                    pixelCutOff = 200.0
        elif self.viewDimensions == 3:
            self.draggerZOffset = 0.0
            self.draggerScale = 1.02
            self.simpleDragger = osgManipulator.TranslateAxisDragger()
            if not visible.sizeIsFixed():
                self.compositeDragger = osgManipulator.TabBoxDragger()
                if visible.parent is not None and visible.sizeIsAbsolute:
                    pixelCutOff = 200.0 / visible.parent.worldSize()[0]
                else:
                    pixelCutOff = 200.0
        draggerMatrix = osg.Matrixd.rotate(pi / 2.0, osg.Vec3d(1, 0, 0)) * \
                        osg.Matrixd.scale(self.draggerScale, self.draggerScale, self.draggerScale) * \
                        visible.sgNode.getMatrix() * \
                        osg.Matrixd.translate(0, 0, self.draggerZOffset)
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
    
    
    def visibleWasDragged(self):
        # TODO: It would be nice to constrain dragging if the visible has a parent.  "Resistance" would be added when the child reached the parent border so that dragging slowed or stopped but if dragged far enough the child could force its way through.
        visible = self.selectedVisibles[0]
        if self.activeDragger is not None:
            matrix = self.activeDragger.getMatrix()
            position = matrix.getTrans()
            size = matrix.getScale()
            if visible.parent is None or not visible.sizeIsAbsolute:
                parentSize = (1.0, 1.0, 1.0)
            else:
                parentSize = visible.parent.worldSize()
            visible.setPosition((position.x(), position.y(), position.z() - self.draggerZOffset))
            visible.setSize((size.x() * parentSize[0] / self.draggerScale, size.y() * parentSize[1] / self.draggerScale, size.z() * parentSize[2] / self.draggerScale))
    
    
    def clearDragger(self):
        if self.dragSelection != None:
            visible = self.selectedVisibles[0]
            
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
            self.visibleWasDragged()
            
            if self.draggerLOD is not None:
                rootNode.removeChild(self.draggerLOD)
            else:
                rootNode.removeChild(self.simpleDragger)
            
            self.simpleDragger.setUpdateCallback(None)
            self.simpleDragger = None
            if self.compositeDragger is not None:
                self.compositeDragger.setUpdateCallback(None)
                self.compositeDragger = None
            self.draggerLOD = None
    
    
    def onAutoLayout(self, event):
        self.autoLayout()
    
    
    def autoLayout(self, method=None):
        """Automatically layout the displayed network without moving visibles with fixed positions (much)"""
        self.deselectAll()
        if method == 'spectral' or (method is None and self.viewDimensions == 3):
            nodes = []
            edges = []
            for visibles in self.visibles.itervalues():
                for visible in visibles:
                    if visible.isPath():
                        edges.append(visible)
                    elif visible.parent is None:
                        nodes.append(visible)
            n=len(nodes)
            if n > 0:
                A = zeros((n, n))
                for edge in edges:
                    n1 = nodes.index(edge.pathStart.rootVisible())
                    n2 = nodes.index(edge.pathEnd.rootVisible())
                    A[n1, n2] = A[n1, n2] + 1
                    if isinstance(edge.client, GapJunction):
                        A[n2, n1] = A[n2, n1] + 1
                #print A
                A_prime = A.T   #conj().transpose()?
                # This is equivalent to the MATLAB code provided by Mitya:
                #   n=size(A,1);
                #   c=full((A+A')/2);
                #   d=diag(sum(c));
                #   l=d-c;
                #   b=sum(c.*sign(full(A-A')),2);
                #   z=pinv(c)*b;
                #   q=d^(-1/2)*l*d^(-1/2);
                #   [vx,lambda]=eig(q);
                #   x=d^(-1/2)*vx(:,2);
                #   y=d^(-1/2)*vx(:,3);
                c = (A + A_prime) / 2.0
                d = diag(c.sum(0))
                l = mat(d - c)
                b = (c * sign(A - A_prime)).sum(1).reshape(1, n)
                z = inner(pinv(c), b)
                d2 = mat(d**-0.5)
                d2[isinf(d2)] = 0
                q = d2 * l * d2
                (eVal, eVec) = eigh(q)
                x = d2 * mat(eVec[:,1])
                y = d2 * mat(eVec[:,2])
                xMin, xMax = x.min(), x.max()
                xScale = 1.0 / (xMax - xMin)
                xOff = (xMax + xMin) / 2.0
                yMin, yMax = y.min(), y.max()
                yScale = 1.0 / (yMax - yMin)
                yOff = (yMax + yMin) / 2.0
                zMin, zMax = z.min(), z.max()
                zScale = 1.0 / (zMax - zMin)
                zOff = (zMax + zMin) / 2.0
                for i in range(n):
                    nodes[i].setPosition(((x[i,0] - xOff) * xScale, (y[i,0] - yOff) * yScale, (z[i,0] - zOff) * zScale))
        elif (method == 'graphviz' or (method is None and self.viewDimensions == 2)) and (pygraphviz is not None or pydot is not None):
            graphVisibles = {}
            edgeVisibles = []
            if pygraphviz is not None:  # Use pygraphviz if it's available as it's faster than pydot.
                graph = pygraphviz.AGraph(strict = False, overlap = 'vpsc', sep = '+1', splines = 'polyline')
            else:
                graph = pydot.Dot(graph_type = 'graph', overlap = 'vpsc', sep = '+1', splines = 'polyline')
            for visibles in self.visibles.itervalues():
                for visible in visibles:
                    if visible.isPath():
                        edgeVisibles.append(visible)   # don't add edges until all the nodes have been added
                    elif len(visible.children) == 0:    #visible.parent is None:
                        graphVisibles[str(visible.displayId)] = visible
                        if pygraphviz is not None:
                            graph.add_node(str(visible.displayId), **visible.graphvizAttributes())
                        else:
                            graph.add_node(pydot.Node(str(visible.displayId), **visible.graphvizAttributes()))
            for edgeVisible in edgeVisibles:
                graphVisibles[str(edgeVisible.displayId)] = edgeVisible
                if pygraphviz is not None:
                    graph.add_edge(str(edgeVisible.pathStart.displayId), str(edgeVisible.pathEnd.displayId), str(edgeVisible.displayId))
                else:
                    graph.add_edge(pydot.Edge(str(edgeVisible.pathStart.displayId), str(edgeVisible.pathEnd.displayId), tooltip = str(edgeVisible.displayId)))
            
            if pygraphviz is not None:
                #print mainGraph.to_string()
                graph.layout(prog='fdp')
                graphData = graph.to_string()
            else:
                graphData = graph.create_dot(prog='fdp')
                graph = pydot.graph_from_dot_data(graphData)
            
            # Get the bounding box of the entire graph so we can center it in the display.
            # The 'bb' attribute doesn't seem to be exposed by pygraphviz so we have to hack it out of the text dump.
            import re
            matches = re.search('bb="([0-9,]+)"', graphData)
            bbx1, bby1, bbx2, bby2 = matches.group(1).split(',')
            width, height = (float(bbx2) - float(bbx1), float(bby2) - float(bby1))
            if width > height:
                scale = 1.0 / width
            else:
                scale = 1.0 / height
            dx, dy = ((float(bbx2) + float(bbx1)) / 2.0, (float(bby2) + float(bby1)) / 2.0)
            for visibleId, visible in graphVisibles.iteritems():
                if visible.parent is None:
                    pos = None
                    if not visible.isPath():
                        if not visible.positionIsFixed():
                            # Set the position of a node
                            pos = self._graphvizNodePos(graph, visibleId)
                            if pos is not None:
                                x, y = pos.split(',') 
                                # TODO: convert to local coordinates?
                                visible.setPosition(((float(x) - dx) * scale, (float(y) - dy) * scale, 0))
                    elif False:
                        # Set the path of an edge
                        if pygraphviz is not None:
                            edge = pygraphviz.Edge(graph, str(visible.pathStart.displayId), str(visible.pathEnd.displayId))
                            if 'pos' in edge.attr:
                                pos = edge.attr['pos']
                        else:
                            pass    # TODO
                        if pos is not None:
                            (startVisX, startVisY, startVisZ) = visible.pathStart.worldPosition()
                            (endVisX, endVisY, endVisZ) = visible.pathEnd.worldPosition()
                            startPos = self._graphvizNodePos(graph, str(visible.pathStart.displayId))
                            startDotX, startDotY = startPos.split(',')
                            startDotX = float(startDotX)
                            startDotY = float(startDotY)
                            endPos = self._graphvizNodePos(graph, str(visible.pathEnd.displayId))
                            endDotX, endDotY = endPos.split(',')
                            endDotX = float(endDotX)
                            endDotY = float(endDotY)
                            scaleX = (startDotX - endDotX) / (startVisX - endVisX)
                            translateX = startDotX - scaleX * startVisX
                            scaleY = (startDotY - endDotY) / (startVisY - endVisY)
                            translateY = startDotY - scaleY * startVisY
                            path_3D = []
                            path = pos.split(' ')
                            for pathElement in path[1:-1]:
                                x, y = pathElement.split(',')
                                path_3D.append(((float(x) - translateX) / scaleX, (float(y) - translateY) / scaleY, 0))
                            visible.setPath(path_3D, visible.pathStart, visible.pathEnd)
        self.centerView()
    
    
    def _graphvizNodePos(self, graph, nodeId):
        pos = None
        if isinstance(graph, pygraphviz.AGraph):
            node = pygraphviz.Node(graph, nodeId) 
            if 'pos' in node.attr:
                pos = node.attr['pos']
        else:
            node = graph.get_node(nodeId)
            if isinstance(node, pydot.Node):
                pos = node.get_pos()[1:-1] 
        return pos
    
    
    def onSaveView(self, event):
        fileTypes = ['JPG', 'Microsoft BMP', 'PNG', 'TIFF']
        fileExtensions = ['jpg', 'bmp', 'png', 'tiff']
        wildcard = ''
        for index in range(0, len(fileTypes)):
            if wildcard != '':
                wildcard += '|'
            wildcard += fileTypes[index] + '|' + fileExtensions[index]
        fileDialog = wx.FileDialog(None, gettext('Save As:'), '', '', wildcard, wx.FD_SAVE)
        if fileDialog.ShowModal() == wx.ID_OK:
            extension = fileExtensions[fileDialog.GetFilterIndex()]
            savePath = str(fileDialog.GetPath())
            if not savePath.endswith('.' + extension):
                savePath += '.' + extension
            width, height = self.GetClientSize()
            image = osg.Image()
            self.SetCurrent()
            image.readPixels(0, 0, width, height, osg.GL_RGB, osg.GL_UNSIGNED_BYTE)
            osgDB.writeImageFile(image, savePath)
    


class DisplayDropTarget(wx.PyDropTarget):
    
    def __init__(self, display):
        wx.PyDropTarget.__init__(self)
        self.display = display

        # specify the type of data we will accept
        self.dropData = wx.CustomDataObject("Neuroptikon Ontology Term")
        self.SetDataObject(self.dropData)
    
    
    def OnData(self, x, y, dragType):
        if self.GetData():
            termData = self.dropData.GetData()
            termDict = cPickle.loads(termData)
            ontologyId = termDict['Ontology']
            termId = termDict['Term']
            
            ontology = wx.GetApp().library.ontology(ontologyId)
            if ontology is not None:
                term = ontology[termId]
                if term is not None:
                    region = self.display.network.createRegion(ontologyTerm = term, addSubTerms = wx.GetKeyState(wx.WXK_ALT))
                    # TODO: self.display.setDisplayPosition(region, ???)
                    if True:    # TODO: only if new region is the only visible
                        self.display.centerView()
            
        return dragType
    
