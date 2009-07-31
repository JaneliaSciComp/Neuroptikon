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
import Layout, Shape    # Not needed by the code but insures that the Layout and Shape modules gets packaged by setuptools.

from Shapes.Box import Box
from Shapes.Capsule import Capsule
from Shapes.Cone import Cone
from Shapes.Line import Line
from Shapes.Ball import Ball

from wx.py import dispatcher
from networkx import *
from math import pi, fabs
from datetime import datetime
import os, platform, cPickle
import xml.etree.ElementTree as ElementTree


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
        self._visibleIds = {}
        self.selectedVisibles = set()
        self.highlightedVisibles = []
        self.animatedVisibles = []
        self.selectConnectedVisibles = True
        self._showRegionNames = True
        self._showNeuronNames = False
        self._labelsFloatOnTop = False
        self._showFlow = False
        self._useGhosts = True
        self._primarySelectionColor = (0, 0, 1, .25)
        self._secondarySelectionColor = (0, 0, 1, .125)
        self.viewDimensions = 2
        
        self._recomputeBounds = True
        self.visiblesMin = [-100, -100, -100]
        self.visiblesMax = [100, 100, 100]
        self.visiblesCenter = [0, 0, 0]
        self.visiblesSize = [200, 200, 200]
        
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
        light = self.viewer3D.getLight()
        light.setAmbient(osg.Vec4f(0.4, 0.4, 0.4, 1))
        light.setDiffuse(osg.Vec4f(0.5, 0.5, 0.5, 1))
        self.viewer3D.setLight(light)
        self._first3DView = True
        
        config = wx.Config("Neuroptikon")
        clearColor = (config.ReadFloat("Color/Background/Red", 0.75), \
                      config.ReadFloat("Color/Background/Green", 0.75), \
                      config.ReadFloat("Color/Background/Blue", 0.75), \
                      config.ReadFloat("Color/Background/Alpha", 1.0))
        self.setBackgroundColor(clearColor)
        
        self.Bind(wx.EVT_SIZE, self.onSize)
        self.Bind(wx.EVT_PAINT, self.onPaint)
        self.Bind(wx.EVT_IDLE, self.onIdle)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.onEraseBackground)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.onMouseEvent)  # TODO: factor this out into individual events
        self.Bind(wx.EVT_MOUSEWHEEL, self.onMouseWheel)
        self.Bind(wx.EVT_SCROLLWIN, self.onScroll)
        
        self.dragSelection = None
        self.draggerLOD = None
        self.simpleDragger = None
        self.compositeDragger = None
        self.activeDragger = None
        
        self.selectionShouldExtend = False
        self.findShortestPath = False
        
        self._useMouseOverSelecting = False
        self.hoverSelect = True
        self.hoverSelecting = False
        self.hoverSelected = False  # set to True if the current selection was made by hovering
        
        width, height = self.GetClientSize()
        self.graphicsWindow = self.viewer2D.setUpViewerAsEmbeddedInWindow(0, 0, width, height)
        
        self.SetDropTarget(DisplayDropTarget(self))
    
        self._nextUniqueId = -1
        self._suppressRefresh = False
        
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
        self.defaultFlowSpread = 0.2    # The pulse should cover 20% of the path
        self.defaultFlowToSpreadUniform = osg.Uniform('flowToSpread', self.defaultFlowSpread)
        self.rootStateSet.addUniform(self.defaultFlowToSpreadUniform)
        self.defaultFlowFromSpreadUniform = osg.Uniform('flowFromSpread', self.defaultFlowSpread)
        self.rootStateSet.addUniform(self.defaultFlowFromSpreadUniform)
        
        dispatcher.connect(self.onSelectionOrShowFlowChanged, ('set', 'selection'), self)
        dispatcher.connect(self.onSelectionOrShowFlowChanged, ('set', 'showFlow'), self)
        
        self.lastUsedLayout = None
    
    
    def fromXMLElement(self, xmlElement):
        self._suppressRefresh = True
        
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
                self.setDefaultFlowColor((red, green, blue, alpha))
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
                visible = Visible.fromXMLElement(visibleElement, self)
                if visible is None:
                    raise ValueError, gettext('Could not create visualized item')
                self.addVisible(visible)
                
        # Add all of the paths (must be done after nodes are added)
        for visibleElement in visibleElements:
            if visibleElement.find('Path') is not None or visibleElement.find('path') is not None:
                visible = Visible.fromXMLElement(visibleElement, self)
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
        if xmlElement.get('useMouseOverSelecting') is not None:
            self._useMouseOverSelecting = xmlElement.get('useMouseOverSelecting') in trueValues
        if xmlElement.get('autoVisualize') is not None:
            self.autoVisualize = xmlElement.get('autoVisualize') in trueValues
        
        selectedVisibleIds = xmlElement.get('selectedVisibleIds')
        visiblesToSelect = []
        if selectedVisibleIds is not None:
            for visibleId in selectedVisibleIds.split(','):
                if visibleId.isdigit() and int(visibleId) in self._visibleIds:
                    visiblesToSelect.append(self._visibleIds[int(visibleId)])
        self.selectVisibles(visiblesToSelect)
        
        self._suppressRefresh = False
        
        self.centerView()
        self.Refresh()
    
    
    def toXMLElement(self, parentElement):
        displayElement = ElementTree.SubElement(parentElement, 'Display')
        
        # Add the background color
        colorElement = ElementTree.SubElement(displayElement, 'BackgroundColor')
        colorElement.set('r', str(self.backgroundColor[0]))
        colorElement.set('g', str(self.backgroundColor[1]))
        colorElement.set('b', str(self.backgroundColor[2]))
        colorElement.set('a', str(self.backgroundColor[3]))
        
        # Add the deault flow appearance
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
            ruleElement = displayRule.toXMLElement(displayElement)
            if ruleElement is None:
                raise ValueError, gettext('Could not save display rule')
        
        # Add the visibles
        for visibles in self.visibles.itervalues():
            for visible in visibles:
                if visible.parent is None:
                    visibleElement = visible.toXMLElement(displayElement)
                    if visibleElement is None:
                        raise ValueError, gettext('Could not save visualized item')
        
        displayElement.set('dimensions', str(self.viewDimensions))
        displayElement.set('showRegionNames', 'true' if self._showRegionNames else 'false')
        displayElement.set('showNeuronNames', 'true' if self._showNeuronNames else 'false')
        displayElement.set('showFlow', 'true' if self._showFlow else 'false')
        displayElement.set('useGhosting', 'true' if self._useGhosts else 'false')
        displayElement.set('useMouseOverSelecting', 'true' if self._useMouseOverSelecting else 'false')
        displayElement.set('autoVisualize', 'true' if self.autoVisualize else 'false')
        selectedVisibleIds = []
        for visible in self.selectedVisibles:
            selectedVisibleIds.append(str(visible.displayId))
        displayElement.set('selectedVisibleIds', ','.join(selectedVisibleIds))
        
        # TODO: it would be nice to save the console command history
        
        return displayElement
    
    
    def toScriptFile(self, scriptFile, scriptRefs, displayRef):
        scriptFile.write(displayRef + '.setBackgroundColor(' + str(self.backgroundColor) + ')\n')
        scriptFile.write(displayRef + '.setDefaultFlowColor(' + str(self.defaultFlowColor) + ')\n')
        scriptFile.write(displayRef + '.setDefaultFlowSpacing(' + str(self.defaultFlowSpacing) + ')\n')
        scriptFile.write(displayRef + '.setDefaultFlowSpeed(' + str(self.defaultFlowSpeed) + ')\n')
        scriptFile.write(displayRef + '.setDefaultFlowSpread(' + str(self.defaultFlowSpread) + ')\n')
        scriptFile.write(displayRef + '.setViewDimensions(' + str(self.viewDimensions) + ')\n')
        scriptFile.write(displayRef + '.setShowRegionNames(' + str(self._showRegionNames) + ')\n')
        scriptFile.write(displayRef + '.setShowNeuronNames(' + str(self._showNeuronNames) + ')\n')
        scriptFile.write(displayRef + '.setShowFlow(' + str(self._showFlow) + ')\n')
        scriptFile.write(displayRef + '.setUseGhosts(' + str(self._useGhosts) + ')\n')
        scriptFile.write(displayRef + '.setUseMouseOverSelecting(' + str(self._useMouseOverSelecting) + ')\n')
        scriptFile.write('\n')
        
        # First visualize all of the nodes
        for visibles in self.visibles.itervalues():
            for visible in visibles:
                if not visible.isPath() and visible.parent is None and not isinstance(visible.client, Stimulus):
                    visible.toScriptFile(scriptFile, scriptRefs, displayRef)
        # Next visualize all of the connections between the nodes
        for visibles in self.visibles.itervalues():
            for visible in visibles:
                if visible.isPath():
                    visible.toScriptFile(scriptFile, scriptRefs, displayRef)
        
        objectRefs = []
        for visible in self.selectedVisibles:
            objectRefs.append(scriptRefs[visible.client.networkId])
        if len(objectRefs) > 0:
            scriptFile.write(displayRef + '.selectObjects([' + ', '.join(objectRefs) + '])\n')
        
        scriptFile.write('\n' + displayRef + '.centerView()\n')
    
    
    def nextUniqueId(self):
        self._nextUniqueId += 1
        return self._nextUniqueId
    
    
    def setViewDimensions(self, dimensions):
        if dimensions != self.viewDimensions:
            self.viewDimensions = dimensions
            width, height = self.GetClientSize()
            
            self.clearDragger()
            
            if self.viewDimensions == 2:
                # TODO: approximate the 3D settings?
                width, height = self.GetClientSize()
                self.graphicsWindow = self.viewer2D.setUpViewerAsEmbeddedInWindow(0, 0, width, height)
                self.viewer2D.setCameraManipulator(None)
                self.resetView()
            elif self.viewDimensions == 3:
                # TODO: approximate the 2D settings
#                self.viewer3D.getCamera().setViewport(osg.Viewport(0, 0, width, height))
                self.SetScrollbar(wx.HORIZONTAL, 0, width, width, True)
                self.SetScrollbar(wx.VERTICAL, 0, height, height, True)
                width, height = self.GetClientSize()
                self.graphicsWindow = self.viewer3D.setUpViewerAsEmbeddedInWindow(0, 0, width, height)
                self.viewer3D.getCamera().setProjectionMatrixAsPerspective(30.0, float(width)/height, 1.0, 10000.0)
                if self._first3DView:
                    self.centerView()
                    self._first3DView = False
            
            if any(self.selectedVisibles):
                self.addDragger(list(self.selectedVisibles)[0])
            
            self.Refresh()
            dispatcher.send(('set', 'viewDimensions'), self)
    
    
    def onViewIn2D(self, event):
        self.setViewDimensions(2)
    
    
    def onViewIn3D(self, event):
        self.setViewDimensions(3)
    
    
    def setOrthoViewPlane(self, plane):
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
            else:
                raise ValueError, gettext("orthographic view plane must be one of 'xy', 'xz' or 'zy'")
            self.resetView()
            self.Refresh()
            dispatcher.send(('set', 'orthoViewPlane'), self)
    
    
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
            self.viewer2D.getCamera().setProjectionMatrixAsOrtho2D(self.orthoCenter[0] - (width + 20) * self.zoomScale / 2.0 / zoom, 
                                                                   self.orthoCenter[0] + (width + 20) * self.zoomScale / 2.0 / zoom, 
                                                                   self.orthoCenter[1] - (height + 20) * self.zoomScale / 2.0 / zoom, 
                                                                   self.orthoCenter[1] + (height + 20) * self.zoomScale / 2.0 / zoom)
            if self.orthoViewPlane == 'xy':
                self.viewer2D.getCamera().setViewMatrix(osg.Matrixd.translate(osg.Vec3d(0.0, 0.0, self.visiblesMin[2] - 2.0)))
            elif self.orthoViewPlane == 'xz':
                self.viewer2D.getCamera().setViewMatrix(osg.Matrixd.translate(osg.Vec3d(0.0, self.visiblesMax[1] + 2.0, 0.0)) * \
                                                        osg.Matrixd.rotate(osg.Quat(pi / -2.0, osg.Vec3d(1, 0, 0))))
            elif self.orthoViewPlane == 'zy':
                self.viewer2D.getCamera().setViewMatrix(osg.Matrixd.translate(osg.Vec3d(self.visiblesMax[0] + 2.0, 0.0, 0.0)) * \
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
            self._recomputeBounds = False
            
        width, height = self.GetClientSize()
        xZoom = self.visiblesSize[self.orthoXPlane] / (width - 10.0)
        yZoom = self.visiblesSize[self.orthoYPlane] / (height - 10.0)
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
            self.orthoCenter = (self.visiblesCenter[self.orthoXPlane], self.visiblesCenter[self.orthoYPlane])
            self.orthoZoom = 0
            self.resetView()
        elif self.viewDimensions == 3:
            self.trackball.setNode(node)
            self.trackball.computeHomePosition()
            self.viewer3D.home()
            self.trackball.setRotation(osg.Quat(0, 0, 0, 1))
        
        self.Refresh()
        
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
    
    
    def setUseMouseOverSelecting(self, flag):
        if flag != self._useMouseOverSelecting:
            self._useMouseOverSelecting = flag
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
        elif event.Moving() and self._useMouseOverSelecting and self.hoverSelect:
            self.hoverSelecting = True
            self.graphicsWindow.getEventQueue().mouseButtonPress(event.GetX(), event.GetY(), wx.MOUSE_BTN_LEFT)
            self.graphicsWindow.getEventQueue().mouseButtonRelease(event.GetX(), event.GetY(), wx.MOUSE_BTN_LEFT)
        self.Refresh()
        event.Skip()
    
    
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
        event.Skip()
    
    
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
    
    
    def onIdle(self, event):
        if len(self.animatedVisibles) > 0:
            self.Refresh()
            event.RequestMore()
        event.Skip()
    
    
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
    
    
    def Refresh(self, *args, **keywordArgs):
        if not self._suppressRefresh:
            wx.glcanvas.GLCanvas.Refresh(self, *args, **keywordArgs)
    
    
    def visibleChanged(self, sender, signal):
        if signal[1] in ('position', 'size', 'rotation', 'path'):
            self._recomputeBounds = True
        if signal[1] in ('positionIsFixed', 'sizeIsFixed') and any(self.selectedVisibles):
            self.clearDragger()
            visible = list(self.selectedVisibles)[0]
            if not visible.positionIsFixed() or not visible.sizeIsFixed():
                self.addDragger(visible)
        if not self._suppressRefresh:
            self.Refresh()
        if signal[1] not in ('glowColor'):
            self.GetTopLevelParent().setModified(True)
    
    
    def addVisible(self, visible, parentVisible = None):
        if visible.client is not None:
            if visible.client.networkId in self.visibles:
                self.visibles[visible.client.networkId].append(visible)
            else:
                self.visibles[visible.client.networkId] = [visible]
        self._visibleIds[visible.displayId] = visible
        if parentVisible is None:
            self.rootNode.addChild(visible.sgNode)
        else:
            parentVisible.addChildVisible(visible)
        dispatcher.connect(self.visibleChanged, dispatcher.Any, visible)
    
    
    def visibleWithId(self, visibleId):
        if visibleId in self._visibleIds:
            return self._visibleIds[visibleId]
        else:
            return None
    
    
    def defaultVisualizationParams(self, object):
        # TODO: replace this whole block with display rules
        neuralTissueColor = (0.85, 0.75, 0.6)
        params = {}
        
        params['opacity'] = 1.0
        params['weight'] = 1.0
        params['label'] = None
        params['texture'] = None
        
        shapes = wx.GetApp().scriptLocals()['shapes']
        
        if isinstance(object, Region):
            params['shape'] = shapes['Box']()
            params['size'] = (0.1, 0.1, 0.01)
            params['color'] = neuralTissueColor
        elif isinstance(object, Pathway):
            params['shape'] = shapes['Line']()
            params['weight'] = 5.0
            params['color'] = neuralTissueColor
            try:
                params['texture'] = wx.GetApp().library.texture('Stripes')
            except:
                pass
            params['textureScale'] = 10.0
        elif isinstance(object, Neuron):
            params['shape'] = shapes['Ball']()
            params['size'] = (.01, .01, .01)
            params['sizeIsAbsolute'] = True
            params['color'] = neuralTissueColor
        elif isinstance(object, Muscle):
            params['shape'] = shapes['Capsule']()
            params['size'] = (.1, .2, .02)
            params['color'] = (0.75, 0.5, 0.5)
            try:
                params['texture'] = wx.GetApp().library.texture('Stripes')
            except:
                pass
            params['textureScale'] = 20.0
            params['label'] = object.abbreviation or object.name
        elif isinstance(object, Arborization):
            params['shape'] = shapes['Line']()
            params['color'] = neuralTissueColor
        elif isinstance(object, Synapse):
            params['shape'] = shapes['Line']()
            params['color'] = neuralTissueColor
        elif isinstance(object, GapJunction):
            params['shape'] = shapes['Line']()
            params['color'] = (.65, 0.75, 0.4)
        elif isinstance(object, Innervation):
            params['shape'] = shapes['Line']()
            params['color'] = (0.55, 0.35, 0.25)
        elif isinstance(object, Stimulus):
            params['shape'] = shapes['Cone']()
            params['size'] = (.02, .02, .02) # so the label is in front (hacky...)
            params['color'] = (0.5, 0.5, 0.5)
            params['label'] = object.abbreviation or object.name
            params['weight'] = 5.0
        
        return params
    
    
    def visualizeObject(self, object, **keywordArgs):
        # TODO: replace this whole block with display rules
        
        visible = Visible(self, object)
        
        # Start with the default params for this object and override with any supplied params.
        params = self.defaultVisualizationParams(object)
        for key, value in keywordArgs.iteritems():
            params[key] = value
            
        parentObject = None
        childObjects = []
        pathStart = None
        pathEnd = None
        pathFlowsTo = None
        pathFlowsFrom = None
        
        if isinstance(object, Region):
            parentObject = object.parentRegion
            childObjects.extend(object.subRegions)
            childObjects.extend(object.neurons)
        elif isinstance(object, Pathway):
            pathStart = object.region1
            pathEnd = object.region2
            pathFlowsTo = object.region1Projects
            pathFlowsFrom = object.region2Projects
        elif isinstance(object, Neuron):
            parentObject = object.region
            #TODO: dispatcher.connect(self.neuronRegionChanged, ('set', 'region'), object)
        elif isinstance(object, Arborization):
            pathStart = object.neurite.neuron()
            pathEnd = object.region
            pathFlowsTo = object.sendsOutput
            pathFlowsFrom = object.receivesInput
            dispatcher.connect(self.arborizationChangedFlow, ('set', 'sendsOutput'), object)
            dispatcher.connect(self.arborizationChangedFlow, ('set', 'receivesInput'), object)
        elif isinstance(object, Synapse):
            pathStart = object.preSynapticNeurite.neuron()
            if len(object.postSynapticNeurites) > 0:
                pathEnd = object.postSynapticNeurites[0].neuron()
                pathFlowsTo = True
                pathFlowsFrom = False
        elif isinstance(object, GapJunction):
            neurites = list(object.neurites)
            pathStart = neurites[0].neuron()
            pathEnd = neurites[1].neuron()
            pathFlowsTo = True
            pathFlowsFrom = True
        elif isinstance(object, Innervation):
            pathStart = object.neurite.neuron()
            pathEnd = object.muscle
            pathFlowsTo = True
            pathFlowsFrom = False
        elif isinstance(object, Stimulus):
            edgeVisible = visible
            nodeVisible = Visible(self, object)
        
        if 'color' in params:
            visible.setColor(params['color'])
        if 'opacity' in params:
            visible.setOpacity(params['opacity'])
            if isinstance(object, Stimulus):
                nodeVisible.setOpacity(params['opacity'])
        if 'shape' in params:
            visible.setShape(params['shape'])
        if 'sizeIsAbsolute' in params:
            visible.setSizeIsAbsolute(params['sizeIsAbsolute'])
        if 'texture' in params:
            visible.setTexture(params['texture'])
        if 'textureScale' in params:
            visible.setTextureScale(params['textureScale'])
        if 'weight' in params:
            visible.setWeight(params['weight'])
        
        # Label and position are applied to the node visible of a stimulus.
        if isinstance(object, Stimulus):
            visible = nodeVisible
        
        if 'size' in params:
            visible.setSize(params['size'])
        if 'label' in params:
            visible.setLabel(params['label'])
        if 'position' in params:
            visible.setPosition(params['position'])
        if 'positionIsFixed' in params:
            visible.setPositionIsFixed(params['positionIsFixed'])
        
        if 'arrangedAxis' in params:
            visible.setArrangedAxis(params['arrangedAxis'])
        if 'arrangedSpacing' in params:
            visible.setArrangedSpacing(params['arrangedSpacing'])
        if 'arrangedWeight' in params:
            visible.setArrangedWeight(params['arrangedWeight'])
            
        parentVisibles = self.visiblesForObject(parentObject)
        self.addVisible(visible, parentVisibles[0] if len(parentVisibles) == 1 else None)
        
        if isinstance(object, Stimulus):
            targetVisibles = self.visiblesForObject(object.target)
            if len(targetVisibles) == 1:
                edgeVisible.setFlowDirection(nodeVisible, targetVisibles[0], True, False)
                edgeVisible.setPath([], nodeVisible, targetVisibles[0])
                if self._showFlow:
                    edgeVisible.animateFlow()
            nodeVisible.setShape(None)
            edgeVisible.setPositionIsFixed(True)
            self.addVisible(edgeVisible)
        else:
            if pathStart is not None and pathEnd is not None:
                pathStartVisibles = self.visiblesForObject(pathStart)
                pathEndVisibles = self.visiblesForObject(pathEnd)
                if len(pathStartVisibles) == 1 and len(pathEndVisibles) == 1:
                    visible.setFlowDirection(pathStartVisibles[0], pathEndVisibles[0], pathFlowsTo, pathFlowsFrom)
                    visible.setPath(params.get('path', []), pathStartVisibles[0], pathEndVisibles[0])
                    if self._showFlow:
                        visible.animateFlow()
            
            for childObject in childObjects:
                subVisibles = self.visiblesForObject(childObject)
                if len(subVisibles) == 1:
                    # TODO: what if the subVisible is already a child?
                    self.rootNode.removeChild(subVisibles[0].sgNode)
                    visible.addChildVisible(subVisibles[0])
        
        # The visible may be outside of the previously computed bounds.
        _recomputeBounds = True

        return visible
    
    
    def arborizationChangedFlow(self, signal, sender):
        arborizationVis = self.visiblesForObject(sender)
        neuronVis = self.visiblesForObject(sender.neurite.neuron())
        regionVis = self.visiblesForObject(sender.region)
        if len(arborizationVis) == 1 and len(neuronVis) == 1 and len(regionVis) == 1:
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
        signal = arguments['signal']
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
        self.GetTopLevelParent().setModified(True)
    
    
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
            self._showRegionNames = flag
            dispatcher.send(('set', 'showRegionNames'), self)
            self.Refresh()
    
    
    def showRegionNames(self):
        return self._showRegionNames
    
    
    def setShowNeuronNames(self, flag):
        if flag != self._showNeuronNames:
            self._showNeuronNames = flag
            dispatcher.send(('set', 'showNeuronNames'), self)
            self.Refresh()
    
    
    def showNeuronNames(self):
        return self._showNeuronNames
    
    
    def setLabelsFloatOnTop(self, flag):
        if flag != self._labelsFloatOnTop:
            self._labelsFloatOnTop = flag
            dispatcher.send(('set', 'labelsFloatOnTop'), self)
            self.Refresh()
    
    
    def labelsFloatOnTop(self):
        return self._labelsFloatOnTop
    
    
    def setShowFlow(self, flag):
        if flag != self._showFlow:
            self._showFlow = flag
            dispatcher.send(('set', 'showFlow'), self)
    
    
    def showFlow(self):
        return self._showFlow
    
    
    def setUseGhosts(self, flag):
        if flag != self._useGhosts:
            self._useGhosts = flag
            dispatcher.send(('set', 'useGhosts'), self)
            self.Refresh()
    
    
    def useGhosts(self):
        return self._useGhosts
    
    
    def setLabel(self, object, label):
        visibles = self.visiblesForObject(object)
        visible = None
        if len(visibles) == 1:
            visible = visibles[0]
        elif isinstance(object, Stimulus):
            visible = visibles[0 if visibles[1].isPath() else 1]
        if visible is not None:
            visible.setLabel(label)
    
    
    def setLabelColor(self, object, color):
        visibles = self.visiblesForObject(object)
        visible = None
        if len(visibles) == 1:
            visible = visibles[0]
        elif isinstance(object, Stimulus):
            visible = visibles[0 if visibles[1].isPath() else 1]
        if visible is not None:
            visible.setLabelColor(color)
    
    
    def setLabelPosition(self, object, position):
        visibles = self.visiblesForObject(object)
        visible = None
        if len(visibles) == 1:
            visible = visibles[0]
        elif isinstance(object, Stimulus):
            visible = visibles[0 if visibles[1].isPath() else 1]
        if visible is not None:
            visible.setLabelPosition(position)
    
    
    def setVisiblePosition(self, object, position = None, fixed = None):
        visibles = self.visiblesForObject(object)
        visible = None
        if len(visibles) == 1:
            visible = visibles[0]
        elif isinstance(object, Stimulus):
            visible = visibles[0 if visibles[1].isPath() else 1]
        if visible is not None:
            if position is not None:
                visible.setPosition(position)
            if fixed is not None:
                visible.setPositionIsFixed(fixed)
    
    
    def setVisibleRotation(self, object, rotation):
        visibles = self.visiblesForObject(object)
        if len(visibles) == 1:
            visibles[0].setRotation(rotation)
    
    
    def setVisibleSize(self, object, size, fixed=True, absolute=False):
        visibles = self.visiblesForObject(object)
        if len(visibles) == 1:
            visibles[0].setSize(size)
            visibles[0].setSizeIsFixed(fixed)
            visibles[0].setSizeIsAbsolute(absolute)
    
    
    def setVisibleColor(self, object, color):
        """setVisibleColor(object, color)
        
        color should be a tuple containing red, green and blue unit float values.
        
        (0.0, 0.0, 0.0) -> black
        (1.0, 0.0, 0.0) -> red
        (0.0, 1.0, 0.0) -> green
        (0.0, 0.0, 1.0) -> blue
        (1.0, 1.0, 1.0) -> white"""
        visibles = self.visiblesForObject(object)
        visible = None
        if len(visibles) == 1:
            visible = visibles[0]
        elif isinstance(object, Stimulus):
            visible = visibles[0 if visibles[0].isPath() else 1]
        if visible is not None:
            visible.setColor(color)
    
    
    def setVisibleTexture(self, object, texture, scale = 1.0):
        """setVisibleShape(object, texture)
        
        texture should an object returned by library.texture() or library.textures()."""
        visibles = self.visiblesForObject(object)
        visible = None
        if len(visibles) == 1:
            visible = visibles[0]
        elif isinstance(object, Stimulus):
            visible = visibles[0 if visibles[0].isPath() else 1]
        if visible is not None:
            visible.setTexture(texture)
            visible.setTextureScale(scale)
    
    
    def setVisibleShape(self, object, shape):
        """setVisibleShape(object, shapeName)
        
        shapeName should one of "ball", "box", "capsule", "cone" or "tube"."""
        
        if isinstance(shape, str):
            shapes = wx.GetApp().scriptLocals()['shapes']
            if shape == 'ball':
                shape = shapes['Ball']()
            elif shape == 'box':
                shape = shapes['Box']()
            elif shape == 'capsule':
                shape = shapes['Capsule']()
            elif shape == 'cone':
                shape = shapes['Cone']()
            elif shape == 'tube':
                shape = shapes['Line']()
        
        visibles = self.visiblesForObject(object)
        visible = None
        if len(visibles) == 1:
            visible = visibles[0]
        elif isinstance(object, Stimulus):
            visible = visibles[0 if visibles[0].isPath() else 1]
        if visible is not None:
            visible.setShape(shape)
    
    
    def setVisibleOpacity(self, object, opacity):
        """seVisibleOpacity(object, opacity)
        
        opacity should be a float value from 0.0 to 1.0."""
        visibles = self.visiblesForObject(object)
        visible = None
        if len(visibles) == 1:
            visible = visibles[0]
        elif isinstance(object, Stimulus):
            visible = visibles[0 if visibles[0].isPath() else 1]
        if visible is not None:
            visible.setOpacity(opacity)
    
    
    def setVisibleWeight(self, object, weight):
        """seVisibleWeight(object, weight)
        
        weight should be a float value with 1.0 being a neutral weight."""
        visibles = self.visiblesForObject(object)
        visible = None
        if len(visibles) == 1:
            visible = visibles[0]
        elif isinstance(object, Stimulus):
            visible = visibles[0 if visibles[0].isPath() else 1]
        if visible is not None:
            visible.setWeight(weight)
    
    
    def setVisibleFlowTo(self, object, show = True, color = None, spacing = None, speed = None, spread = None):
        """seVisibleFlowTo(object, weight, show, color, spacing, speed, spread)
        
        color should be a tuple containing red, green and blue unit float values.
        
        (0.0, 0.0, 0.0) -> black
        (1.0, 0.0, 0.0) -> red
        (0.0, 1.0, 0.0) -> green
        (0.0, 0.0, 1.0) -> blue
        (1.0, 1.0, 1.0) -> white
        
        spacing should be a float, 1.0 being the default
        speed should be a float, 1.0 being the default
        spread should be a float between 0.0 and 1.0"""
        visibles = self.visiblesForObject(object)
        visible = None
        if len(visibles) == 1:
            visible = visibles[0]
        elif isinstance(object, Stimulus):
            visible = visibles[0 if visibles[0].isPath() else 1]
        if visible is not None:
            visible.setFlowDirection(visible.pathStart, visible.pathEnd, flowTo = show, flowFrom = visible.flowFrom)
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
    
    
    def setVisibleFlowFrom(self, object, show = True, color = None, spacing = None, speed = None, spread = None):
        """seVisibleFlowFrom(object, weight, show, color, spacing, speed, spread)
        
        color should be a tuple containing red, green and blue unit float values.
        
        (0.0, 0.0, 0.0) -> black
        (1.0, 0.0, 0.0) -> red
        (0.0, 1.0, 0.0) -> green
        (0.0, 0.0, 1.0) -> blue
        (1.0, 1.0, 1.0) -> white
        
        spacing should be a float, 1.0 being the default
        speed should be a float, 1.0 being the default
        spread should be a float between 0.0 and 1.0"""
        visibles = self.visiblesForObject(object)
        visible = None
        if len(visibles) == 1:
            visible = visibles[0]
        elif isinstance(object, Stimulus):
            visible = visibles[0 if visibles[0].isPath() else 1]
        if visible is not None:
            visible.setFlowDirection(visible.pathStart, visible.pathEnd, flowTo = visible.flowTo, flowFrom = show)
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
    
    
    def setVisiblePath(self, object, path, startObject, endObject):
        visibles = self.visiblesForObject(object)
        visible = None
        if len(visibles) == 1:
            visible = visibles[0]
        elif isinstance(object, Stimulus):
            visible = visibles[0 if visibles[0].isPath() else 1]
        startVisible = self.visiblesForObject(startObject)[0]
        endVisible = self.visiblesForObject(endObject)[0]
        if visible is not None:
            visible.setPath(path, startVisible, endVisible)
    
    
    def selectObjectsMatching(self, predicate):
        matchingVisibles = []
        for object in self.network.objects:
            if predicate.matches(object):
                for visible in self.visiblesForObject(object):
                    matchingVisibles.append(visible)
        self.selectVisibles(matchingVisibles)
    
    
    def selectObjects(self, objects = [], extend = False, findShortestPath = False):
        visibles = []
        for object in objects:
            visibles.extend(self.visiblesForObject(object))
        self.selectVisibles(visibles, extend, findShortestPath)
    
    
    def selectObject(self, object, extend = False, findShortestPath = False):
        for visible in self.visiblesForObject(object):
            self.selectVisibles([visible], extend, findShortestPath)
    
    
    def objectIsSelected(self, object):
        for visible in self.visiblesForObject(object):
            if visible in self.selectedVisibles:
                return True
        return False
    
    
    def selectVisibles(self, visibles, extend = False, findShortestPath = False):
        if (extend or findShortestPath) and not self.hoverSelected:
            newSelection = set(self.selectedVisibles)
        else:
            newSelection = set()
        
        if findShortestPath:
            # Add the visibles that exist along the path to the selection.
            for visible in visibles:
                for startVisible in self.selectedVisibles:
                    prevObject = startVisible.client if startVisible.client.networkId in self.network.graph else None
                    for pathObject in startVisible.client.shortestPathTo(visible.client):
                        for pathVisible in self.visiblesForObject(pathObject):
                            newSelection.add(pathVisible)
                        if prevObject != None:
                            edgeObject = self.network.graph.get_edge(prevObject.networkId, pathObject.networkId)[0]
                            for pathVisible in self.visiblesForObject(edgeObject):
                                newSelection.add(pathVisible)
                        prevObject = pathObject
        elif extend and len(visibles) == 1 and visibles[0] in newSelection:
            # Remove the visible from the selection
            newSelection.remove(visibles[0])
        else:
            # Add the visibles to the new selection.
            for visible in visibles:
                newSelection.add(visible)
        
        self._selectedShortestPath = findShortestPath
        
        if newSelection != self.selectedVisibles or (self.hoverSelected and not self.hoverSelecting):
            self.clearDragger()
            
            self.selectedVisibles = newSelection
            
            if len(self.selectedVisibles) == 0:
                # There is no selection so hover selecting should be enabled.
                self.hoverSelecting = False
                self.hoverSelect = True
            elif not self.hoverSelecting:
                # An explicit selection has been made via the GUI or console.
                
                self.hoverSelect = False    # disable hover selecting
            
                if len(self.selectedVisibles) == 1:
                    # Add a dragger to the selected visible.
                    visible = list(self.selectedVisibles)[0]
                    if visible.isDraggable():
                        self.addDragger(visible)
            
            dispatcher.send(('set', 'selection'), self)
        
        self.hoverSelected = self.hoverSelecting
        self.hoverSelecting = False
        self.Refresh()
   
    
    def selection(self):
        return ObjectList(self.selectedVisibles)
    
    
    def selectedObjects(self):
        selection = set()
        for visible in self.selectedVisibles:
            if visible.client is not None:
                selection.add(visible.client)
        return list(selection)
    
    
    def selectAll(self, report = True):
        visiblesToSelect = []
        for visibles in self.visibles.itervalues():
            for visible in visibles:
                visiblesToSelect.append(visible)
        self.selectVisibles(visiblesToSelect)
        
    
    def deselectAll(self, report = True):
        self.selectVisibles([])
    
    
    def onSelectionOrShowFlowChanged(self, signal, sender):
        # Update the highlighting, animation and ghosting based on the current selection.
        # TODO: this should all be handled by display rules which will also keep ghosting from blowing away opacity settings
        
        self._suppressRefresh = True
        
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
                if self.selectConnectedVisibles and not self._selectedShortestPath:
                    singleSelection = (len(self.selectedVisibles) == 1)
                    
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
        
        if len(self.selectedVisibles) == 0 and self._showFlow:
            for visibles in self.visibles.itervalues():
                for visible in visibles:
                    if visible.isPath() and (visible.flowTo or visible.flowFrom):
                        visiblesToAnimate.add(visible)
        
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
            elif not self._useGhosts:
                visibleToHighlight.setGlowColor(self._secondarySelectionColor)
            else:
                visibleToHighlight.setGlowColor(None)
        for visibleToAnimate in visiblesToAnimate:
            visibleToAnimate.animateFlow()
        
        self.highlightedVisibles = visiblesToHighlight
        self.animatedVisibles = visiblesToAnimate
        
        if self._useGhosts:
            # Dim everything that isn't selected, highlighted or animated.
            selectionIsEmpty = len(self.selectedVisibles) == 0
            for visibles in self.visibles.itervalues():
                for visible in visibles:
                    visible.updateOpacity()
        
        self._suppressRefresh = False
    
    
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
    
    
    def visibleWasDragged(self):
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
            visible.updateTransform()
    
    
    def clearDragger(self):
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
    
    
    def onLayout(self, event):
        layoutClasses = sys.modules['Display'].layoutClasses()
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
            from Layouts.ForceDirectedLayout import ForceDirectedLayout
            self.performLayout(ForceDirectedLayout())
        elif (method == 'spectral' or method is None) and self.viewDimensions == 3:
            from Layouts.SpectralLayout import SpectralLayout
            self.performLayout(SpectralLayout())
    
    
    def performLayout(self, layout = None):
        if layout is None:
            # Fall back to the last layout used.
            layout = self.lastUsedLayout
        else:
            # If a layout class was passed in then create a default instance.
            if isinstance(layout, type(self.__class__)):
                layout = layout()
            
            if not layout.__class__.canLayoutDisplay(self):
                raise ValueError, gettext('The supplied layout cannot be used.')
        
        if layout is None or not layout.__class__.canLayoutDisplay(self):
            # Pick the first layout class capable of laying out the display.
            for layoutClass in sys.modules['Display'].layoutClasses().itervalues():
                if layoutClass.canLayoutDisplay(self):
                    layout = layoutClass()
                    break
        
        self._suppressRefresh = True
        layout.layoutDisplay(self)
        self.lastUsedLayout = layout
        self._suppressRefresh = False
        self.centerView()
        self.Refresh()
    
    
    def saveViewAsImage(self, path):
        width, height = self.GetClientSize()
        image = osg.Image()
        self.SetCurrent()
        image.readPixels(0, 0, width, height, osg.GL_RGB, osg.GL_UNSIGNED_BYTE)
        osgDB.writeImageFile(image, path)
    
    
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
            self.saveViewAsImage(savePath)
    
    
    def setDefaultFlowColor(self, color):
        if len(color) == 3:
            color = (color[0], color[1], color[2], 1.0)
        
        if color != self.defaultFlowColor:
            self.defaultFlowColor = color
            self.defaultFlowToColorUniform.set(osg.Vec4f(*color))
            self.defaultFlowFromColorUniform.set(osg.Vec4f(*color))
            dispatcher.send(('set', 'defaultFlowColor'), self)
    
    
    def setDefaultFlowSpacing(self, spacing):
        if spacing != self.defaultFlowSpacing:
            self.defaultFlowSpacing = float(spacing)
            self.defaultFlowToSpacingUniform.set(self.defaultFlowSpacing)
            self.defaultFlowFromSpacingUniform.set(self.defaultFlowSpacing)
            dispatcher.send(('set', 'defaultFlowSpacing'), self)
    
    
    def setDefaultFlowSpeed(self, speed):
        if speed != self.defaultFlowSpeed:
            self.defaultFlowSpeed = float(speed)
            self.defaultFlowToSpeedUniform.set(self.defaultFlowSpeed)
            self.defaultFlowFromSpeedUniform.set(self.defaultFlowSpeed)
            dispatcher.send(('set', 'defaultFlowSpeed'), self)
    
    
    def setDefaultFlowSpread(self, spread):
        if spread != self.defaultFlowSpread:
            self.defaultFlowSpread = float(spread)
            self.defaultFlowToSpreadUniform.set(self.defaultFlowSpread)
            self.defaultFlowFromSpreadUniform.set(self.defaultFlowSpread)
            dispatcher.send(('set', 'defaultFlowSpread'), self)
    

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
    
