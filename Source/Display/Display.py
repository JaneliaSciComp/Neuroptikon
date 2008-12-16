import wx
import wx.glcanvas
import osg, osgDB, osgFX, osgGA, osgManipulator, osgViewer
from PickHandler import PickHandler
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
from Visible import Visible
from pydispatch import dispatcher
from networkx import *
from math import pi, fabs
from numpy import zeros, diag, mat, sign, inner, isinf
from numpy.linalg import pinv, eigh
import os

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
        self.selectedObjects = []
        self.highlightedObjects = []
        self.animatedObjects = []
        self.selectAdjacentObjects = True
        self._showRegionNames = True
        self._showNeuronNames = False
        self._showFlow = False
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
        
        if False:
            lightGroup = osg.Group()
            light = osg.Light()
            light.setLightNum(1)
            light.setPosition(osg.Vec4f(0, 0, -1000, 1))
            light.setAmbient(osg.Vec4f(0.2, 0.2, 0.2, 1))
            light.setDiffuse(osg.Vec4f(0.1, 0.1, 0.1, 1))
            #light.setConstantAttenuation(1)
            lightSource = osg.LightSource()
            lightSource.setLight(light)
            lightSource.setLocalStateSetModes(osg.StateAttribute.ON)
            lightSource.setStateSetModes(self.rootNode.getOrCreateStateSet(), osg.StateAttribute.ON)
            lightGroup.addChild(lightSource)
            self.rootNode.addChild(lightGroup)
        
        osg.DisplaySettings.instance().setNumMultiSamples(4);
        
        self.trackball = osgGA.TrackballManipulator()
        self._pickHandler = PickHandler(self)
        
        self.viewer2D = osgViewer.Viewer()
        self.viewer2D.setThreadingModel(self.viewer2D.SingleThreaded)
        self.viewer2D.addEventHandler(osgViewer.StatsHandler())
        self.viewer2D.setSceneData(self.rootNode)
#        self.viewer2D.setCameraManipulator(self.trackball)
#        self.viewer2D.setCameraManipulator(None)
        self.viewer2D.addEventHandler(self._pickHandler)
        self.viewer2D.getCamera().setClearColor(osg.Vec4(0.7, 0.8, 0.7, 1))
#        self.viewer2D.getCamera().setComputeNearFarMode(osg.CullSettings.COMPUTE_NEAR_FAR_USING_BOUNDING_VOLUMES)
        
        self.viewer3D = osgViewer.Viewer()
        self.viewer3D.setThreadingModel(self.viewer3D.SingleThreaded)
        self.viewer3D.addEventHandler(osgViewer.StatsHandler())
        self.viewer3D.setSceneData(self.rootNode)
        self.viewer3D.setCameraManipulator(self.trackball)
        self.viewer3D.addEventHandler(self._pickHandler)
        self.viewer3D.getCamera().setClearColor(osg.Vec4(0.7, 0.8, 0.7, 1))
        
        self.Bind(wx.EVT_SIZE, self.onSize)
        self.Bind(wx.EVT_PAINT, self.onPaint)
        self.Bind(wx.EVT_IDLE, self.onIdle)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.onEraseBackground)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.onMouseEvent)  # TODO: factor this out into individual events
        self.Bind(wx.EVT_MOUSEWHEEL, self.onMouseWheel)
        self.Bind(wx.EVT_SCROLLWIN, self.onScroll)
        
        self._motionTexture1 = self.textureFromImage('texture.png')
        self._motionTexture2 = self.textureFromImage('texture.png')
        self._pathwayTexture = self.textureFromImage('pathway.jpg')
        self._textureTransform = osg.Matrixd.scale(10,  10,  10)
        self.selection = None
        self.selectionShouldExtend = False
        
        self.graphicsWindow = self.viewer2D.setUpViewerAsEmbeddedInWindow(0, 0, width, height)
    
    
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
    
    
    def onViewIn2D(self, event):
        self.setViewDimensions(2)
    
    
    def onViewIn3D(self, event):
        self.setViewDimensions(3)
    
    
    def resetView(self):
        if self.viewDimensions == 2:
            width, height = self.GetClientSize()
            zoom = 2 ** (self.orthoZoom / 10.0)
            self.viewer2D.getCamera().setProjectionMatrixAsOrtho2D(self.orthoCenter[0] - width * self.zoomScale / 2 / zoom, 
                                                                   self.orthoCenter[0] + width * self.zoomScale / 2 / zoom, 
                                                                   self.orthoCenter[1] - height * self.zoomScale / 2 / zoom, 
                                                                   self.orthoCenter[1] + height * self.zoomScale / 2 / zoom)
            self.viewer2D.getCamera().setViewMatrix(osg.Matrixd.translate(osg.Vec3d(0, 0, -1000)))
            self.SetScrollbar(wx.HORIZONTAL, (self.orthoCenter[0] - self.visiblesMin[0]) / self.visiblesSize[0] * width - width / zoom / 2, width / zoom, width, True)
            self.SetScrollbar(wx.VERTICAL, (self.visiblesMax[1] - self.orthoCenter[1]) / self.visiblesSize[1] * height - height / zoom / 2, height / zoom, height, True)
    
    
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
                x, y, z = visible[0].position()
                w, h, d = visible[1].size()
            else:
                x, y, z = visible.position()
                w, h, d = visible.size()
            if x - w / 2 < self.visiblesMin[0]:
                self.visiblesMin[0] = x - w / 2
            if x + w / 2 > self.visiblesMax[0]:
                self.visiblesMax[0] = x + w / 2
            if y - h / 2 < self.visiblesMin[1]:
                self.visiblesMin[1] = y - h / 2
            if y + h / 2 > self.visiblesMax[1]:
                self.visiblesMax[1] = y + h / 2
            if z - d / 2 < self.visiblesMin[2]:
                self.visiblesMin[2] = z - d / 2
            if z + d / 2 > self.visiblesMax[2]:
                self.visiblesMax[2] = z + d / 2
        self.visiblesCenter = ((self.visiblesMin[0] + self.visiblesMax[0]) / 2, (self.visiblesMin[1] + self.visiblesMax[1]) / 2, (self.visiblesMin[2] + self.visiblesMax[2]) / 2)
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
        xZoom = self.visiblesSize[0] / (width - 10)
        yZoom = self.visiblesSize[1] / (height - 10)
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
            self.orthoCenter = ((event.GetPosition() + width / zoom / 2) / width * self.visiblesSize[0] + self.visiblesMin[0], self.orthoCenter[1])
        else:
            # Reverse the calculation in resetView():
            # pos = (self.visiblesMax[1] - self.orthoCenter[1]) / self.visiblesSize[1] * height - height / zoom / 2
            # pos + height / zoom / 2 = (self.visiblesMax[1] - self.orthoCenter[1]) / self.visiblesSize[1] * height
            # (pos + height / zoom / 2) * self.visiblesSize[1] / height = self.visiblesMax[1] - self.orthoCenter[1]
            self.orthoCenter = (self.orthoCenter[0], self.visiblesMax[1] - (event.GetPosition() + height / zoom / 2) * self.visiblesSize[1] / height)
        self.resetView()
        self.Refresh()
   
    def onMouseEvent(self, event):
        if event.ButtonDown():
            if event.ShiftDown():
                self.selectionShouldExtend = True
            else:
                self.selectionShouldExtend = False
            button = event.GetButton()
            self.graphicsWindow.getEventQueue().mouseButtonPress(event.GetX(), event.GetY(), button)
        elif event.ButtonUp():
            button = event.GetButton()
            self.graphicsWindow.getEventQueue().mouseButtonRelease(event.GetX(), event.GetY(), button)
        elif event.Dragging():
            self.graphicsWindow.getEventQueue().mouseMotion(event.GetX(), event.GetY())
    
    
    def onMouseWheel(self, event):
        if self.viewDimensions == 2:
            if event.ShiftDown():
                self.orthoCenter = (self.orthoCenter[0] + event.GetWheelRotation() * 10, self.orthoCenter[1])
            elif event.AltDown():
                self.orthoCenter = (self.orthoCenter[0], self.orthoCenter[1] - event.GetWheelRotation() * 10)
            else:
                self.orthoZoom -= event.GetWheelRotation()
                if self.orthoZoom < 0:
                    self.orthoZoom = 0
                # TODO: alter orthoCenter to keep visibles in view
            self.resetView()
        elif self.viewDimensions == 3:
            self.trackball.setDistance(self.trackball.getDistance() + event.GetWheelRotation() * 100)
    
    
    def onIdle(self, event):
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
    
    
    def addVisible(self, visible, object):
        self.visibles[self.keyForObject(object)] = visible
        if isinstance(visible, tuple):
            for subVisible in visible:
                self.rootNode.addChild(subVisible.sgNode)
        else:
            self.rootNode.addChild(visible.sgNode)
        
    def visualizeObject(self, object):
        visible = self.visibleForObject(object)
        if visible == None:
            # TODO: replace this whole block with display filters
            if isinstance(object, Region):
                visible = Visible(self, object)
                visible.setShape("box")
                visible.setSize((500, 500, 100))
#                visible.setRotation((1, 0, 0, pi/2))
#                visible.setScaleOrientation((1, 0, 0, -pi/2))
                visible.setColor((0.01, 0.01, 0.01), (0.5 * 1.5, 0.39 * 1.5, 0.2 * 1.5)) #((0.1, 0.01, 0.01))
                if self._showRegionNames:
                    visible.setLabel(object.name)
                self.addVisible(visible, object)
            elif isinstance(object, Pathway):
                visible = Visible(self, object)
                visible.setShape("tube")
                visible.setWeight(5)
                visible.setColor((0.01, 0.01, 0.01), (0.5, 0.39, 0.2))
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
                visible.setSize((50, 50, 50))
                visible.setColor((0.1, 0.1, 0.1), (0.5, 0.39, 0.2))
                if self._showNeuronNames:
                    visible.setLabel(object.name)
                self.addVisible(visible, object)
            elif isinstance(object, Muscle):
                visible = Visible(self, object)
                visible.setShape("stick")
                visible.setSize((200, 1000, 100))
                visible.setColor((0.01, 0, 0), (0.5, 0, 0))
                visible.setTexture(self._pathwayTexture)
                visible.setTextureTransform(osg.Matrixd.scale(-10,  10,  1))
                visible.setLabel(object.name)
                self.addVisible(visible, object)
            elif isinstance(object, Arborization):
                visible = Visible(self, object)
                visible.setShape("tube")
                visible.setColor((0.01, 0.01, 0.01), (0.5, 0.39, 0.2))
                neuronVis = self.visibleForObject(object.neurite.neuron())
                regionVis = self.visibleForObject(object.region)
                visible.setFlowDirection(neuronVis, regionVis, object.sendsOutput, object.receivesInput)
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
                    visible.setColor((0.01, 0.01, 0.01), (0.5, 0.39, 0.2))
                    postNeuronVis = self.visibleForObject(neurite.neuron())
                    visible.setFlowDirection(preNeuronVis, postNeuronVis)
                    visible.setPath([preNeuronVis.position, postNeuronVis.position], preNeuronVis, postNeuronVis)
                    if self._showFlow:
                        visible.animateFlow()
                    self.addVisible(visible, object)
            elif isinstance(object, GapJunction):
                visible = Visible(self, object)
                visible.setShape("tube")
                visible.setColor((0, 0.1, 0), (0, 0.1, 0))
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
                visible.setColor((0.5, 0.25, 0.25), (0.5, 0.25, 0.25))
                neuronVis = self.visibleForObject(object.neurite.neuron())
                muscleVis = self.visibleForObject(object.muscle)
                visible.setFlowDirection(neuronVis, muscleVis)
                visible.setPath([neuronVis.position, muscleVis.position], neuronVis, muscleVis)
                if self._showFlow:
                    visible.animateFlow()
                self.addVisible(visible, object)
            elif isinstance(object, Stimulus):
                node = Visible(self, object)
                node.setSize((100, 100, 100)) # so the label is in front (hacky...)
                node.setLabel(object.name)
                edge = Visible(self, object)
                edge.setShape("cone")
                edge.setWeight(5)
                edge.setColor((0.01, 0.01, 0.01), (0.5, 0.5, 0.5))
                edge.setFlowDirection(node, self.visibleForObject(object.target))
                edge.setPath([node.position, self.visibleForObject(object.target).position], node, self.visibleForObject(object.target))
                if self._showFlow:
                    edge.animateFlow()
                self.addVisible((node, edge), object)
        elif isinstance(object, Synapse) or isinstance(object, GapJunction):
            pass    #visible.setWeight(visible.weight() + 1)
    
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
                if isinstance(visible.client, Region):
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
    
    def setVisiblePath(self, object, path, startVisible, endVisible):
        visible = self.visibleForObject(object, False)
        visible.setPath(path, startVisible, endVisible)
    
    def clearDragger(self):
        if self.selection != None:
            visible = self.visibleForObject(self.selectedObjects[0])
            
            self.commandMgr.disconnect(self.dragger)
            self.commandMgr = None
            
            self.selection.removeChild(visible.sgNode)
            self.rootNode.removeChild(self.selection)
            self.selection = None
            
            self.rootNode.addChild(visible.sgNode)
            self.visibleWasDragged()
            
            self.rootNode.removeChild(self.dragger)
            self.dragger = None
    
    def selectObjectsMatching(self, predicate):
        self.deselectAll()
        for object in self.network.objects:
            if predicate.matches(object):
                self.selectObject(object, True)
    
    
    def selectObject(self, object, extend=False):
        # TODO: allow a selection delegate that can modify what gets selected?  could be set via script...
        self.clearDragger()
        if object is None:
            self.deselectAll()
        else:
            if isinstance(object, Arborization) and object.neurite.neuron() not in self.selectedObjects:
                object = object.neurite.neuron()
            elif isinstance(object, Synapse) and object.presynapticNeurite.neuron() not in self.selectedObjects:
                object = object.presynapticNeurite.neuron()
            elif isinstance(object, GapJunction) and list(object.neurites)[0].neuron() not in self.selectedObjects:
                object = list(object.neurites)[0].neuron()
            #print "Selecting ", object.__class__.__name__, " ", object.name or object
            if not extend:
                self.deselectAll()
            # TODO: highlight via display filters
            # TODO: handle stimulus tuple
            self.selectedObjects.append(object)
            visible = self.visibleForObject(object, False)
            visible.setGlowColor(self._primarySelectionColor)
            self.highlightedObjects.append(visible)
            if isinstance(object, Region) and self.selectAdjacentObjects:
                for arborization in object.arborizations:
                    neuron = arborization.neurite.neuron()
                    visible = self.visibleForObject(neuron)
                    visible.setGlowColor(self._secondarySelectionColor)
                    self.highlightedObjects.append(visible)
                    for secondaryArborization in neuron.arborizations():
                        if secondaryArborization.region == object or (arborization.sendsOutput and secondaryArborization.receivesInput) or (arborization.receivesInput and secondaryArborization.sendsOutput):
                            visible = self.visibleForObject(secondaryArborization)
                            visible.animateFlow()
                            self.animatedObjects.append(visible)
                    # TODO: synapses too?
            elif isinstance(object, Pathway):
                for region in object.regions:
                    visible = self.visibleForObject(region)
                    visible.setGlowColor(self._secondarySelectionColor)
                    self.highlightedObjects.append(visible)
            elif isinstance(object, Neuron):
                for synapse in object.incomingSynapses():
                    visible = self.visibleForObject(synapse)
                    visible.animateFlow()
                    self.animatedObjects.append(visible)
                    if self.selectAdjacentObjects:
                        visible = self.visibleForObject(synapse.presynapticNeurite.neuron())
                        visible.setGlowColor(self._secondarySelectionColor)
                        self.highlightedObjects.append(visible)
                for synapse in object.outgoingSynapses():
                    visible = self.visibleForObject(synapse)
                    visible.animateFlow()
                    self.animatedObjects.append(visible)
                    if self.selectAdjacentObjects:
                        visible = self.visibleForObject(synapse.postsynapticNeurites[0].neuron())
                        visible.setGlowColor(self._secondarySelectionColor)
                        self.highlightedObjects.append(visible)
                for arborization in object.arborizations():
                    visible = self.visibleForObject(arborization)
                    visible.animateFlow()
                    self.animatedObjects.append(visible)
                    if self.selectAdjacentObjects:
                        visible = self.visibleForObject(arborization.region)
                        visible.setGlowColor(self._secondarySelectionColor)
                        self.highlightedObjects.append(visible)
                for gapJunction in object.gapJunctions():
                    visible = self.visibleForObject(gapJunction)
                    visible.animateFlow()
                    self.animatedObjects.append(visible)
                    if self.selectAdjacentObjects:
                        neurites = list(gapJunction.neurites)
                        if neurites[0].neuron() == object:
                            adjacentNeuron = neurites[1].neuron()
                        else:
                            adjacentNeuron = neurites[0].neuron()
                        visible = self.visibleForObject(adjacentNeuron)
                        visible.setGlowColor(self._secondarySelectionColor)
                        self.highlightedObjects.append(visible)
                for innervation in object.innervations():
                    visible = self.visibleForObject(innervation)
                    visible.animateFlow()
                    self.animatedObjects.append(visible)
                    if self.selectAdjacentObjects:
                        visible = self.visibleForObject(innervation.muscle)
                        visible.setGlowColor(self._secondarySelectionColor)
                        self.highlightedObjects.append(visible)
            elif isinstance(object, Stimulus):
                visible = self.visibleForObject(object, False)
                visible.setGlowColor(self._secondarySelectionColor)
                self.highlightedObjects.append(visible)
                visible.animateFlow()
                self.animatedObjects.append(visible)
            elif isinstance(object, Muscle):
                for innervation in object.innervations:
                    visible = self.visibleForObject(innervation)
                    visible.animateFlow()
                    self.animatedObjects.append(visible)
                    if self.selectAdjacentObjects:
                        visible = self.visibleForObject(innervation.neurite.neuron())
                        visible.setGlowColor(self._secondarySelectionColor)
                        self.highlightedObjects.append(visible)
        if self.selectAdjacentObjects:
            for stimulus in object.stimuli:
                visible = self.visibleForObject(stimulus, False)
                visible.setGlowColor(self._secondarySelectionColor)
                self.highlightedObjects.append(visible)
                visible.animateFlow()
                self.animatedObjects.append(visible)
            
        wx.GetApp().inspector.inspectObjects(self, self.selectedObjects)    # TODO: factor this so wx.GetApp() doesn't have to be called, something like "self.app.inspector.inspectObject()"...
        
        if len(self.selectedObjects) == 1:
            visible = self.visibleForObject(self.selectedObjects[0])
            
            if visible.isDraggable():
                self.rootNode.removeChild(visible.sgNode)
                
                self.selection = osgManipulator.Selection()
                self.selection.addChild(visible.sgNode)
                self.rootNode.addChild(self.selection)
                
                self.dragger = osgManipulator.TranslatePlaneDragger()   # TODO: use a different dragger for 3D
                self.dragger.setupDefaultGeometry()
                # TODO: should scale so that increase in size is fixed and greater than glow increase (14).  Probably should use a ComputeBoundsVisitor...
                self.draggerZOffset = visible.size()[2]
                self.dragger.setMatrix(osg.Matrixd.rotate(pi/2, osg.Vec3d(1, 0, 0)) * visible.sgNode.getMatrix() * osg.Matrixd.translate(0, 0, self.draggerZOffset))
                self.rootNode.addChild(self.dragger)
                
                self.commandMgr = osgManipulator.CommandManager()
                self.commandMgr.connect(self.dragger, self.selection)
    
    
    def deselectAll(self):
        self.clearDragger()
        for highlightedObject in self.highlightedObjects:
            highlightedObject.setGlowColor(None)
        for animatedObject in self.animatedObjects:
            animatedObject.animateFlow(False)
        self.selectedObjects = []
        self.highlightedObjects = []
        self.animatedObjects = []
        wx.GetApp().inspector.inspectObjects(self, self.selectedObjects)    # TODO: factor this so wx.GetApp() doesn't have to be called, something like "self.app.inspector.inspectObject()"...
    
    
    def visibleWasDragged(self):
        visible = self.visibleForObject(self.selectedObjects[0])
        matrix = self.dragger.getMatrix()
        position = matrix.getTrans()
        size = matrix.getScale()
        visible.setPosition((position.x(), position.y(), position.z() - self.draggerZOffset))
        visible.setSize((size.x(), size.y(), size.z()))
    
    
    def onAutoLayout(self, event):
        self.autoLayout()
    
    
    def autoLayout(self, method="graphviz"):
        """Automatically layout the displayed network without moving objects with fixed positions (much)"""
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
            c = (A + A_prime) / 2
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
            xScale = 5000.0 / (xMax - xMin)
            xOff = (xMax + xMin) / 2.0
            yMin, yMax = y.min(), y.max()
            yScale = 5000.0 / (yMax - yMin)
            yOff = (yMax + yMin) / 2.0
            zMin, zMax = z.min(), z.max()
            zScale = 5000.0 / (zMax - zMin)
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
            graphAttr = {"graph": {"splines": "polyline", "overlap": "vpsc", "sep": "+20"}}
            nodeAttr = {"label": "", "shape": "box"}
            for node in graph.nodes():
                object = self.network.objectWithId(node)
                visible = self.visibleForObject(object)
                pos = visible.position()
                attr = {"width": str(visible.size()[0]/72.0), 
                        "height": str(visible.size()[1]/72.0), 
                        "fixedsize": "true", 
                        "pos": "%f,%f" % (pos[0]/72.0, pos[1]/72.0)}
                if visible.positionIsFixed():
                    attr["pin"] = "true"
                nodeAttr[node] = attr
            nodePos={} 
            if pygraphviz is not None:  # Use pygraphviz if it's available as it's faster than pydot.
                A=to_agraph(graph, graph_attr=graphAttr, node_attr=nodeAttr)
                A.layout(prog="fdp")
                for node in graph.nodes(): 
                    visible = self.visibleForObject(self.network.objectWithId(node))
                    pynode = pygraphviz.Node(A, node) 
                    try: 
                        x, y = pynode.attr["pos"].split(',') 
                        visible.setPosition((float(x), float(y), 0))
                    except: 
                        pass
                for edge in graph.edges():
                    try:
                        path_3D = []
                        visible0 = self.visibleForObject(self.network.objectWithId(edge[0]))
                        visible1 = self.visibleForObject(self.network.objectWithId(edge[1]))
                        if True:
                           pyedge = pygraphviz.Edge(A, edge[0], edge[1])
                           path = pyedge.attr["pos"].split(' ')
                           for pathElement in path:
                              x, y = pathElement.split(',')
                              path_3D.append((float(x), float(y), 0.0))
                        else:
                            path_3D.append(visible0.position())
                            path_3D.append(visible1.position())
                        self.setVisiblePath(edge[2], path_3D, visible0, visible1)
                    except:
                        pass
            else:  # Fall back to using pydot.
                pydotGraph = self.network.to_pydot(graph_attr=graphAttr, node_attr=nodeAttr)
                if pydotGraph is not None:
                    graphData = pydotGraph.create_dot(prog="fdp")
                    pydotGraph = pydot.graph_from_dot_data(graphData)
                    for node in graph.nodes(): 
                       visible = self.visibleForObject(self.network.objectWithId(node))
                       pyNode = pydotGraph.get_node(str(node))
                       pos = pyNode.get_pos()[1:-1] 
                       if pos != None:
                          x, y = pos.split(",")
                          visible.setPosition((float(x), float(y), 0))
                    # TODO: extract path segments
        self.Refresh(False)
