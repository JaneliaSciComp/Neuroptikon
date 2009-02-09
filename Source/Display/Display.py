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
from pydispatch import dispatcher
from networkx import *
from math import pi, fabs
from numpy import diag, mat, sign, inner, isinf, zeros
from numpy.linalg import pinv, eigh
import os, platform, cPickle

try:
    import pygraphviz
except ImportError:
    pygraphviz = None


class Display(wx.glcanvas.GLCanvas):
    
    def __init__(self, parent, id, x, y, width, height):
        style = wx.WANTS_CHARS | wx.FULL_REPAINT_ON_RESIZE | wx.HSCROLL | wx.VSCROLL
        if not hasattr(wx.glcanvas, "WX_GL_SAMPLE_BUFFERS"):
            wx.glcanvas.WX_GL_SAMPLE_BUFFERS = wx.glcanvas.WX_GL_MIN_ACCUM_ALPHA + 1
        attribList = [wx.glcanvas.WX_GL_RGBA, wx.glcanvas.WX_GL_DOUBLEBUFFER, wx.glcanvas.WX_GL_SAMPLE_BUFFERS, 1, wx.glcanvas.WX_GL_DEPTH_SIZE, 16, 0, 0]
        wx.glcanvas.GLCanvas.__init__(self, parent, id, wx.DefaultPosition, wx.DefaultSize, style, "", attribList)

        self.network = None
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
        
        self.dragSelection = None
        self.draggerLOD = None
        self.simpleDragger = None
        self.compositeDragger = None
        self.activeDragger = None
        
        self.selectionShouldExtend = False
        self.findShortestPath = False
        
        self.graphicsWindow = self.viewer2D.setUpViewerAsEmbeddedInWindow(0, 0, width, height)
        
        self.SetDropTarget(DisplayDropTarget(self))
    
    
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
            self.deselectAll()
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
    
    
    def centerView(self, visible=None):
        if visible is None:
            node = self.rootNode
        else:
            node = visible.sgNode
            
        # This:
        #     boundingSphere = node.getBound()
        #     sphereCenter = boundingSphere.center()
        # computes a screwy center.  Because there's no camera?
        # Manually compute the bounding box instead.
        # TODO: figure out how to let the faster C++ code do this
        self.visiblesMin = [100000, 100000, 100000]
        self.visiblesMax = [-100000, -100000, -100000]
        for visible in self.visibles.values():
            if isinstance(visible, tuple):
                x, y, z = visible[0].worldPosition()
                w, h, d = visible[0].worldSize()
            else:
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
        # Reverse the calculation in resetView():
        # self.orthoCenter[0] - width / 2 / (2 ** (self.orthoZoom / 10.0)) = minx 
        # self.orthoCenter[0] - minx = width / 2 / (2 ** (self.orthoZoom / 10.0))
        # (2 ** (self.orthoZoom / 10.0)) = width / 2 / (self.orthoCenter[0] - minx)
        # self.orthoZoom / 10.0 = math.log(width / 2 / (self.orthoCenter[0] - minx), 2)
        # self.orthoZoom = 10 * math.log(width / 2 / (self.orthoCenter[0] - minx), 2)
        width, height = self.GetClientSize()
        #xZoom = 10 * math.log((width - 10) / 2 / (self.visiblesCenter[0] - self.visiblesMin[0]), 2)
        #yZoom = 10 * math.log((height - 10) / 2 / (self.visiblesCenter[1] - self.visiblesMin[1]), 2)
        xZoom = self.visiblesSize[0] / (width - 10.0)
        yZoom = self.visiblesSize[1] / (height - 10.0)
        if xZoom > yZoom:
            self.zoomScale = xZoom
        else:
            self.zoomScale = yZoom
        
        if self.viewDimensions == 2:
            self.orthoCenter = (self.visiblesCenter[0], self.visiblesCenter[1])
            self.orthoZoom = 0
            self.resetView()
        elif self.viewDimensions == 3:
            self.trackball.setCenter(osg.Vec3d(*self.visiblesCenter)) #computeHomePosition()
            self.trackball.home(0)
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
            button = event.GetButton()
            self.graphicsWindow.getEventQueue().mouseButtonPress(event.GetX(), event.GetY(), button)
        elif event.ButtonUp():
            button = event.GetButton()
            self.graphicsWindow.getEventQueue().mouseButtonRelease(event.GetX(), event.GetY(), button)
        elif event.Dragging():
            self.graphicsWindow.getEventQueue().mouseMotion(event.GetX(), event.GetY())
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
    
    
    def keyForObject(self, object):
        if isinstance(object, Synapse):
            key = (object.presynapticNeurite, object.postsynapticNeurites[0])
        elif isinstance(object, GapJunction):
            key = list(object.neurites)
            key.sort()
            key = (key[0], key[1])
        elif isinstance(object, Innervation):
            key = (object.neurite.neuron(), object.muscle)
        else:
            key = object
        return key
    
    
    def visibleForObject(self, object, getNode=True):
        key = self.keyForObject(object)
        if key in self.visibles:
            visible = self.visibles[key]
            if isinstance(visible, tuple):
                if getNode:
                    visible = visible[0]
                else:
                    visible = visible[1]
            return visible
        else:
            return None
    
    
    def addVisible(self, visible, object, parentVisible = None):
        self.visibles[self.keyForObject(object)] = visible
        if isinstance(visible, tuple):
            self.visibleIds[id(visible[0])] = visible[1]
            self.visibleIds[id(visible[1])] = visible[1]
        else:
            self.visibleIds[id(visible)] = visible
        if parentVisible is None:
            if isinstance(visible, tuple):
                for subVisible in visible:
                    self.rootNode.addChild(subVisible.sgNode)
            else:
                self.rootNode.addChild(visible.sgNode)
        else:
            parentVisible.addChildVisible(visible)
    
    
    def visualizeObject(self, object):
        visible = self.visibleForObject(object)
        if visible == None:
            # TODO: replace this whole block with display filters
            neuralTissueColor = (0.85, 0.75, 0.6)
            if isinstance(object, Region):
                visible = Visible(self, object)
                visible.setShape("box")
                visible.setSize((0.1, 0.1, 0.01))
                visible.setColor(neuralTissueColor)
                if self._showRegionNames:
                    visible.setLabel(object.abbreviation or object.name)
                self.addVisible(visible, object, self.visibleForObject(object.parentRegion))
            elif isinstance(object, Pathway):
                visible = Visible(self, object)
                visible.setShape("tube")
                visible.setWeight(5.0)
                visible.setColor(neuralTissueColor)
                visible.setTexture(self._pathwayTexture)
                visible.setTextureTransform(osg.Matrixd.scale(-10,  10,  1))
                regions = list(object.regions)
                region1 = self.visibleForObject(regions[0])
                region2 = self.visibleForObject(regions[1])
                visible.setFlowDirection(region1, region2, False, False)
                visible.setPath([region1.position, region2.position], region1, region2)
                self.addVisible(visible, object)
            elif isinstance(object, Neuron):
                visible = Visible(self, object)
                visible.setShape("ball")
                visible.setSize((.01, .01, .01))
                visible.setSizeIsAbsolute(True)
                visible.setColor(neuralTissueColor)
                if self._showNeuronNames:
                    visible.setLabel(object.abbreviation or object.name)
                self.addVisible(visible, object, self.visibleForObject(object.region))
            elif isinstance(object, Muscle):
                visible = Visible(self, object)
                visible.setShape('capsule')
                visible.setSize((.1, .2, .02))
                visible.setColor((0.5, 0, 0))
                visible.setTexture(self._pathwayTexture)
                visible.setTextureTransform(osg.Matrixd.scale(-10,  10,  1))
                visible.setLabel(object.name)
                self.addVisible(visible, object)
            elif isinstance(object, Arborization):
                visible = Visible(self, object)
                visible.setShape("tube")
                visible.setColor(neuralTissueColor)
                neuronVis = self.visibleForObject(object.neurite.neuron())
                regionVis = self.visibleForObject(object.region)
                visible.setFlowDirection(neuronVis, regionVis, object.sendsOutput, object.receivesInput)
                dispatcher.connect(self.arborizationChangedFlow, ('set', 'sendsOutput'), object)
                dispatcher.connect(self.arborizationChangedFlow, ('set', 'receivesInput'), object)
                visible.setPath([neuronVis.position, regionVis.position], neuronVis, regionVis)
                if self._showFlow:
                    visible.animateFlow()
                self.addVisible(visible, object)
            elif isinstance(object, Synapse):
                # create one visible per post-synaptic neurite?
                preNeuronVis = self.visibleForObject(object.presynapticNeurite.neuron())
                for neurite in object.postsynapticNeurites:
                    visible = Visible(self, object)
                    visible.setShape("tube")
                    visible.setColor(neuralTissueColor)
                    postNeuronVis = self.visibleForObject(neurite.neuron())
                    visible.setFlowDirection(preNeuronVis, postNeuronVis)
                    visible.setPath([preNeuronVis.position, postNeuronVis.position], preNeuronVis, postNeuronVis)
                    if self._showFlow:
                        visible.animateFlow()
                    self.addVisible(visible, object)
            elif isinstance(object, GapJunction):
                visible = Visible(self, object)
                visible.setShape("tube")
                visible.setColor((.65, 0.75, 0.4))
                neurites = list(object.neurites)
                neuron1 = self.visibleForObject(neurites[0].neuron())
                neuron2 = self.visibleForObject(neurites[1].neuron())
                visible.setFlowDirection(neuron1, neuron2, True, True)
                visible.setPath([neuron1.position, neuron2.position], neuron1, neuron2)
                if self._showFlow:
                    visible.animateFlow()
                self.addVisible(visible, object)
            elif isinstance(object, Innervation):
                visible = Visible(self, object)
                visible.setShape("tube")
                visible.setColor((0.55, 0.35, 0.25))
                neuronVis = self.visibleForObject(object.neurite.neuron())
                muscleVis = self.visibleForObject(object.muscle)
                visible.setFlowDirection(neuronVis, muscleVis)
                visible.setPath([neuronVis.position, muscleVis.position], neuronVis, muscleVis)
                if self._showFlow:
                    visible.animateFlow()
                self.addVisible(visible, object)
            elif isinstance(object, Stimulus):
                node = Visible(self, object)
                node.setSize((.02, .02, .02)) # so the label is in front (hacky...)
                node.setLabel(object.abbreviation or object.name)
                edge = Visible(self, object)
                edge.setShape("cone")
                edge.setWeight(5)
                edge.setColor((0.5, 0.5, 0.5))
                edge.setFlowDirection(node, self.visibleForObject(object.target))
                edge.setPath([node.position, self.visibleForObject(object.target).position], node, self.visibleForObject(object.target))
                if self._showFlow:
                    edge.animateFlow()
                self.addVisible((node, edge), object)
        elif isinstance(object, Synapse) or isinstance(object, GapJunction):
            pass    #visible.setWeight(visible.weight() + 1)
    
    
    def arborizationChangedFlow(self, signal, sender):
        visible = self.visibleForObject(sender)
        neuronVis = self.visibleForObject(sender.neurite.neuron())
        regionVis = self.visibleForObject(sender.region)
        visible.setFlowDirection(neuronVis, regionVis, sender.sendsOutput, sender.receivesInput)
    
        
    def setNetwork(self, network):
        if self.network != None:
            self.network.removeDisplay(self)
            # TODO: anything else?
        
        self.network = network
        self.network.addDisplay(self)
        
        if network != None:
            for object in network.objects:
                visualizeObject(object)
            try:
                dispatcher.connect(receiver=self.networkChanged, signal=dispatcher.Any, sender=self.network)
            except DispatcherTypeError:
                pass    #TODO
    
    
    def networkChanged(self, affectedObjects=None, **arguments):
        signal = arguments["signal"]
        if signal == 'addition':
            for object in affectedObjects:
                self.visualizeObject(object)
        elif signal == 'deletion':
            # TODO: untested
            for object in affectedObjects:
                visible = self.visibleForObject(object)
                # TODO: remove the visible from the scene graph
        else:
            pass    # TODO: anything?
    
    
    def setShowRegionNames(self, flag):
        if flag != self._showRegionNames:
            for key, visible in self.visibles.iteritems():
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
            for key, visible in self.visibles.iteritems():
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
            for key, visible in self.visibles.iteritems():
                if isinstance(visible, tuple):
                    visible = visible[1]
                if isinstance(visible.client, Arborization) or isinstance(visible.client, Synapse) or isinstance(visible.client, GapJunction) or isinstance(visible.client, Stimulus) or isinstance(visible.client, Innervation):
                    visible.animateFlow(flag)
            self._showFlow = flag
    
    
    def showFlow(self):
        return self._showFlow
    
    
    def setUseGhosts(self, flag):
        if flag != self._useGhosts:
            self._useGhosts = flag
            if len(self.selectedVisibles) > 0:
                for key, visible in self.visibles.iteritems():
                    if isinstance(visible, Visible):
                        if self._useGhosts and visible not in self.highlightedVisibles and visible not in self.animatedVisibles:
                            visible.setOpacity(0.1)
                        else:
                            visible.setOpacity(1)
    
    
    def useGhosts(self):
        return self._useGhosts
    
    
    def setLabel(self, object, label):
        visible = self.visibleForObject(object)
        visible.setLabel(label)
    
    
    def setVisiblePosition(self, object, position, fixed=False):
        visible = self.visibleForObject(object)
        visible.setPosition(position)
        visible.setPositionIsFixed(fixed)
    
    
    def setVisibleSize(self, object, size):
        visible = self.visibleForObject(object)
        visible.setSize(size)
    
    
    def setArrangedAxis(self, object, axis = 'largest', recurse = False):
        visible = self.visibleForObject(object)
        visible.setArrangedAxis(axis = axis, recurse = recurse)
    
    
    def setArrangedSpacing(self, object, spacing = .02, recurse = False):
        visible = self.visibleForObject(object)
        visible.setArrangedSpacing(spacing = spacing, recurse = recurse)
    
    
    def setArrangedWeight(self, object, weight):
        visible = self.visibleForObject(object)
        visible.setArrangedWeight(weight)
    
    
    def visibleChild(self, object, index):
        visible = self.visibleForObject(object)
        if visible is not None:
            if index < len(visible.children):
                visible = visible.children[index]
            else:
                visible = None
        if visible is None:
            return None
        else:
            return visible.client
    
    
    def setVisiblePath(self, object, path, startVisible, endVisible):
        visible = self.visibleForObject(object, False)
        visible.setPath(path, startVisible, endVisible)
    
    
    def highlightObject(self, object, highlight=True):
        visible = self.visibleForObject(object)
        if highlight:
            if visible not in self.highlightedVisibles:
                visible.setGlowColor(self._secondarySelectionColor)
                visible.setOpacity(1)
                self.highlightedVisibles.append(visible)
        else:
            if visible in self.highlightedVisibles:
                visible.setGlowColor(None)
                self.highlightedVisibles.remove(visible)
            else:
                visible = self.visibleForObject(object, False)
                if visible in self.highlightedVisibles:
                    visible.setGlowColor(None)
                    self.highlightedVisibles.remove(visible)
    
    
    def animateObjectFlow(self, object, animate=True):
        wasAnimating = (len(self.animatedVisibles) > 0)
        
        visible = self.visibleForObject(object)
        if animate:
            if visible not in self.animatedVisibles:
                visible.animateFlow()
                visible.setOpacity(1)
                self.animatedVisibles.append(visible)
        else:
            if visible in self.animatedVisibles:
                visible.animateFlow(False)
                self.animatedVisibles.remove(visible)
            else:
                visible = self.visibleForObject(object, False)
                if visible in self.animatedVisibles:
                    visible.animateFlow(False)
                    self.animatedVisibles.remove(visible)
        
        if len(self.animatedVisibles) > 0 and not wasAnimating:
            self.Bind(wx.EVT_IDLE, self.onIdle)
        elif len(self.animatedVisibles) == 0 and wasAnimating:
            self.Unbind(wx.EVT_IDLE)
    
    
    def selectObjectsMatching(self, predicate):
        self.deselectAll(False)
        for object in self.network.objects:
            if predicate.matches(object):
                visible = self.visibleForObject(object)
                if visible is not None:
                    self.selectVisible(visible, extend = True)
    
    
    def selectObject(self, object, extend = False, findShortestPath = False):
        visible = self.visibleForObject(object, False)
        self.selectVisible(visible, extend, findShortestPath)
    
    
    def objectIsSelected(self, object):
        visible = self.visibleForObject(object)
        return visible in self.selectedVisibles
    
    
    def selectVisible(self, visible, extend = False, findShortestPath = False):
        self.clearDragger()
        if visible is None:
            self.deselectAll(report = False)
        else:
            object = visible.client
            if extend and findShortestPath and len(self.selectedVisibles) == 1:
                # Add the visibles that exist along the path to the selection.
                for pathObject in self.selectedVisibles[0].client.shortestPathTo(object):
                    pathVisible = self.visibleForObject(pathObject)
                    if pathVisible is not None:
                        self.selectVisible(pathVisible, extend = True)
                return
                
            if not extend or visible not in self.selectedVisibles:
                if isinstance(object, Arborization) and not self.objectIsSelected(object.neurite.neuron()):
                    object = object.neurite.neuron()
                elif isinstance(object, Synapse) and not self.objectIsSelected(object.presynapticNeurite.neuron()):
                    object = object.presynapticNeurite.neuron()
                elif isinstance(object, GapJunction) and not self.objectIsSelected(list(object.neurites)[0].neuron()):
                    object = list(object.neurites)[0].neuron()
                if not extend:
                    self.deselectAll(report = False)
                # TODO: highlight via display filters
                # TODO: handle stimulus tuple
                self.selectedVisibles.append(visible)
                visible.setGlowColor(self._primarySelectionColor)
                self.highlightedVisibles.append(visible)
                if self._useGhosts:
                    visible.setOpacity(1)
                if isinstance(object, Region) and self.selectConnectedVisibles:
                    for arborization in object.arborizations:
                        neuron = arborization.neurite.neuron()
                        if not extend or self.objectIsSelected(neuron):
                            self.animateObjectFlow(arborization)
                            self.highlightObject(neuron)
                        for secondaryArborization in neuron.arborizations():
                            if secondaryArborization != arborization and (arborization.sendsOutput and secondaryArborization.receivesInput) or (arborization.receivesInput and secondaryArborization.sendsOutput):
                                if not extend or self.objectIsSelected(secondaryArborization.region):
                                    self.animateObjectFlow(arborization)
                                    self.highlightObject(neuron)
                                    self.animateObjectFlow(secondaryArborization)
                                    self.highlightObject(secondaryArborization.region)
                        # TODO: synapses too?
                elif isinstance(object, Pathway):
                    for region in object.regions:
                        self.highlightObject(region)
                elif isinstance(object, Neuron):
                    for synapse in object.incomingSynapses():
                        if not extend or self.objectIsSelected(synapse.presynapticNeurite.neuron()):
                            self.animateObjectFlow(synapse)
                            if self.selectConnectedVisibles:
                                self.highlightObject(synapse.presynapticNeurite.neuron())
                    for synapse in object.outgoingSynapses():
                        if not extend or self.objectIsSelected(synapse.postsynapticNeurites[0].neuron()):
                            self.animateObjectFlow(synapse)
                            if self.selectConnectedVisibles:
                                self.highlightObject(synapse.postsynapticNeurites[0].neuron())
                    for arborization in object.arborizations():
                        if not extend or self.objectIsSelected(arborization.region):
                            self.animateObjectFlow(arborization)
                            if self.selectConnectedVisibles:
                                self.highlightObject(arborization.region)
                    for gapJunction in object.gapJunctions():
                        neurites = list(gapJunction.neurites)
                        if neurites[0].neuron() == object:
                            adjacentNeuron = neurites[1].neuron()
                        else:
                            adjacentNeuron = neurites[0].neuron()
                        if not extend or self.objectIsSelected(adjacentNeuron):
                            self.animateObjectFlow(gapJunction)
                            if self.selectConnectedVisibles:
                                self.highlightObject(adjacentNeuron)
                    for innervation in object.innervations():
                        if not extend or self.objectIsSelected(innervation.muscle):
                            self.animateObjectFlow(innervation)
                            if self.selectConnectedVisibles:
                                self.highlightObject(innervation.muscle)
                elif isinstance(object, Stimulus):
                    visible = self.visibleForObject(object, False)
                    visible.setGlowColor(self._secondarySelectionColor)
                    self.highlightedVisibles.append(visible)
                    visible.animateFlow()
                    self.animatedVisibles.append(visible)
                elif isinstance(object, Muscle):
                    for innervation in object.innervations:
                        self.animateObjectFlow(innervation)
                        if self.selectConnectedVisibles:
                            self.highlightObject(innervation.neurite.neuron())
                if self.selectConnectedVisibles:
                    for stimulus in object.stimuli:
                        visible = self.visibleForObject(stimulus, False)
                        visible.setGlowColor(self._secondarySelectionColor)
                        self.highlightedVisibles.append(visible)
                        visible.animateFlow()
                        self.animatedVisibles.append(visible)
            elif extend and visible in self.selectedVisibles:
                self.selectedVisibles.remove(visible)
                if len(self.selectedVisibles) == 1:
                    self.selectVisible(self.selectedVisibles[0])
                    return
                else:
                    self.highlightObject(object, False)
        
        dispatcher.send(('set', 'selection'), self)
        
        # Update visible attributes based on the new selection.
        if len(self.selectedVisibles) == 1:
            # Add a dragger to the selected visible.
            visible = self.selectedVisibles[0]
            if isinstance(visible.client, Stimulus):
                visible = self.visibleForObject(visible.client)
            
            if visible.isDraggable():
                self.addDragger(visible)
        elif len(self.selectedVisibles) > 1:
            # Turn off highlighting/animation for visibles that aren't selected or that aren't direct connections between the selected visibles.
            tempList = list(self.highlightedVisibles)
            for highlightedVisible in tempList:
                if highlightedVisible not in self.selectedVisibles:
                    highlightedObject = highlightedVisible.client
                    removeHighlight = True
                    if isinstance(highlightedObject, Region):
                        pass
                    elif isinstance(highlightedObject, Neuron):
                        inputs = []
                        outputs = []
                        for arborization in highlightedObject.arborizations():
                            if self.objectIsSelected(arborization.region):
                                if arborization.receivesInput:
                                   inputs.append(arborization.region)
                                if arborization.sendsOutput:
                                   outputs.append(arborization.region)
                        if len(inputs) > 0 and len(outputs) > 0 and inputs != outputs:
                            removeHighlight = False
                    if removeHighlight:
                        self.highlightObject(highlightedObject, False)
            tempList = list(self.animatedVisibles)
            for animatedVisible in tempList:
                removeAnimation = False
                animatedObject = animatedVisible.client
                if isinstance(animatedObject, Arborization):
                    removeAnimation = True
                    if self.objectIsSelected(animatedObject.region):
                        if self.objectIsSelected(animatedObject.neurite.neuron()) and animatedObject.sendsOutput and animatedObject.receivesInput:
                            removeAnimation = False
                        else:
                            neuron = animatedObject.neurite.neuron()
                            for secondaryArborization in neuron.arborizations():
                                if secondaryArborization != animatedObject and self.objectIsSelected(secondaryArborization.region) and \
                                    ((animatedObject.sendsOutput and secondaryArborization.receivesInput) or (animatedObject.receivesInput and secondaryArborization.sendsOutput)):
                                    removeAnimation = False
                elif isinstance(animatedObject, Synapse):
                    if not self.objectIsSelected(animatedObject.presynapticNeurite.neuron()) or not self.objectIsSelected(animatedObject.postsynapticNeurites[0].neuron()):
                        removeAnimation = True
                elif isinstance(animatedObject, GapJunction):
                    neurites = list(animatedObject.neurites)
                    if not self.objectIsSelected(neurites[0].neuron()) or not self.objectIsSelected(neurites[1].neuron()):
                        removeAnimation = True
                if removeAnimation:
                    self.animateObjectFlow(animatedObject, False)
        
        if self._useGhosts:
            # Dim everything that isn't selected or connected to the selection.
            for key, visible in self.visibles.iteritems():
                if isinstance(visible, Visible):
                    ghost = True
                    ancestors = [visible]
                    ancestors.extend(visible.ancestors())
                    for ancestor in ancestors:
                        if ancestor in self.highlightedVisibles or ancestor in self.animatedVisibles:
                            ghost = False
                    if ghost:
                        visible.setOpacity(0.1)
    
    
    def selection(self):
        selection = ObjectList()
        for visible in self.selectedVisibles:
            if isinstance(visible, tuple):
                selection.append(visible[0])    #stimulus tuple
            else:
                selection.append(visible)
        return selection
    
    
    def selectAll(self, report = True):
        self.deselectAll(report = False)
        for visible in self.visibles.itervalues():
            if isinstance(visible, tuple):
                visible = visible[1]    #stimulus tuple
            
            self.selectedVisibles.append(visible)
            visible.setGlowColor(self._primarySelectionColor)
            self.highlightedVisibles.append(visible)
            visible.setOpacity(1)
            if visible.pathStart is not None:
                visible.animateFlow()
                self.animatedVisibles.append(visible)
        dispatcher.send(('set', 'selection'), self)
            
        
    
    def deselectAll(self, report = True):
        self.clearDragger()
        while len(self.highlightedVisibles) > 0:
            self.highlightObject(self.highlightedVisibles[0].client, False)
        while len(self.animatedVisibles) > 0:
            self.animateObjectFlow(self.animatedVisibles[0].client, False)
        self.selectedVisibles = []
        
        if self._useGhosts:
            # Restore all visibles to full opacity.
            for key, visible in self.visibles.iteritems():
                if isinstance(visible, Visible):
                    visible.setOpacity(1)
        
        if report:
            dispatcher.send(('set', 'selection'), self)
    
    
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
        
        if self.viewDimensions == 2:
            self.draggerZOffset = visible.size()[2]
            self.draggerScale = 1.0
            self.simpleDragger = osgManipulator.TranslatePlaneDragger()
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
        
        self.commandMgr = osgManipulator.CommandManager()
        self.commandMgr.connect(self.simpleDragger, self.dragSelection)
        self.commandMgr.connect(self.compositeDragger, self.dragSelection)
        
        # TODO: observe the visible's 'positionIsFixed' attribute and add/remove the draggers as needed
    
    
    def visibleWasDragged(self):
        # TODO: It would be nice to constrain dragging if the visible has a parent.  "Resistance" would be added when the child reached the parent border so that dragging slowed or stopped but if dragged far enough the child could force its way through.
        visible = self.selectedVisibles[0]
        if isinstance(visible.client, Stimulus):
            visible = self.visibleForObject(visible.client)
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
            if isinstance(visible.client, Stimulus):
                visible = self.visibleForObject(visible.client)
            
            if visible.parent is None:
                rootNode = self.rootNode
            else:
                rootNode = visible.parent.childGroup
            
            self.commandMgr.disconnect(self.simpleDragger)
            self.commandMgr.disconnect(self.compositeDragger)
            self.commandMgr = None
            
            self.dragSelection.removeChild(visible.sgNode)
            rootNode.removeChild(self.dragSelection)
            self.dragSelection = None
            
            rootNode.addChild(visible.sgNode)
            self.visibleWasDragged()
            
            rootNode.removeChild(self.draggerLOD)
            
            self.simpleDragger.setUpdateCallback(None)
            self.simpleDragger = None
            self.compositeDragger.setUpdateCallback(None)
            self.compositeDragger = None
            self.draggerLOD = None
    
    
    def onAutoLayout(self, event):
        self.autoLayout()
    
    
    def autoLayout(self, method="graphviz"):
        """Automatically layout the displayed network without moving visibles with fixed positions (much)"""
        self.deselectAll()
        graph = self.network.graph
        if method == "spectral-mitya":
            nodes = graph.nodes()
            n=len(nodes)
            A = zeros((n, n))
            for edge in graph.edges():
                n1 = nodes.index(edge[0])
                n2 = nodes.index(edge[1])
                A[n1, n2] = A[n1, n2] + 1
                if isinstance(edge[2], GapJunction):
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
                node = nodes[i]
                visible = self.visibleForObject(self.network.objectWithId(node))
                if isinstance(visible, tuple):
                    visible = visible[0]
                #visible.setPosition((x[i,0], y[i,0], z[i,0]))
                visible.setPosition(((x[i,0] - xOff) * xScale, (y[i,0] - yOff) * yScale, (z[i,0] - zOff) * zScale))
            visitedEdges = []
            for edge in graph.edges():
                edgeVisible = self.visibleForObject(edge[2], False)
                if edgeVisible not in visitedEdges:
                    path_3D = []
                    visible0 = self.visibleForObject(self.network.objectWithId(edge[0]))
                    visible1 = self.visibleForObject(self.network.objectWithId(edge[1]))
                    path_3D.append(visible0.position())
                    path_3D.append(visible1.position())
                    self.setVisiblePath(edge[2], path_3D, visible0, visible1)
                    visitedEdges.append(edgeVisible)
        elif method == "spectral":
            layout = drawing.layout.spectral_layout(graph, dim=3)
            #print layout
            for node in graph.nodes(): 
                visible = self.visibleForObject(self.network.objectWithId(node))
                position = layout[node]
                visible.setPosition((position[0]*100.0, position[1]*100.0, position[2]*100.0))
            for edge in graph.edges():
                path_3D = []
                visible0 = self.visibleForObject(self.network.objectWithId(edge[0]))
                visible1 = self.visibleForObject(self.network.objectWithId(edge[1]))
                path_3D.append(visible0.position())
                path_3D.append(visible1.position())
                self.setVisiblePath(edge[2], path_3D, visible0, visible1)
        elif method == "graphviz":
            visibles = {}
            edgeVisibles = []
            if pygraphviz is not None:  # Use pygraphviz if it's available as it's faster than pydot.
                mainGraph = pygraphviz.AGraph(strict = False, overlap = 'vpsc', sep = '+1', splines = 'polyline')
                for key, visible in self.visibles.iteritems():
                    if isinstance(visible, tuple):
                        visibles[str(id(visible[0]))] = visible[0]
                        mainGraph.add_node(id(visible[0]), **visible[0].graphvizAttributes())
                        edgeVisibles.append(visible[1])
                    else:
                        if visible.pathStart is not None:
                            edgeVisibles.append(visible)   # don't add edges until all the nodes have been added
                        elif len(visible.children) == 0:    #visible.parent is None:
                            visibles[str(id(visible))] = visible
                            mainGraph.add_node(id(visible), **visible.graphvizAttributes())
                for edgeVisible in edgeVisibles:
                    visibles[str(id(edgeVisible))] = edgeVisible
                    if True:
                        mainGraph.add_edge(str(id(edgeVisible.pathStart)), str(id(edgeVisible.pathEnd)), str(id(edgeVisible)))
                    else:
                        startKey = str(id(edgeVisible.pathStart.rootVisible()))
                        endKey = str(id(edgeVisible.pathEnd.rootVisible()))
                        edgeAttrs = {}
                        if edgeVisible.pathStart.parent is not None:
                            worldX, worldY, worldZ = edgeVisible.pathStart.worldPosition()
                            rootX, rootY, rootZ = edgeVisible.pathStart.rootVisible().position()
                            rootWidth, rootHeight, rootDepth = edgeVisible.pathStart.rootVisible().size()
                            subX = int((worldX - rootX) / rootWidth * 9.0) + 4
                            subY = int((worldY - rootY) / rootHeight * 9.0) + 4
                            startKey += ':' + str(subX) + str(subY)
                            edgeAttrs['tailport'] = str(subX) + str(subY)
                        if edgeVisible.pathEnd.parent is not None:
                            worldX, worldY, worldZ = edgeVisible.pathEnd.worldPosition()
                            rootX, rootY, rootZ = edgeVisible.pathEnd.rootVisible().position()
                            rootWidth, rootHeight, rootDepth = edgeVisible.pathEnd.rootVisible().size()
                            subX = int((worldX - rootX) / rootWidth * 9.0) + 4
                            subY = int((worldY - rootY) / rootHeight * -9.0) + 4
                            edgeAttrs['headport'] = str(subX) + str(subY)
                        mainGraph.add_edge(startKey, endKey, str(id(edgeVisible)), **edgeAttrs)
                
                #print mainGraph.to_string()
                mainGraph.layout(prog='fdp')
                
                # Get the bounding box of the entire graph so we can center it in the display.
                # The 'bb' attribute doesn't seem to be exposed by pygraphviz so we have to hack it out of the text dump.
                import re
                matches = re.search('bb="([0-9,]+)"', mainGraph.to_string())
                bbx1, bby1, bbx2, bby2 = matches.group(1).split(',')
                width, height = (float(bbx2) - float(bbx1), float(bby2) - float(bby1))
                dx, dy = ((float(bbx2) + float(bbx1)) / 2.0, (float(bby2) + float(bby1)) / 2.0)
                for visibleId in mainGraph.nodes():
                    visible = visibles[visibleId]
                    if visible.parent is None:
                        pynode = pygraphviz.Node(mainGraph, visibleId) 
                        try: 
                            x, y = pynode.attr['pos'].split(',') 
                            # TODO: convert to local coordinates?
                            visible.setPosition(((float(x) - dx) / width, (float(y) - dy) / height, 0))
                        except: 
                            pass
                for edge in mainGraph.edges():
                    try:
                        path_3D = []
                        pathStart = visibles[edge[0]]
                        pathEnd = visibles[edge[1]]
                        visible = visibles[edge[2]]
                        if False:
                           pyedge = pygraphviz.Edge(mainGraph, edge[0], edge[1])
                           path = pyedge.attr['pos'].split(' ')
                           for pathElement in path:
                              x, y = pathElement.split(',')
                              path_3D.append(((float(x) - dx) / width, (float(y) - dy) / height, 0))
                        else:
                            path_3D.append(pathStart.worldPosition())
                            path_3D.append(pathEnd.worldPosition())
                        visible.setPath(path_3D, visible.pathStart, visible.pathEnd)
                    except:
                        pass
            else:  # Fall back to using pydot.
                pydotGraph = self.network.to_pydot(graph_attr=graphAttr, node_attr=nodeAttr)
                if pydotGraph is not None:
                    graphData = pydotGraph.create_dot(prog='fdp')
                    pydotGraph = pydot.graph_from_dot_data(graphData)
                    for node in graph.nodes(): 
                       visible = self.visibleForObject(self.network.objectWithId(node))
                       pyNode = pydotGraph.get_node(str(node))
                       pos = pyNode.get_pos()[1:-1] 
                       if pos != None:
                          x, y = pos.split(',')
                          visible.setPosition((float(x), float(y), 0))
                    # TODO: extract path segments
        self.centerView()
    
    
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
    
