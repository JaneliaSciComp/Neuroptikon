import osg, osgFX, osgText

from Network.Region import Region
from Network.Neuron import Neuron
from Network.Arborization import Arborization
from Network.Synapse import Synapse
from Network.Stimulus import Stimulus
from Network.Innervation import Innervation
from AnimatedTextureCallback import AnimatedTextureCallback

from pydispatch import dispatcher
from math import atan2, pi, sqrt
import random


class Visible(object):
    """Instances of this class map a network object (neurion, region, etc.) or a group of objects to a specific display.  They capture all of the attributes needed to render the object(s)."""
    
    # Objects in unit space
    geometries = {"ball": osg.Sphere(osg.Vec3(0, 0, 0), 0.5), 
                  "box": osg.Box(osg.Vec3(0, 0, 0), 1), 
                  "cone": osg.Cone(osg.Vec3(0, -0.25, 0), 0.5, 1), # have to offset center <http://www.mail-archive.com/osg-users@lists.openscenegraph.org/msg07081.html>
                  "stick": osg.Cylinder(osg.Vec3(0, 0, 0), 0.5, 1), 
                  "tube": osg.Cylinder(osg.Vec3(0, 0, 0), 0.5, 1)}
    geometries["cone"].setRotation( osg.Quat(-pi/2, osg.Vec3d(1, 0, 0)))
    geometries["stick"].setRotation( osg.Quat(-pi/2, osg.Vec3d(1, 0, 0)))
    geometries["tube"].setRotation( osg.Quat(-pi/2, osg.Vec3d(1, 0, 0)))
        
        
#        drawables = {"ball": osg.ShapeDrawable(ball), 
#                     "box": osg.ShapeDrawable(box), 
#                     "cone": osg.ShapeDrawable(cone), 
#                     "stick": osg.ShapeDrawable(stick), 
#                     "tube": osg.ShapeDrawable(stick)}
    # TODO: osgText::Font* font = osgText::readFontFile("fonts/arial.ttf");
    
    
    def __init__(self, display, client):
        self.display = display
        self.client = client
        self._motionTexture1 = display.textureFromImage('texture2.png')
        self._motionTexture2 = display.textureFromImage('texture2.png')
        self._selectable = True
        self._glowColor = None
        self._glowNode = None
        self._position = (random.randint(0, 1000), random.randint(0, 1000), 0) #(0, 0, 0)
        self._positionIsFixed = False
        self._size = (1, 1, 1)
        self._rotation = (0, 0, 1, 0)
        self._scaleOrientation = (0, 0, 1, 0)
        self._weight = 1
        self._dependencies = set()
        self._visible = True
        self._label = None
        self._labelNode = None
        self._shapeName = "none"
        self._color = ((1, 1, 1), (1, 1, 1)) # diffuse, emissive
        self._opacity = 1
        self._path = None
        self.pathStart = None
        self.pathEnd = None
        self.sgNode = osg.MatrixTransform()    #osg.PositionAttitudeTransform()
        self._shapeGeode = osg.Geode()
        self._shapeGeode.setName(str(id(self.client)))
        self._shapeDrawable = None
        self._stateSet = self._shapeGeode.getOrCreateStateSet()
        self._stateSet.setAttributeAndModes(osg.BlendFunc(), osg.StateAttribute.ON)
        self._material = osg.Material()
        self._material.setDiffuse(osg.Material.FRONT_AND_BACK, osg.Vec4(1, 1, 1, 1))
        self._material.setEmission(osg.Material.FRONT_AND_BACK, osg.Vec4(0, 0, 0, 1))
        self._material.setAmbient(osg.Material.FRONT_AND_BACK, osg.Vec4(1, 1, 1, 1))
        self._material.setSpecular(osg.Material.FRONT_AND_BACK, osg.Vec4(1, 1, 1, 1))
        self._material.setShininess(osg.Material.FRONT_AND_BACK, 1)
        self._stateSet.setAttribute(self._material)
        self.sgNode.addChild(self._shapeGeode)
        self._textGeode = osg.Geode()
        self._textGeode.setName(str(id(self.client)))
        self._textDrawable = None
        self.sgNode.addChild(self._textGeode)
        self._staticTexture = None
        self._staticTextureTransform = None
    
    
    def shape(self):
        """Return the type of shape set for this visualized object, one of 'ball', 'box' or 'stick'"""
        return self._shapeName
    
    
    def setShape(self, shapeName):
        self._shapeName = shapeName
        if self._shapeDrawable:
            self._geode.removeDrawable(self._shapeDrawable)
        self._shapeDrawable = osg.ShapeDrawable(Visible.geometries[self._shapeName])
        self._shapeGeode.addDrawable(self._shapeDrawable)
       # TODO: recreate the glow shape if needed
    
    
    def setLabel(self, label):
        if label is not None:
            if self._textDrawable is None:
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
            self._textDrawable.setText(label)
        elif label is None and self._textDrawable is not None:
            self._textGeode.removeDrawable(self._textDrawable)
            self._textDrawable = None
        self._label = label
    
    
    def label(self):
        return self._label
    
    
    def setColor(self, diffuseColor, emissiveColor=None):
        self._material.setDiffuse(osg.Material.FRONT_AND_BACK, osg.Vec4 (diffuseColor[0], diffuseColor[1], diffuseColor[2], 1))
        if emissiveColor is not None:
            self._material.setEmission(osg.Material.FRONT_AND_BACK, osg.Vec4 (emissiveColor[0], emissiveColor[1], emissiveColor[2], 1))
        self._color = (diffuseColor, emissiveColor)
    
    
    def color(self):
        return self._color
    
    
    def setOpacity(self, opacity):
        if opacity < 0:
            opacity = 0
        elif opacity > 1:
            opacity = 1
        self._material.setAlpha(osg.Material.FRONT_AND_BACK, opacity)
        if opacity == 1:
            self._shapeDrawable.getOrCreateStateSet().setRenderingHint(osg.StateSet.OPAQUE_BIN)
            self._shapeDrawable.getStateSet().setMode(osg.GL_BLEND, osg.StateAttribute.OFF)
        else:
            self._shapeDrawable.getOrCreateStateSet().setRenderingHint(osg.StateSet.TRANSPARENT_BIN)
            self._shapeDrawable.getStateSet().setMode(osg.GL_BLEND, osg.StateAttribute.ON)
        
        if self._textDrawable is not None:
            self._textDrawable.setColor(osg.Vec4(0, 0, 0, opacity))
        
        self._opacity = opacity
    
    
    def opacity(self):
        return self._opacity
    
    
    def updateTransform(self):
#        self.sgNode.setPosition(osg.Vec3d(self.position()[0], self.position()[1], self.position()[2]))
#        self.sgNode.setScale(osg.Vec3d(self.size()[0], self.size()[1], self.size()[2]))
#        self.sgNode.setAttitude(osg.Quat(self.rotation()[3], osg.Vec3d(self.rotation()[0], self.rotation()[1], self.rotation()[2])))
        # update the transform unless we're under an osgGA.Selection node, i.e. being dragged
        if len(self.sgNode.getParents()) == 0 or self.display.selection is None or self.sgNode.getParent(0).__repr__() != self.display.selection.asGroup().__repr__():
            self.sgNode.setMatrix(osg.Matrixd.scale(osg.Vec3d(self.size()[0], self.size()[1], self.size()[2])) * 
                                   osg.Matrixd.rotate(self.rotation()[3], osg.Vec3d(self.rotation()[0], self.rotation()[1], self.rotation()[2])) *
                                   osg.Matrixd.translate(osg.Vec3d(self.position()[0], self.position()[1], self.position()[2])))
    
    
    def position(self):
        return self._position
    
    
    def setPosition(self, position):
        if position != self._position:
            self._position = position
            self.updateTransform()
            dispatcher.send(('set', 'position'), self)
    
    
    def offsetPosition(self, offset):
        if offset != (0, 0, 0):
            self._position = (self._position[0] + offset[0], self._position[1] + offset[1], self._position[2] + offset[2])
            self._positionFixed = True
            self.updateTransform()
    
    
    def positionIsFixed(self):
        return self._positionIsFixed
    
    
    def setPositionIsFixed(self, flag):
        if self._positionIsFixed != flag:
            self._positionIsFixed = flag
            dispatcher.send(('set', 'position is fixed'), self)
    
    
    def size(self):
        return self._size
    
    
    def setSize(self, size):
        self._size = size
        self.updateTransform()
        dispatcher.send(('set', 'size'), self)
    
    
    def rotation(self):
        return self._rotation
    
    
    def setRotation(self, rotation):
        self._rotation = rotation
        self.updateTransform()
        dispatcher.send(('set', 'rotation'), self)
    
    
    def scaleOrientation(self):
        return self._scaleOrientation
    
    
    def setScaleOrientation(self, scaleOrientation):
        self._scaleOrientation = scaleOrientation
        self.updateTransform()
        dispatcher.send(('set', 'scaleOrientation'), self)
    
    
    def weight(self):
        return self._weight
    
    
    def setWeight(self, weight):
        self._weight = weight
        if self._path is None:
            self.updateTransform()
        else:
            self.setPath(self._path)
    
    
    def addDependency(self, otherVisible, attribute):
        self._dependencies.add(otherVisible)
        dispatcher.connect(self.dependentVisibleChanged, ('set', attribute), otherVisible)
    
    
    def dependentVisibleChanged( self, signal, sender, event=None, value=None, **arguments):
        if self._path is not None and len(self._dependencies) == 2:
            self.setPath(self._path)
    
    
    def positionSizeRotation(self, startPoint, endPoint):
        position = ((startPoint[0] + endPoint[0]) / 2, 
                    (startPoint[1] + endPoint[1]) / 2, 
                    (startPoint[2] + endPoint[2]) / 2)
        dx = endPoint[0] - startPoint[0]
        dy = endPoint[1] - startPoint[1]
        dz = endPoint[2] - startPoint[2]
        dsize = (self._weight * 10.0, sqrt(dx * dx + dy * dy + dz * dz), self._weight * 10.0)
        dxz = sqrt(dx**2 + dz**2)
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
    
        
    def setTextureTransform(self, transform):
        if transform is None:
            self._stateSet.removeTextureAttribute(0, osg.StateAttribute.TEXMAT)
        else:
            textureMatrix = osg.TexMat()
            textureMatrix.setMatrix(transform)
            self._stateSet.setTextureAttributeAndModes(0, textureMatrix, osg.StateAttribute.ON);
        self._staticTextureTransform = transform
    
    
    def setFlowDirection(self, fromVisible, toVisible, flowTo=True, flowFrom=False):
        self.pathStart = fromVisible
        self.pathEnd = toVisible
        self.flowTo = flowTo
        self.flowFrom = flowFrom
    
    
    def animateFlow(self, animate=True):
        if animate and self._shapeGeode.getUpdateCallback() is None:
            if self.flowTo:
                self._stateSet.setTextureAttributeAndModes(0, self._motionTexture1, osg.StateAttribute.ON)
                textureMatrix = osg.TexMat(osg.Matrixd.scale(10,  self.size()[1] / 400,  10))
                textureMatrix.setDataVariance(osg.Object.DYNAMIC)
                self._stateSet.setTextureAttributeAndModes(0, textureMatrix, osg.StateAttribute.ON);
                # TODO: Python callbacks really don't perform well.  It may be better to use a TexGen, possibly tied to a cycling uniform?  Or even a shader...
                callback = AnimatedTextureCallback(self, 0, textureMatrix, osg.Matrixd.translate(-0.05, -0.05, -0.05))
                self._shapeGeode.setUpdateCallback(callback.__disown__())
            if self.flowFrom:
                # TODO: this should be using texture unit 1 but it doesn't render correctly on Mac OS X
                self._stateSet.setTextureAttributeAndModes(0, self._motionTexture2, osg.StateAttribute.ON)
                textureMatrix = osg.TexMat(osg.Matrixd.scale(10,  self.size()[1] / 400,  10))
                textureMatrix.setDataVariance(osg.Object.DYNAMIC)
                self._stateSet.setTextureAttributeAndModes(0, textureMatrix, osg.StateAttribute.ON);
                # TODO: Python callbacks really don't perform well.  It may be better to use a TexGen, possibly tied to a cycling uniform?  Or even a shader...
                callback = AnimatedTextureCallback(self, 0, textureMatrix, osg.Matrixd.translate(0.05, 0.05, 0.05))
                self._shapeGeode.setUpdateCallback(callback.__disown__())
        elif not animate and self._shapeGeode.getUpdateCallback() is not None:
            self._shapeGeode.setUpdateCallback(None)
            self._stateSet.removeTextureAttribute(0, osg.StateAttribute.TEXTURE)
            self._stateSet.removeTextureAttribute(0, osg.StateAttribute.TEXMAT)
            self.setTexture(self._staticTexture)
            self.setTextureTransform(self._staticTextureTransform)
        
        
    def setPath(self, path, startVisible=None, endVisible=None):
        if startVisible is not None:
            self.addDependency(startVisible, 'position')
            if startVisible != self.pathStart:
                path.reverse()
        if endVisible is not None:
            self.addDependency(endVisible, 'position')
        
        path[0] = self.pathStart.position()
        path[-1] = self.pathEnd.position()
        
        self._path = path
        if True:    #len(path) == 2:
            # Create a straight connection from start to end
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
                if self._shapeName in ["tube", "stick"]:
                    segment = osg.Cylinder(osg.Vec3(position[0], position[1], position[2]), size[0], size[1])
                    segment.setRotation(osg.Quat(-pi/2, osg.Vec3d(1, 0, 0)) * osg.Quat(rotation[3], osg.Vec3(rotation[0], rotation[1], rotation[2])))
                elif self._shapeName == "cone":
                    segment = osg.Cone(osg.Vec3(position[0], position[1], position[2]), size[0], size[1])
                    segment.setRotation(osg.Quat(-pi/2, osg.Vec3d(1, 0, 0)) * osg.Quat(rotation[3], osg.Vec3(rotation[0], rotation[1], rotation[2])))
                else:
                    # TODO: handle other shapes
                    print "oops"
                self._shapeGeode.addDrawable(osg.ShapeDrawable(segment))
    
    
    def onMouseDown(self, event):
        pass    # TODO?
    
    
    def setGlowColor(self, color):
        if color != self._glowColor:
            if color is None:
                if self._glowNode is not None:
                    self.sgNode.removeChild(self._glowNode)
                    self._glowNode = None
                    self._glowNodeMaterial = None
            else:
                if self._glowNode is None:
                    w, h, d = self.size()
                    self._glowNode = osg.MatrixTransform(osg.Matrixd.scale(osg.Vec3((w + 14.0) / w, (h + 14.0) / h, (d + 14.0) / d)))
                    clone = osg.Geode()
                    clone.setName(str(id(self.client)))
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
    
