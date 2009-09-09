from __future__ import with_statement # This isn't required in Python 2.6

import osg, osgDB, osgFX, osgText

from Shape import Shape, UnitShape, PathShape

from Network.Region import Region
from Network.Neuron import Neuron
from Network.Arborization import Arborization
from Network.Stimulus import Stimulus

from Library.Texture import Texture

from Network.Attribute import Attribute

import wx
from wx.py import dispatcher
import weakref

# The standard wx.py.dispatcher is dog slow for a large connection pool.  The bottleneck shown by profiling is the attempt to avoid duplicate connections.  Since we never attempt duplicate connections this expensive check is not necessary.
# Here we replace the normal connect method with a version that doesn't check for duplicate connections.
def dispatcher_connect(receiver, signal=dispatcher.Any, sender=dispatcher.Any, weak=True):
    if signal is None:
        raise dispatcher.DispatcherError, 'signal cannot be None'
    if weak:
        receiver = dispatcher.safeRef(receiver)
    senderkey = id(sender)
    signals = {}
    if dispatcher.connections.has_key(senderkey):
        signals = dispatcher.connections[senderkey]
    else:
        dispatcher.connections[senderkey] = signals
        # Keep track of senders for cleanup.
        if sender not in (None, dispatcher.Any):
            def remove(object, senderkey=senderkey):
                dispatcher._removeSender(senderkey=senderkey)
            # Skip objects that can not be weakly referenced, which means
            # they won't be automatically cleaned up, but that's too bad.
            try:
                weakSender = weakref.ref(sender, remove)
                dispatcher.senders[senderkey] = weakSender
            except:
                pass
    receivers = []
    if signals.has_key(signal):
        receivers = signals[signal]
    else:
        signals[signal] = receivers
# This is the disabled block.
#    try:
#        receivers.remove(receiver)
#    except ValueError:
#        pass
    receivers.append(receiver)
dispatcher.connect = dispatcher_connect

import sys, os.path
runningFromSource = not hasattr(sys, "frozen")

from math import atan2, pi, sqrt
import random
import xml.etree.ElementTree as ElementTree

class Visible(object):
    """
    Instances of this class map a network object (neurion, region, etc.) to a specific display.  They capture all of the attributes needed to render the object.
    
    You should never create an instance of this class directly.  Instead use the value returned by calling :meth:`visualizeObject() <Display.Display.Display.visualizeObject>` on a display.
    """
    
    try:
        if osgText.readFontFile("Arial Bold.ttf"):
            labelFont = 'Arial Bold.ttf'
        elif osgText.readFontFile("ArialBD.ttf"):
            labelFont = 'ArialBD.ttf'
    except:
        (exceptionType, exceptionValue, exceptionTraceback) = sys.exc_info()
        print 'Could not load Arial font (' + exceptionValue.message + ')'
        labelFont = None
    
    if wx.GetApp():
        shaderDir = wx.GetApp().rootDir
        if runningFromSource:
            shaderDir = os.path.join(shaderDir, 'Display')
        with open(os.path.join(shaderDir, 'FlowShader.vert')) as f:
            flowVertexShader = f.read()
        with open(os.path.join(shaderDir, 'FlowShader.frag')) as f:
            flowFragmentShader = f.read()
        flowProgram = osg.Program()
        flowProgram.addShader(osg.Shader(osg.Shader.VERTEX, flowVertexShader))
        flowProgram.addShader(osg.Shader(osg.Shader.FRAGMENT, flowFragmentShader))
        del shaderDir
    
    osgDB.Registry.instance().getReaderWriterForExtension('osg')    # Make sure the osg plug-in can be found before the cwd gets changed for a script run.
    
    
    def __init__(self, display, client):
        self.display = display
        self.displayId = display._generateUniqueId() # a unique identifier within the display
        self.client = client
        self._glowColor = None
        self._glowNode = None
        
        # Geometry attributes
        self._position = (random.random() - 0.5, random.random() - 0.5, 0)
        self._positionIsFixed = False
        self._size = (.001, .001, .001)
        self._sizeIsFixed = True
        self._sizeIsAbsolute = False
        self._rotation = (0, 0, 1, 0)
        
        # Appearance attributes
        self._weight = 1.0
        self._label = None
        self._labelNode = None
        self._labelPosition = (0.0, 0.0, 0.0)   # in local coordinates
        self._labelColor = (0.0, 0.0, 0.0)
        self._shape = None
        self._color = (0.5, 0.5, 0.5)
        self._opacity = 1.0
        
        self._dependencies = set()
        self.dependentVisibles = []
        
        # Path attributes
        self._pathMidPoints = []
        self._pathStart = None
        self._pathEnd = None
        self.connectedPaths = []
        
        # Flow attributes
        self._animateFlow = False
        self._flowTo = False
        self._flowToColor = None
        self._flowToSpacing = None
        self._flowToSpeed = None
        self._flowToSpread = None
        self._flowFrom = False
        self._flowFromColor = None
        self._flowFromSpacing = None
        self._flowFromSpeed = None
        self._flowFromSpread = None
        
        self.sgNode = osg.MatrixTransform()
        self._shapeGeode = osg.Geode()
        self._shapeGeode.setName(str(self.displayId))
        self._shapeGeode2 = None
        self._stateSet = self._shapeGeode.getOrCreateStateSet()
        self._stateSet.setAttributeAndModes(osg.BlendFunc(), osg.StateAttribute.ON)
        self._material = osg.Material()
        self._material.setDiffuse(osg.Material.FRONT_AND_BACK, osg.Vec4(0.5, 0.5, 0.5, 1))
        self._material.setAmbient(osg.Material.FRONT_AND_BACK, osg.Vec4(0.5, 0.5, 0.5, 1))
        self._material.setSpecular(osg.Material.FRONT_AND_BACK, osg.Vec4(0.0, 0.0, 0.0, 0.0))
        self._material.setShininess(osg.Material.FRONT_AND_BACK, 0.0)
        self._stateSet.setAttribute(self._material)
        self.sgNode.addChild(self._shapeGeode)
        self._textGeode = osg.Geode()
        self._textGeode.setName(str(self.displayId))
        self._textGeode.getOrCreateStateSet().setMode(osg.GL_BLEND, osg.StateAttribute.ON)
        self._textGeode.getOrCreateStateSet().setRenderBinDetails(51, 'RenderBin')
        self._textGeode.setDataVariance(osg.Object.DYNAMIC)
        self._textDrawable = None
        self.sgNode.addChild(self._textGeode)
        self._staticTexture = None
        self._staticTextureScale = 1.0
        
        # Parent and children
        self.parent = None
        self.children = []
        self.childGroup = osg.MatrixTransform(osg.Matrixd.identity())
        self.sgNode.addChild(self.childGroup)
        
        # Arrangement attributes
        self.arrangedAxis = 'largest'
        self.arrangedSpacing = 0.02
        self.arrangedWeight = 1.0
        
        self._updateLabel()
        if isinstance(self.client, Region):
            dispatcher.connect(self._displayChangedShowName, ('set', 'showRegionNames'), self.display)
        if isinstance(self.client, Neuron):
            dispatcher.connect(self._displayChangedShowName, ('set', 'showNeuronNames'), self.display)
        dispatcher.connect(self._displayChangedShowName, ('set', 'viewDimensions'), self.display)
        dispatcher.connect(self._displayChangedShowName, ('set', 'orthoViewPlane'), self.display)
        dispatcher.connect(self._displayChangedShowName, ('set', 'labelsFloatOnTop'), self.display)
        
        self._updateOpacity()
        dispatcher.connect(self._displayChangedGhosting, ('set', 'useGhosts'), self.display)
        
        if not hasattr(Visible, 'cullFrontFacesAttr'):
            # This is a bit of a hack.  osgswig does not expose the osg::CullFace class which is needed to get proper transparency.
            # To get around this we load an osg file which contains nodes with both front and back cull face state attributes and extract them. 
            if runningFromSource:
                cullFacesPath = os.path.join(wx.GetApp().rootDir, 'Display', 'CullFaces.osg')
            else:
                cullFacesPath = os.path.join(wx.GetApp().rootDir, 'CullFaces.osg')
            cullFacesNode = osgDB.readNodeFile(cullFacesPath)
            cullFacesGroup = cullFacesNode.asGroup()
            Visible.cullFrontFacesAttr = cullFacesGroup.getChild(0).getStateSet().getAttribute(osg.StateAttribute.CULLFACE)
            Visible.cullBackFacesAttr = cullFacesGroup.getChild(1).getStateSet().getAttribute(osg.StateAttribute.CULLFACE)
            # Make sure the node with our attributes doesn't get garbage collected.
            cullFacesNode.ref()
    
    
    def __repr__(self):
        if self.client is None:
            return gettext('anonymous proxy')
        else:
            return gettext('proxy of %s') % (self.client.name or gettext('<unnamed %s>') % (self.client.__class__.displayName()))
    
    
    @classmethod
    def _fromXMLElement(cls, xmlElement, display):
        client = display.network.objectWithId(xmlElement.get('objectId'))
        visible = Visible(display, client)
        visible.displayId = int(xmlElement.get('id'))
        visible._shapeGeode.setName(str(visible.displayId))
        visible._textGeode.setName(str(visible.displayId))
        
        # Set any geometry
        geometryElement = xmlElement.find('Geometry')
        if geometryElement is None:
            geometryElement = xmlElement.find('geometry')
        if geometryElement is not None:
            positionElement = geometryElement.find('Position')
            if positionElement is None:
                positionElement = geometryElement.find('position')
            if positionElement is not None:
                x = float(positionElement.get('x'))
                y = float(positionElement.get('y'))
                z = float(positionElement.get('z'))
                visible.setPosition((x, y, z))
                if positionElement.get('fixed') == 'true':
                    visible.setPositionIsFixed(True)
            sizeElement = geometryElement.find('Size')
            if sizeElement is None:
                sizeElement = geometryElement.find('size')
            if sizeElement is not None:
                width = float(sizeElement.get('x'))
                height = float(sizeElement.get('y'))
                depth = float(sizeElement.get('z'))
                visible.setSize((width, height, depth))
                if sizeElement.get('fixed') == 'false':
                    visible.setSizeIsFixed(False)
                if sizeElement.get('absolute') == 'true':
                    visible.setSizeIsAbsolute(True)
            rotationElement = geometryElement.find('Rotation')
            if rotationElement is None:
                rotationElement = geometryElement.find('rotation')
            if rotationElement is not None:
                x = float(rotationElement.get('x'))
                y = float(rotationElement.get('y'))
                z = float(rotationElement.get('z'))
                angle = float(rotationElement.get('angle'))
                visible.setRotation((x, y, z, angle))
        
        # Set any appearance
        appearanceElement = xmlElement.find('Appearance')
        if appearanceElement is None:
            appearanceElement = xmlElement.find('appearance')
        if appearanceElement is not None:
            labelElement = appearanceElement.find('Label')
            if labelElement is None:
                labelElement = appearanceElement.find('label')
            if labelElement != None:
                textElement = labelElement.find('Text')
                colorElement = labelElement.find('Color')
                positionElement = labelElement.find('Position')
                if textElement != None or colorElement != None or positionElement != None:
                    if textElement != None:
                        visible.setLabel(textElement.text or '')
                    if colorElement != None:
                        visible.setLabelColor((float(colorElement.get('r')), float(colorElement.get('g')), float(colorElement.get('b')), float(colorElement.get('a') or '1.0')))
                    if positionElement != None:
                        visible.setLabelPosition((float(positionElement.get('x')), float(positionElement.get('y')), float(positionElement.get('z'))))
                else:
                    visible.setLabel(labelElement.text or '') # previous XML format
            
            shapeElement = appearanceElement.find('Shape')
            shapeClassName = None if shapeElement == None else shapeElement.get('class')
            shapeAttrs = {}
            if shapeClassName == None:
                shapeName = appearanceElement.findtext('Shape') or appearanceElement.findtext('shape')
                if shapeName == 'ball':
                    shapeClassName = 'Ball'
                elif shapeName == 'capsule':
                    shapeClassName = 'Capsule'
                elif shapeName == 'cone':
                    shapeClassName = 'Cone'
                elif shapeName in ['Line', 'tube']:
                    shapeClassName = 'Line'
                elif shapeName != None:
                    shapeClassName = 'Box' # the default
            else:
                # Get any attributes
                for element in shapeElement.findall('Attribute'):
                    attribute = Attribute._fromXMLElement(object, element)
                    if attribute is not None:
                        shapeAttrs[attribute.name()] = attribute.value()
            if shapeClassName == None:
                visible.setShape(None)
            else:
                shapes = wx.GetApp().scriptLocals()['shapes']
                shape = shapes[shapeClassName](**shapeAttrs)
                visible.setShape(shape)
            
            colorElement = appearanceElement.find('Color')
            if colorElement is None:
                colorElement = appearanceElement.find('color')
            if colorElement is not None:
                red = float(colorElement.get('r'))
                green = float(colorElement.get('g'))
                blue = float(colorElement.get('b'))
                visible.setColor((red, green, blue))
            opacityText = appearanceElement.findtext('Opacity') or appearanceElement.findtext('opacity')
            if opacityText is not None:
                visible.setOpacity(float(opacityText))
            weightText = appearanceElement.findtext('Weight') or appearanceElement.findtext('weight')
            if weightText is not None:
                visible.setWeight(float(weightText))
            textureElement = appearanceElement.find('Texture')
            if textureElement is None:
                textureElement = appearanceElement.find('texture')
            if textureElement is not None:
                textureId = textureElement.get('identifier')
                textureScale = textureElement.get('scale')
                if textureId is None:
                    textureId = textureElement.text
                    textureScale = "10.0"
                if textureId is not None:
                    visible.setTexture(wx.GetApp().library.texture(textureId))
                if textureScale is not None:
                    visible.setTextureScale(float(textureScale))
        
        # Set up any arrangement
        arrangementElement = xmlElement.find('Arrangement')
        if arrangementElement is None:
            arrangementElement = xmlElement.find('arrangement')
        if arrangementElement is not None:
            axis = arrangementElement.get('axis')
            visible.setArrangedAxis(None if axis == 'None' else axis)
            spacing = arrangementElement.get('spacing')
            if spacing is not None:
                visible.setArrangedSpacing(float(spacing))
            weight = arrangementElement.get('weight')
            if weight is not None:
                visible.setArrangedWeight(float(weight))
        
        # Set up any path
        pathElement = xmlElement.find('Path')
        if pathElement is None:
            pathElement = xmlElement.find('path')
        if pathElement is not None:
            pathStart = display.visibleWithId(int(pathElement.get('startVisibleId')))
            pathEnd = display.visibleWithId(int(pathElement.get('endVisibleId')))
            if pathStart is None or pathEnd is None:
                raise ValueError, gettext('Could not create path')
            visible.setPathEndPoints(pathStart, pathEnd)
            flowTo = pathElement.get('flowTo')
            if flowTo == 'true':
                visible.setFlowTo(True)
            elif flowTo == 'false':
                visible.setFlowTo(False)
            flowFrom = pathElement.get('flowFrom')
            if flowFrom == 'true':
                visible.setFlowFrom(True)
            elif flowFrom == 'false':
                visible.setFlowFrom(False)
            midPoints = []
            for midPointElement in pathElement.findall('MidPoint'):
                x = float(midPointElement.get('x'))
                y = float(midPointElement.get('y'))
                z = float(midPointElement.get('z'))
                midPoints.append((x, y, z))
            visible.setPathMidPoints(midPoints)
            flowToElement = pathElement.find('FlowToAppearance')
            if flowToElement is None:
                flowToElement = pathElement.find('flowToAppearance')
            if flowToElement is not None:
                colorElement = flowToElement.find('Color')
                if colorElement is None:
                    colorElement = flowToElement.find('color')
                if colorElement is not None:
                    red = float(colorElement.get('r'))
                    green = float(colorElement.get('g'))
                    blue = float(colorElement.get('b'))
                    alpha = float(colorElement.get('a'))
                    visible.setFlowToColor((red, green, blue, alpha))
                if flowToElement.get('spacing') is not None:
                    visible.setFlowToSpacing(float(flowToElement.get('spacing')))
                if flowToElement.get('speed') is not None:
                    visible.setFlowToSpeed(float(flowToElement.get('speed')))
                if flowToElement.get('spread') is not None:
                    visible.setFlowToSpread(float(flowToElement.get('spread')))
            flowFromElement = pathElement.find('FlowFromAppearance')
            if flowFromElement is None:
                flowFromElement = pathElement.find('flowFromAppearance')
            if flowFromElement is not None:
                colorElement = flowFromElement.find('Color')
                if colorElement is None:
                    colorElement = flowFromElement.find('color')
                if colorElement is not None:
                    red = float(colorElement.get('r'))
                    green = float(colorElement.get('g'))
                    blue = float(colorElement.get('b'))
                    alpha = float(colorElement.get('a'))
                    visible.setFlowFromColor((red, green, blue, alpha))
                if flowFromElement.get('spacing') is not None:
                    visible.setFlowFromSpacing(float(flowFromElement.get('spacing')))
                if flowFromElement.get('speed') is not None:
                    visible.setFlowFromSpeed(float(flowFromElement.get('speed')))
                if flowFromElement.get('spread') is not None:
                    visible.setFlowFromSpread(float(flowFromElement.get('spread')))
        
        # Create any child visibles
        for visibleElement in xmlElement.findall('Visible'):
            childVisible = Visible._fromXMLElement(visibleElement, display)
            if childVisible is None:
                raise ValueError, gettext('Could not create visualized item')
            display.addVisible(childVisible, visible)
        
        return visible
    
    
    def _toXMLElement(self, parentElement):
        visibleElement = ElementTree.SubElement(parentElement, 'Visible')
        visibleElement.set('id', str(self.displayId))
        if self.client is not None:
            visibleElement.set('objectId', str(self.client.networkId))
        
        # Add a comment to the XML to make it easier to figure out the client of the visible.
        if self.client:
            visibleElement.append(ElementTree.Comment(self.client.__class__.displayName() + ': ' + (self.client.name or self.client.abbreviation or gettext('(unnamed)'))))
        
        # Add the geometry
        geometryElement = ElementTree.SubElement(visibleElement, 'Geometry')
        if self.parent == None or self.parent.arrangedAxis == None:
            positionElement = ElementTree.SubElement(geometryElement, 'Position')
            positionElement.set('x', str(self._position[0]))
            positionElement.set('y', str(self._position[1]))
            positionElement.set('z', str(self._position[2]))
            positionElement.set('fixed', 'true' if self._positionIsFixed else 'false')
        if self.parent == None or self.parent.arrangedAxis == None or self._sizeIsAbsolute:
            sizeElement = ElementTree.SubElement(geometryElement, 'Size')
            if self.parent == None or self.parent.arrangedAxis == None:
                sizeElement.set('x', str(self._size[0]))
                sizeElement.set('y', str(self._size[1]))
                sizeElement.set('z', str(self._size[2]))
                sizeElement.set('fixed', 'true' if self.sizeIsFixed else 'false')
            sizeElement.set('absolute', 'true' if self._sizeIsAbsolute else 'false')
        if self.parent == None or self.parent.arrangedAxis == None:
            rotationElement = ElementTree.SubElement(geometryElement, 'Rotation')
            rotationElement.set('x', str(self._rotation[0]))
            rotationElement.set('y', str(self._rotation[1]))
            rotationElement.set('z', str(self._rotation[2]))
            rotationElement.set('angle', str(self._rotation[3]))
        
        # Add the appearance
        appearanceElement = ElementTree.SubElement(visibleElement, 'Appearance')
        if self._label is not None or self._labelColor != (0.0, 0.0, 0.0) or self._labelPosition != (0.0, 0.0, 0.0):
            labelElement = ElementTree.SubElement(appearanceElement, 'Label')
            if self._label is not None:
                textElement = ElementTree.SubElement(labelElement, 'Text')
                textElement.text = self._label
            if self._labelColor != (0.0, 0.0, 0.0):
                colorElement = ElementTree.SubElement(labelElement, 'Color')
                colorElement.set('r', str(self._labelColor[0]))
                colorElement.set('g', str(self._labelColor[1]))
                colorElement.set('b', str(self._labelColor[2]))
                if len(self._labelColor) > 3:
                    colorElement.set('a', str(self._labelColor[3]))
            if self._labelPosition != (0.0, 0.0, 0.0):
                positionElement = ElementTree.SubElement(labelElement, 'Position')
                positionElement.set('x', str(self._labelPosition[0]))
                positionElement.set('y', str(self._labelPosition[1]))
                positionElement.set('z', str(self._labelPosition[2]))
        if self._shape is not None:
            shapeElement = ElementTree.SubElement(appearanceElement, 'Shape')
            shapeElement.set('class', self._shape.__class__.__name__)
            # Save any custom attributes of the shape.
            for attributeName, attributeValue in self._shape.persistentAttributes().iteritems():
                attribute = None
                if isinstance(attributeValue, str):
                    attribute = Attribute(self._shape, attributeName, Attribute.STRING_TYPE, attributeValue)
                elif isinstance(attributeValue, int):
                    attribute = Attribute(self._shape, attributeName, Attribute.INTEGER_TYPE, attributeValue)
                elif isinstance(attributeValue, float):
                    attribute = Attribute(self._shape, attributeName, Attribute.DECIMAL_TYPE, attributeValue)
                elif isinstance(attributeValue, bool):
                    attribute = Attribute(self._shape, attributeName, Attribute.BOOLEAN_TYPE, attributeValue)
                if attribute != None:
                    attribute._toXMLElement(shapeElement)
                
        colorElement = ElementTree.SubElement(appearanceElement, 'Color')
        colorElement.set('r', str(self._color[0]))
        colorElement.set('g', str(self._color[1]))
        colorElement.set('b', str(self._color[2]))
        ElementTree.SubElement(appearanceElement, 'Opacity').text = str(self._opacity)
        ElementTree.SubElement(appearanceElement, 'Weight').text = str(self._weight)
        if self._staticTexture is not None:
            textureElement = ElementTree.SubElement(appearanceElement, 'Texture')
            textureElement.set('identifier', self._staticTexture.identifier)
            textureElement.set('scale', str(self._staticTextureScale))
        
        # Add the arrangement
        arrangementElement = ElementTree.SubElement(visibleElement, 'Arrangement')
        arrangementElement.set('axis', str(self.arrangedAxis))
        arrangementElement.set('spacing', str(self.arrangedSpacing))
        arrangementElement.set('weight', str(self.arrangedWeight))
        
        # Add any path
        if self.isPath():
            pathElement = ElementTree.SubElement(visibleElement, 'Path')
            pathElement.set('startVisibleId', str(self._pathStart.displayId))
            pathElement.set('endVisibleId', str(self._pathEnd.displayId))
            pathElement.set('flowTo', 'true' if self._flowTo else 'false')
            pathElement.set('flowFrom', 'true' if self._flowFrom else 'false')
            if self._flowToColor is not None or self._flowToSpread is not None:
                flowToElement = ElementTree.SubElement(pathElement, 'FlowToAppearance')
                if self._flowToColor is not None:
                    colorElement = ElementTree.SubElement(flowToElement, 'Color')
                    colorElement.set('r', str(self._flowToColor[0]))
                    colorElement.set('g', str(self._flowToColor[1]))
                    colorElement.set('b', str(self._flowToColor[2]))
                    colorElement.set('a', str(self._flowToColor[3]))
                if self._flowToSpacing is not None:
                    flowToElement.set('spacing', str(self._flowToSpacing))
                if self._flowToSpeed is not None:
                    flowToElement.set('speed', str(self._flowToSpeed))
                if self._flowToSpread is not None:
                    flowToElement.set('spread', str(self._flowToSpread))
            if self._flowFromColor is not None or self._flowFromSpread is not None:
                flowFromElement = ElementTree.SubElement(pathElement, 'FlowFromAppearance')
                if self._flowFromColor is not None:
                    colorElement = ElementTree.SubElement(flowFromElement, 'Color')
                    colorElement.set('r', str(self._flowFromColor[0]))
                    colorElement.set('g', str(self._flowFromColor[1]))
                    colorElement.set('b', str(self._flowFromColor[2]))
                    colorElement.set('a', str(self._flowFromColor[3]))
                if self._flowFromSpacing is not None:
                    flowFromElement.set('spacing', str(self._flowFromSpacing))
                if self._flowFromSpeed is not None:
                    flowFromElement.set('speed', str(self._flowFromSpeed))
                if self._flowFromSpread is not None:
                    flowFromElement.set('spread', str(self._flowFromSpread))
            for midPoint in self._pathMidPoints:
                midPointElement = ElementTree.SubElement(pathElement, 'MidPoint')
                midPointElement.set('x', str(midPoint[0]))
                midPointElement.set('y', str(midPoint[1]))
                midPointElement.set('z', '0.0' if len(midPoint) == 2 else str(midPoint[2]))
        
        # Add any child visibles
        for childVisible in self.children:
            childElement = childVisible._toXMLElement(visibleElement)
            if childElement is None:
                raise ValueError, gettext('Could not save visualized item')
        
        return visibleElement
    
    
    def _toScriptFile(self, scriptFile, scriptRefs, displayRef):
        # The stimulus visibles make this complicated because there are two visibles per stimulus object (a node and an path) and some attributes come from one visible and some from the other.
        # This is worked around by tweaking the value of self as the attributes are queried.  The attributes are grouped as follows to simplify the switching:
        # Attribute     Stimulus      Non-Stimulus
        # =========     ========      ============
        # size                        node
        # rotation                    node
        # arr. axis                   node
        # arr. spacing                node
        # arr. weight                 node
        # 
        # label         node          node
        # position      node          node
        # 
        # weight        path          path
        # flow color    path          path
        # flow spread   path          path
        # 
        # shape         path          node or path
        # color         path          node or path
        # opacity       path          node or path
        # texture       path          node or path
        
        defaultParams = self.display.defaultVisualizationParams(self.client)
        params = {}
        
        if isinstance(self.client, Stimulus):
            visibles = list(self.display.visiblesForObject(self.client))
            nodeVisible = visibles[0 if visibles[1].isPath() else 1]
            pathVisible = visibles[0 if visibles[0].isPath() else 1]
        else:
            # Size, rotation and arrangement are never applied to stimuli.
            
            if not self.isPath():
                if self.parent == None or self.parent.arrangedAxis == None:
                    params['size'] = self.size()
                    if not self.sizeIsFixed():
                        params['sizeIsFixed'] = False
                    if self.rotation() != (0, 0, 1, 0):
                        params['rotation'] = self.rotation()
                if self.parent is not None and self.sizeIsAbsolute():
                    params['sizeIsAbsolute'] = self.sizeIsAbsolute()
            
            if len(self.children) > 0:
                if self.arrangedAxis is not None:
                    params['arrangedAxis'] = self.arrangedAxis
                if self.arrangedSpacing is not None:
                    params['arrangedSpacing'] = self.arrangedSpacing
            if self.parent is not None and self.arrangedWeight != 1.0:
                params['arrangedWeight'] = self.arrangedWeight
        
        # Stimuli label and position are always taken from the node visible.
        if isinstance(self.client, Stimulus):
            self = nodeVisible
        
        if self._label is None:
            params['label'] = None
        else:
            params['label'] = self._label
        if self._labelColor != (0.0, 0.0, 0.0):
            params['labelColor'] = self._labelColor
        if self._labelPosition != (0.0, 0.0, 0.0):
            params['labelPosition'] = self._labelPosition
        if not self.isPath() and (self.parent == None or self.parent.arrangedAxis == None):
            params['position'] = self.position()
            if self.positionIsFixed():
                params['positionIsFixed'] = True
        
        # All other stimuli attributes are taken from the path visible.
        if isinstance(self.client, Stimulus):
            self = pathVisible
        
        if self.isPath():
            params['weight'] = self.weight()
            if self._flowTo:
                if self.flowToColor() != None:
                    params['flowToColor'] = self.flowToColor()
                if self.flowToSpacing() != None:
                    params['flowToSpacing'] = self.flowToSpacing()
                if self.flowToSpeed() != None:
                    params['flowToSpeed'] = self.flowToSpeed()
                if self.flowToSpread() != None:
                    params['flowToSpread'] = self.flowToSpread()
            if self._flowFrom:
                if self.flowFromColor() != None:
                    params['flowFromColor'] = self.flowFromColor()
                if self.flowFromSpacing() != None:
                    params['flowFromSpacing'] = self.flowFromSpacing()
                if self.flowFromSpeed() != None:
                    params['flowFromSpeed'] = self.flowFromSpeed()
                if self.flowFromSpread() != None:
                    params['flowFromSpread'] = self.flowFromSpread()
            if not isinstance(self.client, Stimulus):
                params['pathEndPoints'] = (self._pathStart.client, self._pathEnd.client)
                if self._pathMidPoints != []:
                    params['pathMidPoints'] = self._pathMidPoints
            
        
        params['shape'] = self.shape()
        params['color'] = self.color()
        params['opacity'] = self.opacity()
        params['texture'] = self._staticTexture

        # Strip out values that are the same as the default.
        for key in params.keys():
            if key in defaultParams and params[key] == defaultParams[key]:
                del params[key]
        
        scriptRef = scriptRefs[self.client.networkId]
        if self.display.autoVisualize:
            # Change the existing visualization of the object.
            if '(' in scriptRef and len(params) > 1:
                scriptFile.write('object = ' + scriptRef + '\n')
                scriptRef = 'object'
            if 'position' in params:
                scriptFile.write('%s.setVisiblePosition(%s, (%s)' % (displayRef, scriptRef, ', '.join([str(dim) for dim in params['position']])))
                if 'positionIsFixed' in params:
                    scriptFile.write(', fixed = ' + str(params['positionIsFixed']))
                scriptFile.write(')\n')
            if 'size' in params or 'sizeIsFixed' in params or 'sizeIsAbsolute' in params:
                scriptFile.write('%s.setVisibleSize(%s' % (displayRef, scriptRef))
                if 'size' in params:
                    scriptFile.write(', (' + ', '.join([str(dim) for dim in params['size']]) + ')')
                if 'sizeIsFixed' in params:
                    scriptFile.write(', fixed = ' + str(self.sizeIsFixed()))
                if 'sizeIsAbsolute' in params:
                    scriptFile.write(', absolute = ' + str(self.sizeIsAbsolute()))
                scriptFile.write(')\n')
            if 'rotation' in params:
                scriptFile.write('%s.setVisibleRotation(%s, (%s))\n' % (displayRef, scriptRef, ', '.join([str(dim) for dim in params['rotation']])))
            if 'label' in params:
                scriptFile.write('%s.setLabel(%s, \'%s\')\n' % (displayRef, scriptRef, params['label'].replace('\\', '\\\\').replace('\'', '\\\'')))
            if 'labelColor' in params:
                scriptFile.write('%s.setLabelColor(%s, (%s))\n' % (displayRef, scriptRef, ', '.join([str(component) for component in params['labelColor']])))
            if 'labelPosition' in params:
                scriptFile.write('%s.setLabelPosition(%s, (%s))\n' % (displayRef, scriptRef, ', '.join([str(dim) for dim in params['labelPosition']])))
            if 'shape' in params:
                if params['shape'] == None:
                    scriptFile.write('%s.setVisibleShape(%s, None)\n' % (displayRef, scriptRef))
                else:
                    scriptFile.write('%s.setVisibleShape(%s, shapes[\'%s\'](' % (displayRef, scriptRef, self.shape().__class__.__name__))
                    for attributeName, attributeValue in self._shape.persistentAttributes().iteritems():
                        scriptFile.write(attributeName + ' = ' + repr(attributeValue) + ', ')
                    scriptFile.write('))\n')
            if 'color' in params:
                scriptFile.write('%s.setVisibleColor(%s, (%s))\n' % (displayRef, scriptRef, ', '.join([str(component) for component in params['color']])))
            if 'opacity' in params:
                scriptFile.write('%s.setVisibleOpacity(%s, %s)\n' % (displayRef, scriptRef, str(self.opacity())))
            if 'weight' in params:
                scriptFile.write('%s.setVisibleWeight(%s, %s)\n' % (displayRef, scriptRef, str(self.weight())))
            if 'texture' in params:
                if self._staticTexture == None:
                    scriptFile.write('%s.setVisibleTexture(%s, None)\n' % (displayRef, scriptRef))
                else:
                    scriptFile.write('%s.setVisibleTexture(%s, library.texture(\'%s\'), scale = %s)\n' % (displayRef, scriptRef, self._staticTexture.identifier.replace('\\', '\\\\').replace('\'', '\\\''), str(self._staticTextureScale)))
            if 'arrangedAxis' in params:
                scriptFile.write('%s.setArrangedAxis(%s, \'%s\')\n' % (displayRef, scriptRef, self.arrangedAxis))
            if 'arrangedSpacing' in params:
                scriptFile.write('%s.setArrangedSpacing(%s, %s)\n' % (displayRef, scriptRef, str(self.arrangedSpacing)))
            if 'arrangedWeight' in params:
                scriptFile.write('%s.setArrangedWeight(%s, %s)\n' % (displayRef, scriptRef, str(self.arrangedWeight)))
            if 'pathEndPoints' in params:
                startObject, endObject = params['pathEndPoints']
                scriptFile.write('%s.setVisiblePath(%s, %s, %s' % (displayRef, scriptRef, scriptRefs[startObject.networkId], scriptRefs[endObject.networkId]))
                if 'pathMidPoints' in params:
                    scriptFile.write(', ' + str(params['pathMidPoints']))
                scriptFile.write(')\n')
            if 'flowToColor' in params or 'flowToSpacing' in params or 'flowToSpeed' in params or 'flowToSpread' in params:
                scriptFile.write('%s.setVisibleFlowTo(%s, True' % (displayRef, scriptRef))
                if 'flowToColor' in params:
                    scriptFile.write(', flowToColor = (' + ', '.join([str(component) for component in params['flowToColor']]) + ')')
                if 'flowToSpacing' in params:
                    scriptFile.write(', flowToSpacing = ' + str(self.flowToSpacing))
                if 'flowToSpeed' in params:
                    scriptFile.write(', flowToSpeed = ' + str(self.flowToSpeed))
                if 'flowToSpread' in params:
                    scriptFile.write(', flowToSpread = ' + str(self.flowToSpread))
                scriptFile.write(')\n')
            if 'flowFromColor' in params or 'flowFromSpacing' in params or 'flowFromSpeed' in params or 'flowFromSpread' in params:
                scriptFile.write('%s.setVisibleFlowFrom(%s, True' % (displayRef, scriptRef))
                if 'flowFromColor' in params:
                    scriptFile.write(', flowFromColor = (' + ', '.join([str(component) for component in params['flowFromColor']]) + ')')
                if 'flowFromSpacing' in params:
                    scriptFile.write(', flowFromSpacing = ' + str(self.flowFromSpacing))
                if 'flowFromSpeed' in params:
                    scriptFile.write(', flowFromSpeed = ' + str(self.flowFromSpeed))
                if 'flowFromSpread' in params:
                    scriptFile.write(', flowFromSpread = ' + str(self.flowFromSpread))
                scriptFile.write(')\n')
        else:
            # Manually visualize the object.
            scriptFile.write('%s.visualizeObject(%s' % (displayRef, scriptRef))
            for key, value in params.iteritems():
                if isinstance(value, str):
                    valueText = '\'' + value.replace('\\', '\\\\').replace('\'', '\\\'') + '\''
                elif isinstance(value, Texture):
                    valueText = 'library.texture(\'%s\')' % (value.identifier.replace('\\', '\\\\').replace('\'', '\\\''))
                else:
                    valueText = str(value)
                scriptFile.write(', %s = %s' % (key, valueText))
            scriptFile.write(')\n')
        
        for childVisible in self.children:
            childVisible._toScriptFile(scriptFile, scriptRefs, displayRef)
    
    
    def shape(self):
        """
        Return the shape of this visualized :class:`object <Network.Object.Object>`, a Shape sub-class instance or None.
        """
        return self._shape
        
    
    def setShape(self, shape):
        """
        Set the :class:`shape <Display.Shape.Shape>` of this visualized :class:`object <Network.Object.Object>`.
        
        >>> visible.setShape(shapes['Ball']())
        >>> visible.setShape(shapes['Ring'](startAngle = 0.0, endAngle = pi))
        
        The shape must be an instance of one of the classes in shapes or None.
        """
        
        if not isinstance(shape, (Shape, type(None))):
            raise TypeError, 'The argument passed to setShape() must be a Shape instance or None'
        
        if self._shape != shape:
            glowColor = self._glowColor
            if self._glowNode is not None:
                self.setGlowColor(None)
            if self._shape:
                self._shapeGeode.removeDrawable(self._shape.geometry())
            self._shape = shape
            if self._shape:
                self._shapeGeode.addDrawable(self._shape.geometry())
                if self._shape.interiorBounds() != None:
                    minBound, maxBound = self._shape.interiorBounds()
                    minBound = osg.Vec3(*minBound)
                    maxBound = osg.Vec3(*maxBound)
                    self.childGroup.setMatrix(osg.Matrixd.scale(maxBound - minBound) * osg.Matrixd.translate((minBound + maxBound) / 2.0))
            for child in self.children:
                dispatcher.send(('set', 'position'), child)
            # Recreate the glow shape if needed
            self.setGlowColor(glowColor)
            dispatcher.send(('set', 'shape'), self)
            if self.isPath():
                self._updatePath()
            else:
                self._updateTransform()
    
    
    def _displayChangedShowName(self, signal, sender):
        self._updateLabel()
    
    
    def _updateLabel(self, opacity = 1.0):
        label = self._label
        if label is None and ((isinstance(self.client, Region) and self.display.showRegionNames()) or (isinstance(self.client, Neuron) and self.display.showNeuronNames())):
            label = self.client.abbreviation or self.client.name
        
        if label is None:
            if self._textDrawable is not None:
                self._textGeode.removeDrawable(self._textDrawable)
                self._textDrawable = None
        else:
            if self._textDrawable is None:
                # Create the text drawable
                self._textDrawable = osgText.Text()
                self._textDrawable.setDataVariance(osg.Object.DYNAMIC)
                self._textDrawable.setCharacterSizeMode(osgText.Text.SCREEN_COORDS)
                if Visible.labelFont is None:
                    self._textDrawable.setCharacterSize(48.0)
                else:
                    self._textDrawable.setFont(Visible.labelFont)
                    self._textDrawable.setCharacterSize(18.0)
                self._textDrawable.setAxisAlignment(osgText.Text.SCREEN)
                self._textDrawable.setAlignment(osgText.Text.CENTER_CENTER)
                self._textDrawable.setBackdropType(osgText.Text.OUTLINE)
                self._textGeode.addDrawable(self._textDrawable)
            
            self._textDrawable.setColor(osg.Vec4(self._labelColor[0], self._labelColor[1], self._labelColor[2], self._opacity * opacity))
            backdropColor = 1.0 if self._labelColor[0] + self._labelColor[1] + self._labelColor[2] <= .75 * 3.0 else 0.0
            self._textDrawable.setBackdropColor(osg.Vec4(backdropColor, backdropColor, backdropColor, self._opacity * opacity * 0.25))
            
            if self.display.viewDimensions == 3 or self.display.labelsFloatOnTop():
                self._textDrawable.setPosition(osg.Vec3(*self._labelPosition))
                self._textGeode.getOrCreateStateSet().setAttribute(osg.Depth(osg.Depth.ALWAYS))
            else:
                if self.display.orthoViewPlane == 'xy':
                    self._textDrawable.setPosition(osg.Vec3(self._labelPosition[0], self._labelPosition[1], self._labelPosition[2] + 1.0))
                elif self.display.orthoViewPlane == 'xz':
                    self._textDrawable.setPosition(osg.Vec3(self._labelPosition[0], self._labelPosition[1] - 1.0, self._labelPosition[2]))
                else:
                    self._textDrawable.setPosition(osg.Vec3(self._labelPosition[0] - 1.0, self._labelPosition[1], self._labelPosition[2]))
                self._textGeode.getOrCreateStateSet().removeAttribute(osg.StateAttribute.DEPTH)
            self._textDrawable.setText(str(label))
    
    
    def setLabel(self, label):
        """
        Set the label that adorns this visualized :class:`object <Network.Object.Object>`.
        
        If the label is set to None then neurons and regions will be automatically labeled with their abbreviation or name (unless those options have been disabled).  To really have no label pass in '', an empty string.
        """
        if label != self._label:
            self._label = label
            self._updateLabel()
            dispatcher.send(('set', 'label'), self)
    
    
    def label(self):
        """
        Return the label that has been set to adorn this visualized :class:`object <Network.Object.Object>`.
        
        If the object is a region or neuron automatically displaying its abbreviation or name then this method will return None, not what is being displayed.
        """
        return self._label
    
    
    def setLabelColor(self, color):
        """
        Set the color of the label that adorns this visualized :class:`object <Network.Object.Object>`.
         
        The color argument should be a tuple or list of three values between 0.0 and 1.0 indicating the red, green and blue values of the color.  For example:
        
        * (0.0, 0.0, 0.0) -> black
        * (1.0, 0.0, 0.0) -> red
        * (0.0, 1.0, 0.0) -> green
        * (0.0, 0.0, 1.0) -> blue
        * (1.0, 1.0, 1.0) -> white
        
        Any alpha value should be set independently using :meth:`setOpacity <Display.Visible.Visible.setOpacity>`.
        """
        
        if color != self._labelColor:
            self._labelColor = color
            self._updateLabel()
            dispatcher.send(('set', 'labelColor'), self)
    
    
    def labelColor(self):
        """
        Return the color of the the label that adorns this visualized :class:`object <Network.Object.Object>`.
        """
        
        return self._labelColor
    
    
    def setLabelPosition(self, position):
        """
        Set the position of the label that adorns this visualized :class:`object <Network.Object.Object>`.
        
        The position argument should be a tuple or list indicating the position of the label.  The coordinates are local to the object with is usually a unit square centered at (0.0, 0.0).  For example:
        (0.0, 0.0) -> label at center of object
        (-0.5, -0.5) -> label at lower left corner of object
        (0.0, 0.5) -> label centered at top of object
        """
        
        if position != self._labelPosition:
            self._labelPosition = position
            self._updateLabel()
            dispatcher.send(('set', 'labelPosition'), self)
    
    
    def labelPosition(self):
        """
        Return the position of the label that adorns this visualized :class:`object <Network.Object.Object>`.
        """
        
        return self._labelPosition
    
    
    def setColor(self, color):
        """
        Set the color of this visualized :class:`object <Network.Object.Object>`.
         
        The color argument should be a tuple or list of three values between 0.0 and 1.0 indicating the red, green and blue values of the color.  For example:
        
        * (0.0, 0.0, 0.0) -> black
        * (1.0, 0.0, 0.0) -> red
        * (0.0, 1.0, 0.0) -> green
        * (0.0, 0.0, 1.0) -> blue
        * (1.0, 1.0, 1.0) -> white
        
        Any alpha value should be set independently using :meth:`setOpacity <Display.Visible.Visible.setOpacity>`.
        """
        
        if (not isinstance(color, (tuple, list)) or len(color) != 3 or 
            not isinstance(color[0], (int, float)) or color[0] < 0.0 or color[0] > 1.0 or 
            not isinstance(color[1], (int, float)) or color[1] < 0.0 or color[1] > 1.0 or 
            not isinstance(color[2], (int, float)) or color[2] < 0.0 or color[2] > 1.0):
            raise ValueError, 'The color argument should be a tuple or list of three integer or floating point values between 0.0 and 1.0, inclusively.'
        
        if color != self._color:
            colorVec = osg.Vec4(color[0], color[1], color[2], 1)
            self._material.setDiffuse(osg.Material.FRONT_AND_BACK, colorVec)
            self._material.setAmbient(osg.Material.FRONT_AND_BACK, colorVec)
            if self._shape != None:
                self._shape.setColor(color)
            self._color = color
            self._updateOpacity()
            dispatcher.send(('set', 'color'), self)
    
    
    def color(self):
        """
        Return the color of this visualized :class:`object <Network.Object.Object>`.
        """
        
        return self._color
    
    
    def _displayChangedGhosting(self, sender, signal):
        self._updateOpacity()
    
    
    def _updateOpacity(self):
        if self.display.useGhosts() and any(self.display.selection()) and self not in self.display.highlightedVisibles and self not in self.display.animatedVisibles:
            opacity = 0.1
            for ancestor in self.ancestors():
                if ancestor in self.display.selectedVisibles:
                    opacity = 0.5
                    break
            if opacity == 0.1:
                for child in self.allChildren():
                    if child in self.display.selectedVisibles:
                        opacity = 0.5
                        break
        elif any(self.children) and self._shape != None:
            opacity = 0.5
        else:
            opacity = self._opacity
        
        if self._shape is not None:
            self._material.setAlpha(osg.Material.FRONT_AND_BACK, opacity)
            stateSet1 = self._shapeGeode.getOrCreateStateSet()
            if opacity == 1.0:
                if self._shapeGeode2:
                    self.sgNode.removeChild(self._shapeGeode2)
                    self._shapeGeode2 = None
                stateSet1.setRenderingHint(osg.StateSet.OPAQUE_BIN)
                stateSet1.setMode(osg.GL_BLEND, osg.StateAttribute.OFF)
                stateSet1.removeAttribute(osg.StateAttribute.CULLFACE)
            else:
                if not self._shapeGeode2:
                    # Technique that may correctly render nested, transparent geometries, from http://www.mail-archive.com/osg-users@lists.openscenegraph.org/msg06863.html
                    self._shapeGeode2 = osg.Geode()
                    self._shapeGeode2.addDrawable(self._shape.geometry())
                    stateSet2 = self._shapeGeode2.getOrCreateStateSet()
                    stateSet2.setAttributeAndModes(Visible.cullFrontFacesAttr, osg.StateAttribute.ON)
                    stateSet1.setAttributeAndModes(Visible.cullBackFacesAttr, osg.StateAttribute.ON)
                else:
                    stateSet2 = self._shapeGeode2.getOrCreateStateSet()
                stateSet1.setMode(osg.GL_BLEND, osg.StateAttribute.ON)
                stateSet2.setMode(osg.GL_BLEND, osg.StateAttribute.ON)
                # Place more deeply nested regions in lower render bins so they are rendered before the containing visible.
                # Each nesting depth needs four render bins: two for the front and back face of the shape and one for the glow shape.
                # This assumes a maximum nesting depth of 10.
                sceneDepth = len(self.ancestors())
                stateSet1.setRenderBinDetails(40 - sceneDepth * 3 - 1, 'DepthSortedBin')
                stateSet2.setRenderBinDetails(40 - sceneDepth * 3 - 2, 'DepthSortedBin')
        
        if self._textDrawable is not None:
            self._updateLabel(opacity)
    
    
    def setOpacity(self, opacity):
        """
        Set the opacity of the visualized :class:`object's <Network.Object.Object>` shape and label.
        
        The opacity parameter should be a number from 0.0 (fully transparent) to 1.0 (fully opaque).
        """
        
        if opacity < 0.0:
            opacity = 0.0
        elif opacity > 1.0:
            opacity = 1.0
        
        if opacity != self.opacity:
            self._opacity = opacity
            self._updateOpacity()
            dispatcher.send(('set', 'opacity'), self)
    
    
    def opacity(self):
        """
        Return the opacity of the visualized :class:`object <Network.Object.Object>`.
        """
        
        return self._opacity
    
    
    def _updateTransform(self):
        if isinstance(self._shape, (UnitShape, type(None))):
            # update the transform unless we're under an osgGA.Selection node, i.e. being dragged
            if len(self.sgNode.getParents()) == 0 or self.display.dragSelection is None or self.sgNode.getParent(0).__repr__() != self.display.dragSelection.asGroup().__repr__():
                if self.parent is None or not self.sizeIsAbsolute():
                    scale = self._size
                else:
                    parentScale = self.parent.worldSize()
                    scale = (self._size[0] / parentScale[0], self._size[1] / parentScale[1], self._size[2] / parentScale[2])
                self.sgNode.setMatrix(osg.Matrixd.scale(osg.Vec3d(scale[0], scale[1], scale[2])) * 
                                       osg.Matrixd.rotate(self.rotation()[3], osg.Vec3d(self.rotation()[0], self.rotation()[1], self.rotation()[2])) *
                                       osg.Matrixd.translate(osg.Vec3d(self.position()[0], self.position()[1], self.position()[2])))
        else:
            self.sgNode.setMatrix(osg.Matrixd.identity())
    
    
    def position(self):
        """
        Return the position of this visualized :class:`object <Network.Object.Object>`.
        """
        
        return self._position
    
    
    def setPosition(self, position):
        """
        Set the position of this visualized :class:`object <Network.Object.Object>`.
        
        For objects without containers this value is in world-space coordinates.  For objects within containers the coordinate space is a unit cube centered at (0.0, 0.0, 0.0).  Values should be between -0.5 and 0.5 to be located within the container but values beyond that are allowed.
        """
        
        if position != self._position:
            self._position = position
            self._updateTransform()
            dispatcher.send(('set', 'position'), self)
    
    
    def offsetPosition(self, offset):
        """
        Offset the position of this visualized :class:`object <Network.Object.Object>` by the indicated amounts.
        
        The offset argument should be a tuple of three numbers indicating how much the position should be offset in each dimension.
        """
        
        if offset != (0, 0, 0):
            self._position = (self._position[0] + offset[0], self._position[1] + offset[1], self._position[2] + offset[2])
            self._updateTransform()
            dispatcher.send(('set', 'position'), self)
    
    
    def worldPosition(self):
        """
        Return the position of the visualized :class:`object <Network.Object.Object>` in world-space coordinates.
        """
        
        # TODO: if a parent is rotated does this screw up?
        # TODO: will OSG do this for us?
        # TODO: merge this with position() and add a coordinate-space argument? 
        
        if self.parent is None:
            worldPosition = self._position
        else:
            parentSize = self.parent.worldSize()
            parentPosition = self.parent.worldPosition()
            trans = osg.Vec3d()
            rot = osg.Quat()
            scale = osg.Vec3d()
            so = osg.Quat()
            self.parent.childGroup.getMatrix().decompose(trans, rot, scale, so)
            parentPosition = (parentPosition[0] + trans.x() * parentSize[0], parentPosition[1] + trans.y() * parentSize[1], parentPosition[2] + trans.z() * parentSize[2])
            parentSize = (parentSize[0] * scale.x(), parentSize[1] * scale.y(), parentSize[2] * scale.z())
            worldPosition = (parentPosition[0] + self._position[0] * parentSize[0], parentPosition[1] + self._position[1] * parentSize[1], parentPosition[2] + self._position[2] * parentSize[2])
        
        return worldPosition
    
    
    def positionIsFixed(self):
        """
        Return whether the position of this visualized :class:`object <Network.Object.Object>` should be allowed to change.
        """
        return self._positionIsFixed
    
    
    def setPositionIsFixed(self, isFixed):
        """
        Set whether the position of this visualized :class:`object <Network.Object.Object>` should be allowed to change.
        
        Calling :meth:`setPosition <Display.Visible.Visible.setPosition>` ignores this setting.
        """
        
        if self._positionIsFixed != isFixed:
            self._positionIsFixed = isFixed
            dispatcher.send(('set', 'positionIsFixed'), self)
    
    
    def size(self):
        """
        Return the size of this visualized :class:`object <Network.Object.Object>`.
        """
        
        # TODO: if isinstance(self._shape, UnitShape)...
        return self._size
    
    
    def setSize(self, size):
        """
        Set the size of this visualized :class:`object <Network.Object.Object>`.
        
        For objects without containers or those that are :meth:`absolutely sized <Display.Visible.Visible.setSizeIsAbsolute>` this value is in world-space coordinates.  For relatively sized objects within containers the coordinate space is a unit cube centered at (0.0, 0.0, 0.0).
        """
        
        if self._size != size:
            self._size = size
            # TODO: if not isinstance(self._shape, UnitShape): # then rebuild geometry with new size
            self._updateTransform()
            dispatcher.send(('set', 'size'), self)
            self._arrangeChildren()
    
    
    def sizeIsFixed(self):
        """
        Return whether the size of this visualized :class:`object <Network.Object.Object>` should be allowed to change.
        """
        return self._sizeIsFixed
    
    
    def setSizeIsFixed(self, isFixed):
        """
        Set whether the size of this visualized :class:`object <Network.Object.Object>` should be allowed to change.
        
        Calling :meth:`setSize <Display.Visible.Visible.setSize>` ignores this setting.
        """
        
        if self._sizeIsFixed != isFixed:
            self._sizeIsFixed = isFixed
            dispatcher.send(('set', 'sizeIsFixed'), self)
    
    
    def sizeIsAbsolute(self):
        """
        Return whether the size set for this visualized :class:`object <Network.Object.Object>` should be in world-space coordinates or relative to the enclosing container.
        """
        
        return self._sizeIsAbsolute
    
    
    def setSizeIsAbsolute(self, sizeIsAbsolute = True):
        """
        Set whether the size set for this visualized :class:`object <Network.Object.Object>` should be in world-space coordinates or relative to the enclosing container.
        """
        
        if self._sizeIsAbsolute != sizeIsAbsolute:
            self._sizeIsAbsolute = sizeIsAbsolute
            
            # TODO: convert absolute to relative size or vice versa
            
            self._updateTransform()
            dispatcher.send(('set', 'sizeIsAbsolute'), self)
            self._arrangeChildren()
            
            for ancestor in self.ancestors():
                if self._sizeIsAbsolute:
                    dispatcher.connect(self._maintainAbsoluteSize, ('set', 'position'), ancestor)
                    dispatcher.connect(self._maintainAbsoluteSize, ('set', 'size'), ancestor)
                    dispatcher.connect(self._maintainAbsoluteSize, ('set', 'rotation'), ancestor)
                else:
                    dispatcher.disconnect(self._maintainAbsoluteSize, ('set', 'position'), ancestor)
                    dispatcher.disconnect(self._maintainAbsoluteSize, ('set', 'size'), ancestor)
                    dispatcher.disconnect(self._maintainAbsoluteSize, ('set', 'rotation'), ancestor)
    
    
    def _maintainAbsoluteSize( self, signal, sender, event=None, value=None, **arguments):
        self._updateTransform()
        self._arrangeChildren()
    
    
    def worldSize(self):
        """
        Return the size of the visualized :class:`object <Network.Object.Object>` in world-space coordinates.
        """
        
        # TODO: if a parent is rotated does this screw up?
        # TODO: will OSG do this for us?
        # TODO: merge this with size() and add a coordinate-space argument? 
        
        if self.parent is None or self.sizeIsAbsolute():
            worldSize = self._size
        else:
            parentSize = self.parent.worldSize()
            trans = osg.Vec3d()
            rot = osg.Quat()
            scale = osg.Vec3d()
            so = osg.Quat()
            self.parent.childGroup.getMatrix().decompose(trans, rot, scale, so)
            worldSize = (self._size[0] * parentSize[0] * scale.x(), self._size[1] * parentSize[1] * scale.y(), self._size[2] * parentSize[2] * scale.z())
        
        return worldSize
    
    
    def rotation(self):
        return self._rotation
    
    
    def setRotation(self, rotation):
        if self._rotation != rotation:
            self._rotation = rotation
            self._updateTransform()
            dispatcher.send(('set', 'rotation'), self)
    
    
    def weight(self):
        """
        Return the weight of the visualized :class:`object <Network.Object.Object>`.
        """
        
        return self._weight
    
    
    def setWeight(self, weight):
        """
        Set the weight of the visualized :class:`object <Network.Object.Object>`.
        
        The weight parameter should be a float value with 1.0 being a neutral weight.  Currently this only applies to visualized connections.
        """
        
        if self._weight != weight:
            self._weight = weight
            if isinstance(self._shape, PathShape):
                self._shape.setWeight(weight)
            elif self.isPath():
                self._updatePath()
            dispatcher.send(('set', 'weight'), self)
    
    
    def addChildVisible(self, childVisible):
        """
        Make the indicated visible a child of this visualized :class:`object <Network.Object.Object>`.
        
        A child visible will be drawn inside of the parent visible.
        """
        
        if not isinstance(childVisible, Visible):
            raise TypeError, 'The argument passed to addChildVisible() must be a visible in the same display.'
         
        if childVisible not in self.children:
            if childVisible.parent:
                childVisible.parent.removeChildVisible(childVisible)
            self.children.append(childVisible)
            childVisible.parent = self
            self.childGroup.addChild(childVisible.sgNode)
            dispatcher.connect(self._childArrangedWeightChanged, ('set', 'arrangedWeight'), childVisible)
            if childVisible.sizeIsAbsolute():
                for ancestor in childVisible.ancestors():
                    dispatcher.connect(childVisible._maintainAbsoluteSize, ('set', 'position'), ancestor)
                    dispatcher.connect(childVisible._maintainAbsoluteSize, ('set', 'size'), ancestor)
                    dispatcher.connect(childVisible._maintainAbsoluteSize, ('set', 'rotation'), ancestor)
            self._updateOpacity()
            if self.arrangedAxis is None:
                childVisible._updateTransform()
            else:
                self._arrangeChildren()
            dispatcher.send(('set', 'children'), self)
    
    
    def removeChildVisible(self, childVisible):
        """
        Remove the indicated visible from this container visible.
        
        After this call the indicated visible will have no parent.
        """
        
        if childVisible in self.children:
            if childVisible.sizeIsAbsolute():
                for ancestor in childVisible.ancestors():
                    dispatcher.disconnect(childVisible._maintainAbsoluteSize, ('set', 'position'), ancestor)
                    dispatcher.disconnect(childVisible._maintainAbsoluteSize, ('set', 'size'), ancestor)
                    dispatcher.disconnect(childVisible._maintainAbsoluteSize, ('set', 'rotation'), ancestor)
            dispatcher.disconnect(self._childArrangedWeightChanged, ('set', 'arrangedWeight'), childVisible)
            self.childGroup.removeChild(childVisible.sgNode)
            childVisible.parent = None
            self.children.remove(childVisible)
            if not any(self.children):
                self._updateOpacity()
            if self.arrangedAxis is None:
                childVisible._updateTransform()
            else:
                self._arrangeChildren()
            dispatcher.send(('set', 'children'), self)
    
    
    def rootVisible(self):
        """ Return the outermost container of this visible.
        
        If this visible is not contained within any other visible then this visible itself will be returned.
        """
        
        if self.parent is None:
            return self
        else:
            return self.parent.rootVisible()
    
    
    def ancestors(self):
        """
        Return the containers of this visible in a list with the outermost container appearing last.
        
        If this visible is not contained within any others then an empty list will be returned.
        """
        
        ancestors = []
        if self.parent is not None:
            ancestors.append(self.parent)
            ancestors.extend(self.parent.ancestors())
        return ancestors
    
    
    def allChildren(self):
        """
        Return all visibles contained by this visible.
        
        If this visible does not contain any others then an empty list will be returned.
        """
        
        children = []
        for child in self.children:
            children += [child]
            children += child.allChildren()
        return children
    
    
    def _arrangeChildren(self, recurse = True):
        if self.arrangedAxis is None or len(self.children) == 0:
            return
        
        worldSize = self.worldSize()
        
        if self.arrangedAxis == 'largest':
            # Pick the axis in which our size is largest.
            if worldSize[0] >= worldSize[1] and worldSize[0] >= worldSize[2]:
                axisToUse = 'X'
            elif worldSize[1] >= worldSize[0] and worldSize[1] >= worldSize[2]:
                axisToUse = 'Y'
            else:
                axisToUse = 'Z'
        else:
            axisToUse = self.arrangedAxis
        
        childCount = len(self.children)
        weightedChildCount = 0.0
        for child in self.children:
            weightedChildCount += child.arrangedWeight
        if axisToUse == 'X':
            worldSpacing = worldSize[0] * self.arrangedSpacing
            ySize = (worldSize[1] - 2.0 * worldSpacing) / worldSize[1]
            zSize = (worldSize[2] - 2.0 * worldSpacing) / worldSize[2]
            curX = -0.5 + self.arrangedSpacing
            for index in range(0, childCount):
                child = self.children[index]
                childWidth = (1.0 - self.arrangedSpacing * (childCount + 1.0)) / weightedChildCount * child.arrangedWeight
                child.setPosition((curX + childWidth / 2.0, 0.0, 0.0))
                if not child.sizeIsAbsolute():
                    child.setSize((childWidth, max(ySize, 0.5), max(zSize, 0.5)))
                child.setPositionIsFixed(True)
                curX += childWidth + self.arrangedSpacing
        elif axisToUse == 'Y':
            worldSpacing = worldSize[1] * self.arrangedSpacing
            xSize = (worldSize[0] - 2.0 * worldSpacing) / worldSize[0]
            zSize = (worldSize[2] - 2.0 * worldSpacing) / worldSize[2]
            curY = 0.5 - self.arrangedSpacing
            for index in range(0, childCount):
                child = self.children[index]
                childHeight = (1.0 - self.arrangedSpacing * (childCount + 1.0)) / weightedChildCount * child.arrangedWeight
                child.setPosition((0.0, curY - childHeight / 2.0, 0.0))
                if not child.sizeIsAbsolute():
                    child.setSize((max(xSize, 0.5), childHeight, max(zSize, 0.5)))
                child.setPositionIsFixed(True)
                curY -= childHeight + self.arrangedSpacing
        else:   # axisToUse == 'Z'
            worldSpacing = worldSize[2] * self.arrangedSpacing
            xSize = (worldSize[0] - 2.0 * worldSpacing) / worldSize[0]
            ySize = (worldSize[1] - 2.0 * worldSpacing) / worldSize[1]
            curZ = -0.5 + self.arrangedSpacing
            for index in range(0, childCount):
                child = self.children[index]
                childDepth = (1.0 - self.arrangedSpacing * (childCount + 1.0)) / weightedChildCount * child.arrangedWeight
                child.setPosition((0.0, 0.0, curZ + childDepth / 2.0))
                if not child.sizeIsAbsolute():
                    child.setSize((max(xSize, 0.5), max(ySize, 0.5), childDepth))
                child.setPositionIsFixed(True)
                curZ += childDepth + self.arrangedSpacing
        
        if recurse:
            for child in self.children:
                child._arrangeChildren(recurse = True)
    
    
    def setArrangedAxis(self, axis = 'largest', recurse = False):
        """
        Automatically arrange the children of this visualized :class:`object <Network.Object.Object>` along the specified axis.
        
        The axis value should be one of 'largest', 'X', 'Y', 'Z' or None.  When 'largest' is indicated the children will be arranged along whichever axis is longest at any given time.  Resizing the parent object therefore can change which axis is used.
        
        If recurse is True then all descendants will have their axes set as well.
        """
        
        if axis not in [None, 'largest', 'X', 'Y', 'Z']:
            raise ValueError, 'The axis argument passed to setArrangedAxis() must be one of \'largest\', \'X\', \'Y\', \'Z\' or None.'
        
        if axis != self.arrangedAxis:
            self.arrangedAxis = axis
            if axis is None:
                for child in self.children:
                    child.setPositionIsFixed(False)
            else:
                self._arrangeChildren(False)
            dispatcher.send(('set', 'arrangedAxis'), self)
        
        if recurse:
            for child in self.children:
                child.setArrangedAxis(axis = axis, recurse = True)
    
    
    def setArrangedSpacing(self, spacing = .02, recurse = False):
        """
        Set the visible spacing between the children of the visualized :class:`object <Network.Object.Object>`.
        
        The spacing is measured as a fraction of the whole.  So a value of .02 uses 2% of the parent's size for the spacing between each object.
         
        If recurse is True then all descendants will have their spacing set as well.
        """
        
        if not isinstance(spacing, (int, float)):
            raise TypeError, 'The spacing argument passed to setArrangedSpacing() must be an integer or floating point value.'
        
        if spacing != self.arrangedSpacing:
            self.arrangedSpacing = float(spacing)
            self._arrangeChildren(False)
            dispatcher.send(('set', 'arrangedSpacing'), self)
            self.display.Update()
        
        if recurse:
            for child in self.children:
                child.setArrangedSpacing(spacing = spacing, recurse = True)
    
    
    def setArrangedWeight(self, weight = weight):
        """
        Set the amount of its parent's space the visualized :class:`object <Network.Object.Object>` should use compared to its siblings.
        
        Larger weight values will result in more of the parent's space being used.
         
        If recurse is True then all descendants will have their spacing set as well.
        """
        
        if not isinstance(weight, (int, float)):
            raise TypeError, 'The weight argument passed to setArrangedWeight() must be an integer or floating point value.'
        
        if weight != self.arrangedWeight:
            self.arrangedWeight = weight
            self._arrangeChildren(False)
            dispatcher.send(('set', 'arrangedWeight'), self)
            self.display.Update()
    
    
    def _childArrangedWeightChanged(self, signal, sender, **arguments):
        self._arrangeChildren()
    
    
    def _addDependency(self, otherVisible, attribute):
        self._dependencies.add(otherVisible)
        dispatcher.connect(self._dependentVisibleChanged, ('set', attribute), otherVisible)
        ancestor = otherVisible.parent
        while ancestor is not None:
            dispatcher.connect(self._dependentVisibleChanged, ('set', attribute), ancestor)
            ancestor = ancestor.parent
    
    
    def _dependentVisibleChanged( self, signal, sender, event=None, value=None, **arguments):
        if self.isPath():
            self._updatePath()
    
    
    def _positionSizeRotation(self, startPoint, endPoint):
        if len(startPoint) == 2:
            startPoint = list(startPoint) + [0.0]
        if len(endPoint) == 2:
            endPoint = list(endPoint) + [0.0]
        position = ((startPoint[0] + endPoint[0]) / 2.0, 
                    (startPoint[1] + endPoint[1]) / 2.0, 
                    (startPoint[2] + endPoint[2]) / 2.0)
        dx = endPoint[0] - startPoint[0]
        dy = endPoint[1] - startPoint[1]
        dz = endPoint[2] - startPoint[2]
        dsize = (self._weight / 500.0, sqrt(dx * dx + dy * dy + dz * dz), self._weight / 500.0)
        dxz = sqrt(dx**2.0 + dz**2.0)
        dAngle = atan2(dxz, dy)
        cross = osg.Vec3f(0, 1, 0) ^ osg.Vec3f(dx, dy, dz)
        cross.normalize()
        rotation = (cross.x(), cross.y(), cross.z(), dAngle)
        return (position, dsize, rotation)
    
    
    def _isDraggable(self):
        return (self.positionIsFixed() == False and self._pathStart is None)
    
    
    def setTexture(self, texture):
        """
        Set the texture used to paint the surface of the visualized :class:`object <Network.Object.Object>`.
        
        >>> display.setVisibleTexture(region1, library.texture('Stripes'))
        
        The texture parameter should be an object obtained from the :class:`library <Library.Library.Library>` or None.
        """
        
        if not isinstance(texture, (Texture, type(None))):
            raise TypeError, 'The texture argument passed to setTexture() must be a texture from the library.'
        
        if self._staticTexture != texture:
            if texture is None:
                self._stateSet.removeTextureAttribute(0, osg.StateAttribute.TEXTURE)
            else:
                self._stateSet.setTextureAttributeAndModes(0, texture.textureData(), osg.StateAttribute.ON)
            self._staticTexture = texture
            dispatcher.send(('set', 'texture'), self)
    
    
    def texture(self):
        """
        Set the texture used to paint the surface of the visualized :class:`object <Network.Object.Object>`.
        """
        
        return self._staticTexture
    
        
    def setTextureScale(self, scale):
        """
        Set the scale of the texture used to paint the surface of the visualized :class:`object <Network.Object.Object>`.
        
        The scale parameter can be used to reduce or enlarge the texture relative to the visualized object.
        """
        
        if not isinstance(scale, (float, int)):
            raise TypeError, 'The scale argument passed to setTextureScale() must be a number.'
        
        if self._staticTextureScale != scale:
            if scale == 1.0:
                self._stateSet.removeTextureAttribute(0, osg.StateAttribute.TEXMAT)
            else:
                textureMatrix = osg.TexMat()
                textureMatrix.setMatrix(osg.Matrixd.scale(scale, scale, scale))
                self._stateSet.setTextureAttributeAndModes(0, textureMatrix, osg.StateAttribute.ON);
            self._staticTextureScale = scale
            self._updateFlowAnimation()
            dispatcher.send(('set', 'textureScale'), self)
    
    
    def textureScale(self):
        """
        Return the scale of the texture used to paint the surface of the visualized :class:`object <Network.Object.Object>`.
        """
        
        return self._staticTextureScale
    
    
    def setFlowTo(self, showFlow = True):
        """
        Set whether the flow of information from the start of the path towards the end should be shown.
        """
        
        # Convert to a bool.
        showFlow = True if showFlow else False
        
        if showFlow != self._flowTo:
            self._flowTo = (showFlow == True)
            dispatcher.send(('set', 'flowTo'), self)
            self._updateFlowAnimation()
    
    
    def flowTo(self):
        """
        Return whether the flow of information from the start of the path towards the end should be shown.
        """
        
        return self._flowTo
    
    
    def setFlowToColor(self, color):
        """
        Set the color of the pulse used to show the flow of information from the start of the path towards the end. 
        
        The color argument should be None or a tuple or list of three values between 0.0 and 1.0 indicating the red, green and blue values of the color.  For example:
        
        * (0.0, 0.0, 0.0) -> black
        * (1.0, 0.0, 0.0) -> red
        * (0.0, 1.0, 0.0) -> green
        * (0.0, 0.0, 1.0) -> blue
        * (1.0, 1.0, 1.0) -> white
        
        If None is passed then the default flow color will be used.
        """
        
        if not isinstance(color, (list, tuple, type(None))) or (color != None and len(color) != 3):
            raise ValueError, 'The color passed to setFlowToColor() must be None or a tuple or list of three numbers.'
        for colorComponent in color:
            if not isinstance(colorComponent, (int, float)) or colorComponent < 0.0 or colorComponent > 1.0:
                raise ValueError, 'The components of the color passed to setFlowToColor() must all be numbers between 0.0 and 1.0, inclusive.'
        
        if color != None and len(color) == 3:
            color = (color[0], color[1], color[2], 1.0)
        if color != self._flowToColor:
            self._flowToColor = color
            if self._flowToColor is None:
                self._stateSet.removeUniform('flowToColor')
            else:
                self._stateSet.addUniform(osg.Uniform('flowToColor', osg.Vec4f(*self._flowToColor)))
            self._updateFlowAnimation()
            dispatcher.send(('set', 'flowToColor'), self)
    
    
    def flowToColor(self):
        """
        Return the color of the pulse used to show the flow of information from the start of the path towards the end. 
        """
        
        return self._flowToColor
    
    
    def setFlowToSpacing(self, spacing):
        """
        Set the spacing between pulses used to show the flow of information from the start of the path towards the end. 
        
        The spacing argument should be a number value in world-space coordinates.
        """
        
        if not isinstance(spacing, (int, float)):
            raise TypeError, 'The spacing passed to setFlowToSpacing() must be a number.'
        
        if spacing != self._flowToSpacing:
            self._flowToSpacing =float(spacing)
            if self._flowToSpacing is None:
                self._stateSet.removeUniform('flowToSpacing')
            else:
                self._stateSet.addUniform(osg.Uniform('flowToSpacing', self._flowToSpacing))
            self._updateFlowAnimation()
            dispatcher.send(('set', 'flowToSpacing'), self)
    
    
    def flowToSpacing(self):
        """
        Return the spacing between pulses used to show the flow of information from the start of the path towards the end. 
        """
        
        return self._flowToSpacing
    
    
    def setFlowToSpeed(self, speed):
        """
        Set the speed of the pulses used to show the flow of information from the start of the path towards the end.
        
        The speed argument should be a number value in world-space coordinates per second.
        """
        
        if not isinstance(speed, (int, float)):
            raise TypeError, 'The speed passed to setFlowToSpeed() must be a number.'
        
        if speed != self._flowToSpeed:
            self._flowToSpeed = float(speed)
            if self._flowToSpeed is None:
                self._stateSet.removeUniform('flowToSpeed')
            else:
                self._stateSet.addUniform(osg.Uniform('flowToSpeed', self._flowToSpeed))
            self._updateFlowAnimation()
            dispatcher.send(('set', 'flowToSpeed'), self)
    
    
    def flowToSpeed(self):
        """
        Return the speed of the pulses used to show the flow of information from the start of the path towards the end.
        """
        
        return self._flowToSpeed
    
    
    def setFlowToSpread(self, spread):
        """
        Set the length of the pulse tails used to show the flow of information from the start of the path towards the end.
        
        The spread argument should be a number value from 0.0 (no tail) to 1.0 (tail extends all the way to the next pulse).
        """
        
        if not isinstance(spread, (int, float)):
            raise TypeError, 'The spread passed to setFlowToSpread() must be a number.'
        
        if spread != self._flowToSpread:
            self._flowToSpread = float(spread)
            if self._flowToSpread is None:
                self._stateSet.removeUniform('flowToSpread')
            else:
                self._stateSet.addUniform(osg.Uniform('flowToSpread', self._flowToSpread))
            self._updateFlowAnimation()
            dispatcher.send(('set', 'flowToSpread'), self)
    
    
    def flowToSpread(self):
        """
        Return the length of the pulse tails used to show the flow of information from the start of the path towards the end.
        """
        
        return self._flowToSpread
    
    
    def setFlowFrom(self, showFlow = True):
        """
        Set whether the flow of information from the end of the path towards the start should be shown.
        """
        # Convert to a bool.
        showFlow = True if showFlow else False
        
        if showFlow != self._flowFrom:
            self._flowFrom = showFlow
            dispatcher.send(('set', 'flowFrom'), self)
            self._updateFlowAnimation()
    
    
    def flowFrom(self):
        """
        Return whether the flow of information from the end of the path towards the start should be shown.
        """
        
        return self._flowFrom
    
    
    def setFlowFromColor(self, color):
        """
        Set the color of the pulse used to show the flow of information from the end of the path towards the start. 
        
        The color argument should be None or a tuple or list of three values between 0.0 and 1.0 indicating the red, green and blue values of the color.  For example:
        
        * (0.0, 0.0, 0.0) -> black
        * (1.0, 0.0, 0.0) -> red
        * (0.0, 1.0, 0.0) -> green
        * (0.0, 0.0, 1.0) -> blue
        * (1.0, 1.0, 1.0) -> white
        
        If None is passed then the default flow color will be used.
        """
        
        if not isinstance(color, (list, tuple, type(None))) or (color != None and len(color) != 3):
            raise ValueError, 'The color passed to setFlowFromColor() must be a tuple or list of three numbers.'
        for colorComponent in color:
            if not isinstance(colorComponent, (int, float)) or colorComponent < 0.0 or colorComponent > 1.0:
                raise ValueError, 'The components of the color passed to setFlowFromColor() must all be numbers between 0.0 and 1.0, inclusive.'
        
        if color != None and len(color) == 3:
            color = (color[0], color[1], color[2], 1.0)
        if color != self._flowFromColor:
            self._flowFromColor = color
            if self._flowFromColor is None:
                self._stateSet.removeUniform('flowFromColor')
            else:
                self._stateSet.addUniform(osg.Uniform('flowFromColor', osg.Vec4f(*self._flowFromColor)))
            self._updateFlowAnimation()
            dispatcher.send(('set', 'flowFromColor'), self)
    
    
    def flowFromColor(self):
        """
        Return the color of the pulse used to show the flow of information from the end of the path towards the start. 
        """
        
        return self._flowFromColor
    
    
    def setFlowFromSpacing(self, spacing):
        """
        Set the spacing between pulses used to show the flow of information from the end of the path towards the start. 
        
        The spacing argument should be a number value in world-space coordinates.
        """
        
        if not isinstance(spacing, (int, float)):
            raise TypeError, 'The spacing passed to setFlowFromSpacing() must be a number.'
        
        if spacing != self._flowFromSpacing:
            self._flowFromSpacing = float(spacing)
            if self._flowFromSpacing is None:
                self._stateSet.removeUniform('flowFromSpacing')
            else:
                self._stateSet.addUniform(osg.Uniform('flowFromSpacing', self._flowFromSpacing))
            self._updateFlowAnimation()
            dispatcher.send(('set', 'flowFromSpacing'), self)
    
    
    def flowFromSpacing(self):
        """
        Return the spacing between pulses used to show the flow of information from the end of the path towards the start. 
        """
        
        return self._flowFromSpacing
    
    
    def setFlowFromSpeed(self, speed):
        """
        Set the speed of the pulses used to show the flow of information from the end of the path towards the start.
        
        The speed argument should be a number value in world-space coordinates per second.
        """
        
        if not isinstance(speed, (int, float)):
            raise TypeError, 'The speed passed to setFlowFromSpeed() must be a number.'
        
        if speed != self._flowFromSpeed:
            self._flowFromSpeed = float(speed)
            if self._flowFromSpeed is None:
                self._stateSet.removeUniform('flowFromSpeed')
            else:
                self._stateSet.addUniform(osg.Uniform('flowFromSpeed', self._flowFromSpeed))
            self._updateFlowAnimation()
            dispatcher.send(('set', 'flowFromSpeed'), self)
    
    
    def flowFromSpeed(self):
        """
        Return the speed of the pulses used to show the flow of information from the end of the path towards the start.
        """
        
        return self._flowFromSpeed
    
    
    def setFlowFromSpread(self, spread):
        """
        Set the length of the pulse tails used to show the flow of information from the end of the path towards the start.
        
        The spread argument should be a number value from 0.0 (no tail) to 1.0 (tail extends all the way to the next pulse).
        """
        
        if not isinstance(spread, (int, float)):
            raise TypeError, 'The spread passed to setFlowFromSpread() must be a number.'
        
        if spread != self._flowFromSpread:
            self._flowFromSpread = float(spread)
            if self._flowFromSpread is None:
                self._stateSet.removeUniform('flowFromSpread')
            else:
                self._stateSet.addUniform(osg.Uniform('flowFromSpread', self._flowFromSpread))
            self._updateFlowAnimation()
            dispatcher.send(('set', 'flowFromSpread'), self)
    
    
    def flowFromSpread(self):
        """
        Return the length of the pulse tails used to show the flow of information from the end of the path towards the start.
        """
        
        return self._flowFromSpread
    
    
    def _updateFlowAnimation(self):
        if self._animateFlow and (self._flowTo or self._flowFrom):
            self._stateSet.addUniform(osg.Uniform('flowTo', self._flowTo))
            self._stateSet.addUniform(osg.Uniform('flowFrom', self._flowFrom))
            self._stateSet.addUniform(osg.Uniform('textureScale', (self._size[1] if isinstance(self._shape, UnitShape) else 1.0) / self._staticTextureScale))
            self._stateSet.addUniform(osg.Uniform('hasTexture', self._staticTexture != None))
            self._stateSet.setAttributeAndModes(Visible.flowProgram, osg.StateAttribute.ON)
        elif self._stateSet.getAttribute(osg.StateAttribute.PROGRAM) is not None:
            self._stateSet.removeAttribute(osg.StateAttribute.PROGRAM)
            self._stateSet.removeUniform('flowTo')
            self._stateSet.removeUniform('flowFrom')
            self._stateSet.removeUniform('textureScale')
            self._stateSet.removeUniform('hasTexture')
    
    
    def animateFlow(self, animate=True):
        if self._animateFlow != animate:
            self._animateFlow = animate
            self._updateFlowAnimation()
        
        
    def _updatePath(self):
        path = list(self._pathMidPoints)
        path.insert(0, self._pathStart.worldPosition())
        path.append(self._pathEnd.worldPosition())
        
        if self._pathStart._shape:
            # Try to find the point where the path intersects the shape.
            rayOrigin = path[1]
            if len(path) > 2:
                rayDirection = (path[1][0] - path[2][0], path[1][1] - path[2][1], path[1][2] - path[2][2])
            else:
                rayDirection = (path[0][0] - path[1][0], path[0][1] - path[1][1], path[0][2] - path[1][2])
            if isinstance(self._pathStart._shape, UnitShape):
                # Translate the ray into the shape's coordinate system.
                size = self._pathStart.worldSize()
                rayOrigin = ((rayOrigin[0] - path[0][0]) / size[0], (rayOrigin[1] - path[0][1]) / size[1], (rayOrigin[2] - path[0][2]) / size[2])
                rayDirection = (rayDirection[0] / size[0], rayDirection[1] / size[1], rayDirection[2] / size[2])
            intersectionPoint = self._pathStart._shape.intersectionPoint(rayOrigin, rayDirection)
            if intersectionPoint:
                if isinstance(self._pathStart._shape, UnitShape):
                    # Translate back into world space coordinates.
                    intersectionPoint = (intersectionPoint[0] * size[0] + path[0][0], intersectionPoint[1] * size[1] + path[0][1], intersectionPoint[2] * size[2] + path[0][2])
                path[0:1] = [intersectionPoint]
        
        if self._pathEnd._shape:
            # Try to find the point where the path intersects the shape.
            rayOrigin = path[-2]
            if len(path) > 2:
                rayDirection = (path[-2][0] - path[-3][0], path[-2][1] - path[-3][1], path[-2][2] - path[-3][2])
            else:
                rayDirection = (path[-1][0] - path[-2][0], path[-1][1] - path[-2][1], path[-1][2] - path[-2][2])
            if isinstance(self._pathEnd._shape, UnitShape):
                # Translate the ray into the shape's coordinate system.
                size = self._pathEnd.worldSize()
                rayOrigin = ((rayOrigin[0] - path[-1][0]) / size[0], (rayOrigin[1] - path[-1][1]) / size[1], (rayOrigin[2] - path[-1][2]) / size[2])
                rayDirection = (rayDirection[0] / size[0], rayDirection[1] / size[1], rayDirection[2] / size[2])
            intersectionPoint = self._pathEnd._shape.intersectionPoint(rayOrigin, rayDirection)
            if intersectionPoint:
                if isinstance(self._pathEnd._shape, UnitShape):
                    # Translate back into world space coordinates.
                    intersectionPoint = (intersectionPoint[0] * size[0] + path[-1][0], intersectionPoint[1] * size[1] + path[-1][1], intersectionPoint[2] * size[2] + path[-1][2])
                path[-1:] = [intersectionPoint]
        
        if isinstance(self._shape, UnitShape):
            # Create a straight connection from start to end
            # TODO: Will this object ever have a parent?  If so then we'll have to translate world to local coordinates here.
            position, size, rotation = self._positionSizeRotation(path[0], path[-1])
            self.setPosition(position)
            self.setSize(size)
            self.setRotation(rotation)
        else:
            minBound = (1e300, 1e300, 1e300)
            maxBound = (-1e300, -1e300, -1e300)
            for point in path:
                minBound = (min(minBound[0], point[0]), min(minBound[1], point[1]), min(minBound[2], point[2]))
                maxBound = (max(maxBound[0], point[0]), max(maxBound[1], point[1]), max(maxBound[2], point[2]))
                
            self._position = ((maxBound[0] + minBound[0]) / 2.0, (maxBound[1] + minBound[1]) / 2.0, (maxBound[2] + minBound[2]) / 2.0)
            self._size = (maxBound[0] - minBound[0], maxBound[1] - minBound[1], maxBound[2] - minBound[2])
            self._rotation = (0, 1, 0, 0)
            
            if isinstance(self._shape, PathShape):
                self._shape.setPoints(path)
            
            self._updateTransform()
        
        self._updateFlowAnimation()
        
        
    def setPathEndPoints(self, startVisible, endVisible):
        """
        Set the start and end points of this path.
        
        The startVisible and endVisible arguments should be other visibles in the same display as this visible.
        """
        
        if not isinstance(startVisible, (Visible, type(None))) or not isinstance(endVisible, (Visible, type(None))):
            raise TypeError, 'The arguments passed to setPathEndPoints() must be Visible instances or None.'
        if startVisible.display != self.display or startVisible == self or endVisible.display != self.display or endVisible == self:
            raise ValueError, 'The arguments passed to setPathEndPoints() must be other visibles in the same display as this visible.'
        
        if startVisible != self._pathStart or endVisible != self._pathEnd:
            if startVisible != self._pathStart:
                if self._pathStart:
                    self._pathStart.dependentVisibles.remove(self)
                self._pathStart = startVisible
                if self._pathStart:
                    self._addDependency(startVisible, 'position')
                    self._addDependency(startVisible, 'size')
                    self._addDependency(startVisible, 'shape')
                    startVisible.connectedPaths.append(self)
                    self._pathStart.dependentVisibles += [self]
            
            if endVisible != self._pathEnd:
                if self._pathEnd:
                    self._pathEnd.dependentVisibles.remove(self)
                self._pathEnd = endVisible
                if self._pathEnd:
                    self._addDependency(endVisible, 'position')
                    self._addDependency(endVisible, 'size')
                    self._addDependency(endVisible, 'shape')
                    endVisible.connectedPaths.append(self)
                    self._pathEnd.dependentVisibles += [self]
            
            self._updatePath()
            
            dispatcher.send(('set', 'path'), self)
    
    
    def pathEndPoints(self):
        """
        Return the start and end points of this path.
        """
        
        return (self._pathStart, self._pathEnd)
    
    
    def _pathCounterpart(self, visible):
        if self._pathStart == visible:
            return self._pathEnd
        elif self._pathEnd == visible:
            return self._pathStart
        else:
            raise ValueError, 'The visible passed to _pathCounterpart is not connected to the path.'
    
    
    def setPathMidPoints(self, midPoints):
        """
        Set any additional mid-points that should be used to render the path.
        
        The mid-points should be a list of world-space coordinates, e.g. [(0.1, 0.3), (0.1, 0.5), (0.2, 0.5)] or None.
        """
        
        if midPoints == None:
            midPoints = []
        
        if not isinstance(midPoints, (list, tuple)):
            raise TypeError, 'The argument passed to setPathMidPoints() must be a list, a tuple or None.'
        for midPoint in midPoints:
            # TODO: figure out a way to skip this part if we're called from Display.setVisiblePath() since it already validated the mid-points.
            if not isinstance(midPoint, (list, tuple)) or len(midPoint) not in (2, 3):
                raise ValueError, 'The mid-points passed to setPathMidPoints() must be a list or tuple of two or three numbers.'
            for midPointDim in midPoint:
                if not isinstance(midPointDim, (int, float)):
                    raise ValueError, 'Each list or tuple mid-point passed to setPathMidPoints() must contain only numbers.'
        
        if midPoints != self._pathMidPoints:
            self._pathMidPoints = midPoints
            self._updatePath()
            dispatcher.send(('set', 'pathMidPoints'), self)
    
    
    def pathMidPoints(self):
        """
        Return any additional mid-points that should be used to render the path.
        """
        
        return self._pathMidPoints
    
    
    def isPath(self):
        """
        Return whether this visible is a path.
        """
        
        return self._pathStart is not None
    
    
    def setGlowColor(self, color):
        if color != self._glowColor:
            if self._shape is not None:
                # TODO: use a shader effect to produce the glow rather than additional geometry
                w, h, d = self.size()
                if color is None or w == 0.0 or h == 0.0 or d == 0.0 or isinstance(self._shape, PathShape):
                    if self._glowNode is not None:
                        self.sgNode.removeChild(self._glowNode)
                        self._glowNode = None
                        self._glowNodeMaterial = None
                else:
                    if self._glowNode is None:
                        self._glowNode = osg.MatrixTransform(osg.Matrixd.scale(osg.Vec3((w * 1.01) / w, (h * 1.01) / h, (d * 1.01) / d)))
                        glowGeode = osg.Geode()
                        glowGeode.setName(str(self.displayId))
                        glowGeode.addDrawable(self._shape.geometry())
                        self._glowNode.addChild(glowGeode)
                        stateSet1 = self._glowNode.getOrCreateStateSet()
                        stateSet1.clear()
                        self._glowNodeMaterial = osg.Material()
                        stateSet1.setAttribute(self._glowNodeMaterial)
                        self.sgNode.addChild(self._glowNode)
                    else:
                        stateSet1 = self._glowNode.getOrCreateStateSet()
                    colorVec = osg.Vec4(color[0], color[1], color[2], color[3])
                    self._glowNodeMaterial.setDiffuse(osg.Material.FRONT_AND_BACK, colorVec)
                    self._glowNodeMaterial.setEmission(osg.Material.FRONT_AND_BACK, colorVec)
                    self._glowNodeMaterial.setAlpha(osg.Material.FRONT_AND_BACK, color[3])
                    if color[3] == 1:
                        stateSet1.setRenderingHint(osg.StateSet.TRANSPARENT_BIN)
                        stateSet1.setMode(osg.GL_BLEND, osg.StateAttribute.OFF)
                    else:
                        stateSet1.setMode(osg.GL_BLEND, osg.StateAttribute.ON)
                        # Place more deeply nested regions in lower render bins so they are rendered before the containing visible.
                        # Each nesting depth needs four render bins: two for the front and back face of the shape and one for the glow shape.
                        # This assumes a maximum nesting depth of 10.
                        sceneDepth = len(self.ancestors())
                        stateSet1.setRenderBinDetails(40 - sceneDepth * 2, 'DepthSortedBin')
                
            self._glowColor = color
            dispatcher.send(('set', 'glowColor'), self)
    
    
    def __del__(self):
        self.children = []
        if self._pathStart:
            self._pathStart.dependentVisibles.remove(self)
        if self._pathEnd:
            self._pathEnd.dependentVisibles.remove(self)
    
