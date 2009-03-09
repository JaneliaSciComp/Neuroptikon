import osg, osgFX, osgText

from Network.Region import Region
from Network.Neuron import Neuron
from Network.Arborization import Arborization
from Network.Synapse import Synapse
from Network.Stimulus import Stimulus
from Network.Innervation import Innervation
from AnimatedTextureCallback import AnimatedTextureCallback

from wx.py import dispatcher
from math import atan2, pi, sqrt
import random
import xml.etree.ElementTree as ElementTree


class Visible(object):
    """Instances of this class map a network object (neurion, region, etc.) to a specific display.  They capture all of the attributes needed to render the object(s)."""
    
    # Objects inside a unit cube
    geometries = {"ball": osg.Sphere(osg.Vec3(0, 0, 0), 0.5), 
                  "box": osg.Box(osg.Vec3(0, 0, 0), 1), 
                  "capsule": osg.Capsule(osg.Vec3(0, 0, 0), 0.25, 0.5), 
                  "cone": osg.Cone(osg.Vec3(0, -0.25, 0), 0.5, 1), # have to offset center <http://www.mail-archive.com/osg-users@lists.openscenegraph.org/msg07081.html>
                  "tube": osg.Cylinder(osg.Vec3(0, 0, 0), 0.5, 1)}
    geometries["capsule"].setRotation( osg.Quat(-pi / 2.0, osg.Vec3d(1, 0, 0)))
    geometries["cone"].setRotation( osg.Quat(-pi / 2.0, osg.Vec3d(1, 0, 0)))
    geometries["tube"].setRotation( osg.Quat(-pi / 2.0, osg.Vec3d(1, 0, 0)))
    
    geometryInterior = {"ball": osg.Matrixd.scale(1.0 / sqrt(3), 1.0 / sqrt(3), 1.0 / sqrt(3)), 
                        "box": osg.Matrixd.identity(), 
                        "capsule": osg.Matrixd.scale(sqrt(1.0 / 8.0) * 0.9, 1.0 - 0.5 / sqrt(3), sqrt(1.0 / 8.0) * 0.9), 
                        "cone": osg.Matrixd.scale(sqrt(1.0 / 8.0), 0.5, sqrt(1.0 / 8.0)) * osg.Matrixd.translate(0.0, -0.25, 0.0), 
                        "tube": osg.Matrixd.scale(1.0 / sqrt(2), 1.0, 1.0 / sqrt(2))}
        
    # TODO: osgText::Font* font = osgText::readFontFile("fonts/arial.ttf");
    
    
    def __init__(self, display, client):
        self.display = display
        self.displayId = display.nextUniqueId() # a unique identifier within the display
        self.client = client
        self._motionTexture1 = display.textureFromImage('texture2.png')
        self._motionTexture2 = display.textureFromImage('texture2.png')
        self._glowColor = None
        self._glowNode = None
        self._position = (random.random() - 0.5, random.random() - 0.5, 0)
        self._positionIsFixed = False
        self._size = (.001, .001, .001)
        self._sizeIsFixed = True
        self.sizeIsAbsolute = False
        self._rotation = (0, 0, 1, 0)
        self._weight = 1.0
        self._dependencies = set()
        self._label = None
        self._labelNode = None
        self._shapeName = None
        self._color = (0.5, 0.5, 0.5)
        self._opacity = 1.0
        self._path = None
        self.pathStart = None
        self.pathEnd = None
        self.flowTo = False
        self.flowFrom = False
        self.sgNode = osg.MatrixTransform()
        self._shapeGeode = osg.Geode()
        self._shapeGeode.setName(str(self.displayId))
        self._shapeDrawable = None
        self._stateSet = self._shapeGeode.getOrCreateStateSet()
        self._stateSet.setAttributeAndModes(osg.BlendFunc(), osg.StateAttribute.ON)
        self._material = osg.Material()
        self._material.setDiffuse(osg.Material.FRONT_AND_BACK, osg.Vec4(0.5, 0.5, 0.5, 1))
        self._material.setAmbient(osg.Material.FRONT_AND_BACK, osg.Vec4(0.5, 0.5, 0.5, 1))
        self._stateSet.setAttribute(self._material)
        self.sgNode.addChild(self._shapeGeode)
        self._textGeode = osg.Geode()
        self._textGeode.setName(str(self.displayId))
        self._textDrawable = None
        self.sgNode.addChild(self._textGeode)
        self._staticTexture = None
        self._staticTextureTransform = None
        self._animateFlow = False
        self.parent = None
        self.children = []
        self.arrangedAxis = 'largest'
        self.arrangedSpacing = 0.02
        self.arrangedWeight = 1.0
        self.childGroup = osg.MatrixTransform(osg.Matrixd.identity())
        self.sgNode.addChild(self.childGroup)
        self.connectedPaths = []
    
    
    @classmethod
    def fromXMLElement(cls, xmlElement, display):
        client = display.network.objectWithId(xmlElement.get('objectId'))
        visible = Visible(display, client)
        visible.displayId = int(xmlElement.get('id'))
        
        # Set any geometry
        geometryElement = xmlElement.find('geometry')
        if geometryElement is not None:
            positionElement = geometryElement.find('position')
            if positionElement is not None:
                x = float(positionElement.get('x'))
                y = float(positionElement.get('y'))
                z = float(positionElement.get('z'))
                visible.setPosition((x, y, z))
                if positionElement.get('fixed') == 'true':
                    visible.setPositionIsFixed(True)
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
            rotationElement = geometryElement.find('rotation')
            if rotationElement is not None:
                x = float(rotationElement.get('x'))
                y = float(rotationElement.get('y'))
                z = float(rotationElement.get('z'))
                angle = float(rotationElement.get('angle'))
                visible.setRotation((x, y, z, angle))
        
        # Set any appearance
        appearanceElement = xmlElement.find('appearance')
        if appearanceElement is not None:
            visible.setLabel(appearanceElement.findtext('label'))
            visible.setShape(appearanceElement.findtext('shape'))
            colorElement = appearanceElement.find('color')
            if colorElement is not None:
                red = float(colorElement.get('r'))
                green = float(colorElement.get('g'))
                blue = float(colorElement.get('b'))
                visible.setColor((red, green, blue))
            opacityText = appearanceElement.findtext('opacity')
            if opacityText is not None:
                visible.setOpacity(float(opacityText))
            weightText = appearanceElement.findtext('weight')
            if weightText is not None:
                visible.setWeight(float(weightText))
        
        # Set up any arrangement
        arrangementElement = xmlElement.find('arrangement')
        if arrangementElement is not None:
            axis = arrangementElement.get('axis')
            if axis is not None:
                visible.setArrangedAxis(axis)
            spacing = arrangementElement.get('spacing')
            if spacing is not None:
                visible.setArrangedSpacing(float(spacing))
            weight = arrangementElement.get('weight')
            if weight is not None:
                visible.setArrangedWeight(float(weight))
        
        # Set up any path
        pathElement = xmlElement.find('path')
        if pathElement is not None:
            pathStart = display.visibleIds[int(pathElement.get('startVisibleId'))]
            pathEnd = display.visibleIds[int(pathElement.get('endVisibleId'))]
            flowTo = pathElement.get('flowTo')
            flowFrom = pathElement.get('flowTo')
            if pathStart is None or pathEnd is None:
                raise ValueError, gettext('Could not create path')
            visible.setFlowDirection(pathStart, pathEnd, flowTo, flowFrom)
            visible.setPath([], pathStart, pathEnd)
        
        # Create any child visibles
        for visibleElement in xmlElement.findall('Visible'):
            childVisible = Visible.fromXMLElement(visibleElement, display)
            if childVisible is None:
                raise ValueError, gettext('Could not create visualized item')
            display.addVisible(childVisible, visible)
        
        return visible
    
    
    def toXMLElement(self, parentElement):
        visibleElement = ElementTree.SubElement(parentElement, 'Visible')
        visibleElement.set('id', str(self.displayId))
        if self.client is not None:
            visibleElement.set('objectId', str(self.client.networkId))
        
        # Add the geometry
        geometryElement = ElementTree.SubElement(visibleElement, 'geometry')
        positionElement = ElementTree.SubElement(geometryElement, 'position')
        positionElement.set('x', str(self._position[0]))
        positionElement.set('y', str(self._position[1]))
        positionElement.set('z', str(self._position[2]))
        positionElement.set('fixed', 'true' if self._positionIsFixed else 'false')
        sizeElement = ElementTree.SubElement(geometryElement, 'size')
        sizeElement.set('x', str(self._size[0]))
        sizeElement.set('y', str(self._size[1]))
        sizeElement.set('z', str(self._size[2]))
        sizeElement.set('fixed', 'true' if self.sizeIsFixed else 'false')
        sizeElement.set('absolute', 'true' if self.sizeIsAbsolute else 'false')
        rotationElement = ElementTree.SubElement(geometryElement, 'rotation')
        rotationElement.set('x', str(self._rotation[0]))
        rotationElement.set('y', str(self._rotation[1]))
        rotationElement.set('z', str(self._rotation[2]))
        rotationElement.set('angle', str(self._rotation[3]))
        
        # Add the appearance
        appearanceElement = ElementTree.SubElement(visibleElement, 'appearance')
        if self._label is not None:
            ElementTree.SubElement(appearanceElement, 'label').text = self._label
        if self._shapeName is not None:
            ElementTree.SubElement(appearanceElement, 'shape').text = self._shapeName
        colorElement = ElementTree.SubElement(appearanceElement, 'color')
        colorElement.set('r', str(self._color[0]))
        colorElement.set('g', str(self._color[1]))
        colorElement.set('b', str(self._color[2]))
        ElementTree.SubElement(appearanceElement, 'opacity').text = str(self._opacity)  # TODO: ghosting will confuse this
        ElementTree.SubElement(appearanceElement, 'weight').text = str(self._weight)
        # TODO: texture, textureTransform
        
        # Add the arrangement
        arrangementElement = ElementTree.SubElement(visibleElement, 'arrangement')
        arrangementElement.set('axis', str(self.arrangedAxis))
        arrangementElement.set('spacing', str(self.arrangedSpacing))
        arrangementElement.set('weight', str(self.arrangedWeight))
        
        # Add any path
        if self.isPath():
            pathElement = ElementTree.SubElement(visibleElement, 'path')
            pathElement.set('startVisibleId', str(self.pathStart.displayId))
            pathElement.set('endVisibleId', str(self.pathEnd.displayId))
            if self.flowTo is not None:
                pathElement.set('flowTo', 'true' if self.flowTo else 'false')
            if self.flowFrom is not None:
                pathElement.set('flowFrom', 'true' if self.flowFrom else 'false')
        
        # Add any child visibles
        for childVisible in self.children:
            childElement = childVisible.toXMLElement(visibleElement)
            if childElement is None:
                raise ValueError, gettext('Could not save visualized item')
        
        return visibleElement
        
    
    def shape(self):
        """Return the type of shape set for this visualized object, one of 'ball', 'box', 'capsule', 'cone', 'tube' or None"""
        return self._shapeName
    
    
    def setShape(self, shapeName):
        if self._shapeName != shapeName:
            self._shapeName = shapeName
            if self._shapeDrawable:
                self._shapeGeode.removeDrawable(self._shapeDrawable)
            self._shapeDrawable = osg.ShapeDrawable(Visible.geometries[self._shapeName])
            self._shapeGeode.addDrawable(self._shapeDrawable)
            self.childGroup.setMatrix(Visible.geometryInterior[self._shapeName])
            for child in self.children:
                dispatcher.send(('set', 'position'), child)
            # Recreate the glow shape if needed
            if self._glowNode is not None:
                glowColor = self._glowColor
                self.setGlowColor(None)
                self.setGlowColor(glowColor)
            self.display.Refresh()
    
    
    def setLabel(self, label):
        if label is not None:
            if self._textDrawable is None:
                # TODO: This works for 2D but not 3D.  The label gets obscured when the camera is rotated.
                #       It would be ideal to draw the label at the center of the visible and tweak the culling so that the label isn't culled by it's visible's shape.
                #       It would be even better to draw the label in the center of the portion of the shape that is currently visible.
                self._textDrawable = osgText.Text()
                self._textDrawable.setPosition(osg.Vec3(0, 0, 1))
                self._textDrawable.setAxisAlignment(osgText.Text.SCREEN)
                self._textDrawable.setAlignment(osgText.Text.CENTER_CENTER)
                self._textDrawable.setCharacterSizeMode(osgText.Text.SCREEN_COORDS)
                self._textDrawable.setColor(osg.Vec4(0, 0, 0, 1))
                self._textDrawable.setCharacterSizeMode(osgText.Text.SCREEN_COORDS)
                self._textDrawable.setCharacterSize(48)
                self._textGeode.addDrawable(self._textDrawable)
                self._textDrawable.setColor(osg.Vec4(0, 0, 0, self._opacity))
            self._textDrawable.setText(str(label))
        elif label is None and self._textDrawable is not None:
            self._textGeode.removeDrawable(self._textDrawable)
            self._textDrawable = None
        self._label = label
        self.display.Refresh()
    
    
    def label(self):
        return self._label
    
    
    def setColor(self, color):
        if color != self._color:
            colorVec = osg.Vec4(color[0], color[1], color[2], 1)
            self._material.setDiffuse(osg.Material.FRONT_AND_BACK, colorVec)
            self._material.setAmbient(osg.Material.FRONT_AND_BACK, colorVec)
            if self._shapeDrawable is not None:
                self._shapeDrawable.setColor(colorVec)
            self._color = color
            self.display.Refresh()
            dispatcher.send(('set', 'color'), self)
    
    
    def color(self):
        return self._color
    
    
    def setOpacity(self, opacity):
        if opacity < 0.0:
            opacity = 0.0
        elif opacity > 1.0:
            opacity = 1.0
        
        if opacity != self.opacity:
            if self._shapeDrawable is not None:
                self._material.setAlpha(osg.Material.FRONT_AND_BACK, opacity)
                if opacity == 1.0:
                    self._shapeDrawable.getOrCreateStateSet().setRenderingHint(osg.StateSet.OPAQUE_BIN)
                    self._shapeDrawable.getStateSet().setMode(osg.GL_BLEND, osg.StateAttribute.OFF)
                else:
                    self._shapeDrawable.getOrCreateStateSet().setRenderingHint(osg.StateSet.TRANSPARENT_BIN)
                    self._shapeDrawable.getStateSet().setMode(osg.GL_BLEND, osg.StateAttribute.ON)
            
            if self._textDrawable is not None:
                self._textDrawable.setColor(osg.Vec4(0, 0, 0, opacity))
            
            self._opacity = opacity
            self.display.Refresh()
            dispatcher.send(('set', 'opacity'), self)
    
    
    def opacity(self):
        return self._opacity
    
    
    def updateTransform(self):
        # update the transform unless we're under an osgGA.Selection node, i.e. being dragged
        if len(self.sgNode.getParents()) == 0 or self.display.dragSelection is None or self.sgNode.getParent(0).__repr__() != self.display.dragSelection.asGroup().__repr__():
            if self.parent is None or not self.sizeIsAbsolute:
                scale = self._size
            else:
                parentScale = self.parent.worldSize()
                scale = (self._size[0] / parentScale[0], self._size[1] / parentScale[1], self._size[2] / parentScale[2])
            self.sgNode.setMatrix(osg.Matrixd.scale(osg.Vec3d(scale[0], scale[1], scale[2])) * 
                                   osg.Matrixd.rotate(self.rotation()[3], osg.Vec3d(self.rotation()[0], self.rotation()[1], self.rotation()[2])) *
                                   osg.Matrixd.translate(osg.Vec3d(self.position()[0], self.position()[1], self.position()[2])))
    
    
    def position(self):
        return self._position
    
    
    def setPosition(self, position):
        """ Set the position of this visible in unit space.  Positions should be between -0.5 and 0.5 for this visible to be rendered fully inside its parent."""
        if position != self._position:
            self._position = position
            self.updateTransform()
            dispatcher.send(('set', 'position'), self)
            self.display.Refresh()
    
    
    def offsetPosition(self, offset):
        if offset != (0, 0, 0):
            self._position = (self._position[0] + offset[0], self._position[1] + offset[1], self._position[2] + offset[2])
            self.updateTransform()
            self.display.Refresh()
    
    
    def worldPosition(self):
        # TODO: if a parent is rotated does this screw up?
        # TODO: will OSG do this for us?
        
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
        return self._positionIsFixed
    
    
    def setPositionIsFixed(self, flag):
        if self._positionIsFixed != flag:
            self._positionIsFixed = flag
            dispatcher.send(('set', 'position is fixed'), self)
    
    
    def size(self):
        return self._size
    
    
    def setSize(self, size):
        """ Set the size of this visible relative to its parent or in absolute space (depending on the current value of sizeIsAbsolute)."""
        self._size = size
        self.updateTransform()
        dispatcher.send(('set', 'size'), self)
        self._arrangeChildren()
        self.display.Refresh()
    
    
    def sizeIsFixed(self):
        return self._sizeIsFixed
    
    
    def setSizeIsFixed(self, flag):
        if self._sizeIsFixed != flag:
            self._sizeIsFixed = flag
            dispatcher.send(('set', 'size is fixed'), self)
    
    
    def setSizeIsAbsolute(self, sizeIsAbsolute = True):
        if self.sizeIsAbsolute != sizeIsAbsolute:
            self.sizeIsAbsolute = sizeIsAbsolute
            
            # TODO: convert absolute to relative size or vice versa
            
            self.updateTransform()
            dispatcher.send(('set', 'sizeIsAbsolute'), self)
            self._arrangeChildren()
            self.display.Refresh()
            
            for ancestor in self.ancestors():
                if self.sizeIsAbsolute:
                    dispatcher.connect(self.maintainAbsoluteSize, ('set', 'position'), ancestor)
                    dispatcher.connect(self.maintainAbsoluteSize, ('set', 'size'), ancestor)
                    dispatcher.connect(self.maintainAbsoluteSize, ('set', 'rotation'), ancestor)
                else:
                    dispatcher.disconnect(self.maintainAbsoluteSize, ('set', 'position'), ancestor)
                    dispatcher.disconnect(self.maintainAbsoluteSize, ('set', 'size'), ancestor)
                    dispatcher.disconnect(self.maintainAbsoluteSize, ('set', 'rotation'), ancestor)
    
    
    def maintainAbsoluteSize( self, signal, sender, event=None, value=None, **arguments):
        self.updateTransform()
        self._arrangeChildren()
    
    
    def worldSize(self):
        # TODO: if a parent is rotated does this screw up?
        # TODO: will OSG do this for us?
        
        if self.parent is None or self.sizeIsAbsolute:
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
        self._rotation = rotation
        self.updateTransform()
        dispatcher.send(('set', 'rotation'), self)
        self.display.Refresh()
    
    
    def weight(self):
        return self._weight
    
    
    def setWeight(self, weight):
        self._weight = weight
        if self._path is None:
            self.updateTransform()
        else:
            self.setPath(self._path)
        dispatcher.send(('set', 'weight'), self)
        self.display.Refresh()
    
    
    def addChildVisible(self, childVisible):
        self.children.append(childVisible)
        childVisible.parent = self
        self.childGroup.addChild(childVisible.sgNode)
        dispatcher.connect(self.childArrangedWeightChanged, ('set', 'arrangedWeight'), childVisible)
        if childVisible.sizeIsAbsolute:
            for ancestor in childVisible.ancestors():
                dispatcher.connect(childVisible.maintainAbsoluteSize, ('set', 'position'), ancestor)
                dispatcher.connect(childVisible.maintainAbsoluteSize, ('set', 'size'), ancestor)
                dispatcher.connect(childVisible.maintainAbsoluteSize, ('set', 'rotation'), ancestor)
        self._stateSet.setAttributeAndModes(osg.PolygonMode(osg.PolygonMode.FRONT_AND_BACK, osg.PolygonMode.LINE), osg.StateAttribute.ON)
        if self.arrangedAxis is None:
            childVisible.updateTransform()
        else:
            self._arrangeChildren()
        dispatcher.send(('set', 'children'), self)
        self.display.Refresh()
    
    
    def removeChildVisible(self, childVisible):
        if childVisible in self.children:
            if childVisible.sizeIsAbsolute:
                for ancestor in childVisible.ancestors():
                    dispatcher.disconnect(childVisible.maintainAbsoluteSize, ('set', 'position'), ancestor)
                    dispatcher.disconnect(childVisible.maintainAbsoluteSize, ('set', 'size'), ancestor)
                    dispatcher.disconnect(childVisible.maintainAbsoluteSize, ('set', 'rotation'), ancestor)
            dispatcher.disconnect(self.childArrangedWeightChanged, ('set', 'arrangedWeight'), childVisible)
            self.childGroup.removeChild(childVisible.sgNode)
            childVisible.parent = None
            self.children.remove(childVisible)
            if len(self.children) == 0:
                pass    # TODO: opposite of self._stateSet.setAttributeAndModes(osg.PolygonMode(osg.PolygonMode.FRONT_AND_BACK, osg.PolygonMode.LINE), osg.StateAttribute.ON)
            if self.arrangedAxis is None:
                childVisible.updateTransform()
            else:
                self._arrangeChildren()
            dispatcher.send(('set', 'children'), self)
            self.display.Refresh()
    
    
    def rootVisible(self):
        if self.parent is None:
            return self
        else:
            return self.parent.rootVisible()
    
    
    def ancestors(self):
        ancestors = []
        if self.parent is not None:
            ancestors.append(self.parent)
            ancestors.extend(self.parent.ancestors())
        return ancestors
    
    
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
                if not child.sizeIsAbsolute:
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
                if not child.sizeIsAbsolute:
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
                if not child.sizeIsAbsolute:
                    child.setSize((max(xSize, 0.5), max(ySize, 0.5), childDepth))
                child.setPositionIsFixed(True)
                curZ += childDepth + self.arrangedSpacing
        
        if recurse:
            for child in self.children:
                child._arrangeChildren(recurse = True)
    
    
    def setArrangedAxis(self, axis = 'largest', recurse = False):
        """ Arrange the children of this visible along the specified axis. """
        
        if axis != self.arrangedAxis:
            self.arrangedAxis = axis
            if axis is None:
                for child in self.children:
                    child.setPositionIsFixed(False)
            else:
                self._arrangeChildren(False)
            dispatcher.send(('set', 'arrangedAxis'), self)
            self.display.Refresh()
        
        if recurse:
            for child in self.children:
                child.setArrangedAxis(axis = axis, recurse = True)
    
    
    def setArrangedSpacing(self, spacing = .02, recurse = False):
        """ Arrange the children of this visible along the specified axis. """
        
        if spacing != self.arrangedSpacing:
            self.arrangedSpacing = spacing
            self._arrangeChildren(False)
            dispatcher.send(('set', 'arrangedSpacing'), self)
            self.display.Refresh()
            self.display.Update()
        
        if recurse:
            for child in self.children:
                child.setArrangedSpacing(spacing = spacing, recurse = True)
    
    
    def setArrangedWeight(self, weight = weight):
        if weight != self.arrangedWeight:
            self.arrangedWeight = weight
            self._arrangeChildren(False)
            dispatcher.send(('set', 'arrangedWeight'), self)
            self.display.Refresh()
            self.display.Update()
    
    
    def childArrangedWeightChanged(self, signal, sender, **arguments):
        self._arrangeChildren()
    
    
#    def allChildrenAreArranged(self):
#        if len(self.children) > 0:
#            if self.arrangedAxis is None:
#                return False
#            else:
#                for child in self.children:
#                    if not child.allChildrenAreArranged():
#                        return False
#        return True
    
    
#    def graphvizRecordLabel(self):
#        labels = []
#        for child in self.children:
#            if len(child.children) == 0:
#                labels.append(child.graphvizRecordLabel())
#            else:
#                subLabel = child.graphvizRecordLabel()
#                if child.arrangedAxis == self.arrangedAxis:
#                    labels.append('{' + subLabel + '}')
#                else:
#                    labels.append('{{' + subLabel + '}}')
#        return '|'.join(labels)
    
    
    def graphvizAttributes(self):
        pos = self.worldPosition()
        size = self.worldSize()
        attributes = {'width': str(size[0] * 1000.0 / 72.0), 
                      'height': str(size[1] * 1000.0 / 72.0), 
                      'fixedsize': 'true', 
                      'pos': '%f,%f' % (pos[0] * 1000.0 / 72.0, pos[1] * 1000.0 / 72.0)}
        if self.positionIsFixed():
            attributes['pin'] = 'true'
        if False:   #len(self.children) > 0:
            attributes['shape'] = 'record'
            attributes['label'] = '{<00>|<10>|<20>|<30>|<40>|<50>|<60>|<70>|<80>}|{<01>|<11>|<21>|<31>|<41>|<51>|<61>|<71>|<81>}|{<02>|<12>|<22>|<32>|<42>|<52>|<62>|<72>|<82>}|{<03>|<13>|<23>|<33>|<43>|<53>|<63>|<73>|<83>}|{<04>|<14>|<24>|<34>|<44>|<54>|<64>|<74>|<84>}|{<05>|<15>|<25>|<35>|<45>|<55>|<65>|<75>|<85>}|{<06>|<16>|<26>|<36>|<46>|<56>|<66>|<76>|<86>}|{<07>|<17>|<27>|<37>|<47>|<57>|<67>|<77>|<87>}|{<08>|<18>|<28>|<38>|<48>|<58>|<68>|<78>|<88>}'
        else:
            attributes['shape'] = 'box'
            attributes['label'] = ''
        return attributes
    
    
    def addDependency(self, otherVisible, attribute):
        self._dependencies.add(otherVisible)
        dispatcher.connect(self.dependentVisibleChanged, ('set', attribute), otherVisible)
        ancestor = otherVisible.parent
        while ancestor is not None:
            dispatcher.connect(self.dependentVisibleChanged, ('set', attribute), ancestor)
            ancestor = ancestor.parent
    
    
    def dependentVisibleChanged( self, signal, sender, event=None, value=None, **arguments):
        if self._path is not None and len(self._dependencies) == 2:
            self.setPath(self._path)
    
    
    def positionSizeRotation(self, startPoint, endPoint):
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
    
    
    def isDraggable(self):
        return (self.positionIsFixed() == False and self.pathStart is None)
    
    
    def setTexture(self, texture):
        if texture is None:
            self._stateSet.removeTextureAttribute(0, osg.StateAttribute.TEXTURE)
        else:
            self._stateSet.setTextureAttributeAndModes(0, texture, osg.StateAttribute.ON)
        self._staticTexture = texture
        self.display.Refresh()
    
        
    def setTextureTransform(self, transform):
        if transform is None:
            self._stateSet.removeTextureAttribute(0, osg.StateAttribute.TEXMAT)
        else:
            textureMatrix = osg.TexMat()
            textureMatrix.setMatrix(transform)
            self._stateSet.setTextureAttributeAndModes(0, textureMatrix, osg.StateAttribute.ON);
        self._staticTextureTransform = transform
        self.display.Refresh()
    
    
    def setFlowDirection(self, fromVisible, toVisible, flowTo=True, flowFrom=False):
        self.pathStart = fromVisible
        self.pathEnd = toVisible
        self.flowTo = flowTo
        self.flowFrom = flowFrom
        self.updateFlowAnimation()
        self.display.Refresh()
    
    
    def updateFlowAnimation(self):
        if self._animateFlow and (self.flowTo or self.flowFrom):
            if self.flowTo:
                self._stateSet.setTextureAttributeAndModes(0, self._motionTexture1, osg.StateAttribute.ON)
                textureMatrix = osg.TexMat(osg.Matrixd.scale(10,  self.size()[1] / 400.0 * 5000.0,  10))
                textureMatrix.setDataVariance(osg.Object.DYNAMIC)
                self._stateSet.setTextureAttributeAndModes(0, textureMatrix, osg.StateAttribute.ON);
                # TODO: Python callbacks really don't perform well.  It may be better to use a TexGen, possibly tied to a cycling uniform?  Or even a shader...
                callback = AnimatedTextureCallback(self, 0, textureMatrix, osg.Matrixd.translate(-0.05, -0.05, -0.05))
                self._shapeGeode.setUpdateCallback(callback.__disown__())
            elif self.flowFrom:
                # TODO: this should be using texture unit 1 but it doesn't render correctly on Mac OS X
                self._stateSet.setTextureAttributeAndModes(0, self._motionTexture2, osg.StateAttribute.ON)
                textureMatrix = osg.TexMat(osg.Matrixd.scale(10,  self.size()[1] / 400.0 * 5000.0,  10))
                textureMatrix.setDataVariance(osg.Object.DYNAMIC)
                self._stateSet.setTextureAttributeAndModes(0, textureMatrix, osg.StateAttribute.ON);
                # TODO: Python callbacks really don't perform well.  It may be better to use a TexGen, possibly tied to a cycling uniform?  Or even a shader...
                callback = AnimatedTextureCallback(self, 0, textureMatrix, osg.Matrixd.translate(0.05, 0.05, 0.05))
                self._shapeGeode.setUpdateCallback(callback.__disown__())
        elif self._shapeGeode.getUpdateCallback() is not None:
            self._shapeGeode.setUpdateCallback(None)
            self._stateSet.removeTextureAttribute(0, osg.StateAttribute.TEXTURE)
            self._stateSet.removeTextureAttribute(0, osg.StateAttribute.TEXMAT)
            self.setTexture(self._staticTexture)
            self.setTextureTransform(self._staticTextureTransform)
    
    
    def animateFlow(self, animate=True):
        if self._animateFlow != animate:
            self._animateFlow = animate
            self.updateFlowAnimation()
        
        
    def setPath(self, path, startVisible=None, endVisible=None):
        if startVisible is not None:
            self.addDependency(startVisible, 'position')
            if startVisible != self.pathStart:
                path.reverse()
            startVisible.connectedPaths.append(self)
        if endVisible is not None:
            self.addDependency(endVisible, 'position')
            endVisible.connectedPaths.append(self)
        
        self._path = path
        
        path = list(path)
        path.insert(0, self.pathStart.worldPosition())
        path.append(self.pathEnd.worldPosition())
        
        if len(path) == 2:
            # Create a straight connection from start to end
            # TODO: Will this object ever have a parent?  If so then we'll have to translate world to local coordinates here.
            position, size, rotation = self.positionSizeRotation(path[0], path[-1])
            self.setPosition(position)
            self.setSize(size)
            self.setRotation(rotation)
        else:
            # Create a multi-segmented path from start to end.  This mostly works but looks really bad.  Probably need to wait for the Python wrapper of osgModeling <http://code.google.com/p/osgmodeling/> to make this look good.
            while self._shapeGeode.getNumDrawables() > 0:
                self._shapeGeode.removeDrawable(self._shapeGeode.getDrawable(0))
            self._position = (0, 0, 0)
            self._size = (1, 1, 1)
            self._rotation = (0, 1, 0, 0)
            self.updateTransform()
            for index in range(len(path) - 1):
                position, size, rotation = self.positionSizeRotation(path[index], path[index + 1])
                if self._shapeName == 'tube':
                    segment = osg.Cylinder(osg.Vec3(position[0], position[1], position[2]), size[0], size[1])
                    segment.setRotation(osg.Quat(-pi/2.0, osg.Vec3d(1, 0, 0)) * osg.Quat(rotation[3], osg.Vec3(rotation[0], rotation[1], rotation[2])))
                elif self._shapeName == 'cone':
                    segment = osg.Cone(osg.Vec3(position[0], position[1], position[2]), size[0], size[1])
                    segment.setRotation(osg.Quat(-pi/2.0, osg.Vec3d(1, 0, 0)) * osg.Quat(rotation[3], osg.Vec3(rotation[0], rotation[1], rotation[2])))
                else:
                    # TODO: handle other shapes
                    print "oops"
                self._shapeGeode.addDrawable(osg.ShapeDrawable(segment))
        self.display.Refresh()
    
    
    def isPath(self):
        return self.pathStart is not None
    
    
    def onMouseDown(self, event):
        pass    # TODO?
    
    
    def setGlowColor(self, color):
        if color != self._glowColor:
            if self._shapeName is not None:
                if color is None:
                    if self._glowNode is not None:
                        self.sgNode.removeChild(self._glowNode)
                        self._glowNode = None
                        self._glowNodeMaterial = None
                else:
                    if self._glowNode is None:
                        w, h, d = self.size()
                        self._glowNode = osg.MatrixTransform(osg.Matrixd.scale(osg.Vec3((w * 1.01) / w, (h * 1.01) / h, (d * 1.01) / d)))
                        clone = osg.Geode()
                        clone.setName(str(self.displayId))
                        shapeDrawable = osg.ShapeDrawable(Visible.geometries[self._shapeName])
                        clone.addDrawable(shapeDrawable)
                        self._glowNode.addChild(clone)
                        self._glowNode.getOrCreateStateSet().clear()
                        self._glowNodeMaterial = osg.Material()
                        self._glowNode.getStateSet().setAttribute(self._glowNodeMaterial)
                        self.sgNode.addChild(self._glowNode)
                    colorVec = osg.Vec4(color[0], color[1], color[2], color[3])
                    self._glowNodeMaterial.setDiffuse(osg.Material.FRONT_AND_BACK, colorVec)
                    self._glowNodeMaterial.setEmission(osg.Material.FRONT_AND_BACK, colorVec)
                    self._glowNodeMaterial.setAlpha(osg.Material.FRONT_AND_BACK, color[3])
                    if color[3] == 1:
                        self._glowNode.getStateSet().setRenderingHint(osg.StateSet.OPAQUE_BIN)
                        self._glowNode.getStateSet().setMode(osg.GL_BLEND, osg.StateAttribute.OFF)
                    else:
                        self._glowNode.getStateSet().setRenderingHint(osg.StateSet.TRANSPARENT_BIN)
                        self._glowNode.getStateSet().setMode(osg.GL_BLEND, osg.StateAttribute.ON)
                
            self._glowColor = color
            self.display.Refresh()
    
    
    def __del__(self):
        self.children = []
    
    
