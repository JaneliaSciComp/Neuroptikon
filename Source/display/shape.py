#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

import os, sys
import wx
import osg
from ctypes import c_float, c_uint, pointer


def shapeClasses():
    shapeClasses = []
    classesToInspect = Shape.__subclasses__() # pylint_disabled: disable=E1101
    while any(classesToInspect):
        classToInspect = classesToInspect.pop(0)
        if classToInspect.shouldBeRegistered():
            shapeClasses += [classToInspect]
        classesToInspect += classToInspect.__subclasses__()
    return shapeClasses


class Shape(object):
    
    @classmethod
    def name(cls):
        raise NotImplementedError, gettext('Shape sub-classes must override the name method.')
    
    
    @classmethod
    def shouldBeRegistered(cls):
        return cls != Shape
    
    
    @classmethod
    def bitmap(cls):
        # Check for an Icon.png in the same directory as this class's module's source file, otherwise return an empty bitmap.
        iconDir = os.path.dirname(sys.modules[cls.__module__].__file__)
        try:
            image = wx.Image(iconDir + os.sep + 'Icon.png')
        except:
            image = None
        if image is not None and image.IsOk():
            image.Rescale(16, 16, wx.IMAGE_QUALITY_HIGH)
            return image.ConvertToBitmap()
        else:
            return wx.EmptyBitmap(16, 16)
    
    
    @classmethod
    def vectorArrayFromList(cls, vectorList):
        dims = len(vectorList[0])
        if dims == 2:
            vectorArray = osg.Vec2Array(len(vectorList))
        elif dims == 3:
            vectorArray = osg.Vec3Array(len(vectorList))
        elif dims == 4:
            vectorArray = osg.Vec4Array(len(vectorList))
        else:
            raise ValueError, gettext('Vector arrays can only be created with vectors of 2, 3 or 4 dimensions.')
        arrayPointer = pointer(c_float.from_address(int(vectorArray.getDataPointer()))) # pylint: disable=E1101
        vectorSize = vectorArray.getDataSize()
        offset = 0
        for vector in vectorList:
            for dim in range(dims):
                arrayPointer[offset + dim] = vector[dim]
            offset += vectorSize
        return vectorArray
    
    
    @classmethod
    def primitiveSetFromList(cls, primitiveType, vertexIndexList):
        primitiveSet = osg.DrawElementsUInt(primitiveType, len(vertexIndexList))
        arrayPointer = pointer(c_uint.from_address(int(primitiveSet.getDataPointer()))) # pylint: disable=E1101
        offset = 0
        for vertex in vertexIndexList:
            arrayPointer[offset] = vertex
            offset += 1
        return primitiveSet
    
    
    def __init__(self, *args, **keywordArgs):
        object.__init__(self, *args, **keywordArgs)
        self._geometry = osg.Geometry()
        self.setColor((0.5, 0.5, 0.5, 1.0))
    
    
    def geometry(self):
        return self._geometry
    
    
    def setColor(self, color):
        if not isinstance(color, (list, tuple)) or len(color) != 4:
            raise ValueError, 'The color argument to setColor() must be a list or tuple of four float values.'
        
        self._geometry.setColorArray(Shape.vectorArrayFromList([color]))
        self._geometry.setColorBinding(osg.Geometry.BIND_OVERALL)
        self._geometry.dirtyDisplayList()

    # TODO: the world is not ready to iterate over osg:Arrays
    # def getColor(self):
    #     return self._geometry.getColorArray()
    
    
    def persistentAttributes(self):
        return {}
    
    
    def __eq__(self, otherObject):
        return isinstance(otherObject, type(self)) and otherObject.persistentAttributes() == self.persistentAttributes() 
    
    
    def interiorBounds(self):
        """ The largest bounding box that can fit inside the shape in the form ((x_min, y_min, z_min), (x_max, y_max, z_max)) or None if the shape has no interior. """
        return None
    
    
    def intersectionPoint(self, rayOrigin, rayDirection):
        """ Returns the intersection point nearest to the ray origin or None if the ray does not intersect the shape. """
        raise NotImplementedError, gettext('Shape sub-classes must override the intersectionPoint method.')


class UnitShape(Shape):
    """ 
    Shape objects should fill a unit cube.  They will be sized, positioned and rotated by the containing Visible object.
    """
    
    @classmethod
    def name(cls):
        raise NotImplementedError, gettext('UnitShape sub-classes must override the name method.')
    
    
    @classmethod
    def shouldBeRegistered(cls):
        return cls != UnitShape
    
    
    def intersectionPoint(self, rayOrigin, rayDirection):
        """ Returns the intersection point nearest to the ray origin or None if the ray does not intersect the shape. """
        raise NotImplementedError, gettext('Unithape sub-classes must override the intersectionPoint method.')


class PathShape(Shape):
    
    @classmethod
    def name(cls):
        raise NotImplementedError, gettext('UnitShape sub-classes must override the name method.')
    
    
    @classmethod
    def shouldBeRegistered(cls):
        return cls != PathShape
    
    
    def __init__(self, pathPoints = None, *args, **keywordArgs):
        pathPoints = pathPoints or []
        Shape.__init__(self, *args, **keywordArgs)
        self.setPoints(pathPoints)
    
    
    def setPoints(self, pathPoints):
        raise NotImplementedError, gettext('PathShape sub-classes must override the setPoints method.')
    
    
    def points(self):
        raise NotImplementedError, gettext('PathShape sub-classes must override the points method.')
        
    
    def setWeight(self, weight):
        raise NotImplementedError, gettext('PathShape sub-classes must override the setWeight method.')
        
    
    def weight(self):
        raise NotImplementedError, gettext('PathShape sub-classes must override the weight method.')
    
    
    def intersectionPoint(self, rayOrigin, rayDirection):
        """ Returns the intersection point nearest to the ray origin or None if the ray does not intersect the shape. """
        raise NotImplementedError, gettext('Unithape sub-classes must override the intersectionPoint method.')
