#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

import neuroptikon
import wx
import osg, osgDB
from library_item import LibraryItem

class Texture(LibraryItem):
    
    @classmethod
    def listProperty(cls):
        return 'textures'
    
    
    @classmethod
    def lookupProperty(cls):
        return 'texture'
    
    
    @classmethod
    def bitmap(cls):
        bitmap = None
        try:
            image = neuroptikon.loadImage("Texture.png")
            if image is not None and image.IsOk():
                bitmap = wx.BitmapFromImage(image)
        except:
            pass
        return bitmap
    
    
    def __init__(self, *args, **keywordArgs):
        LibraryItem.__init__(self, *args, **keywordArgs)
        
        self._texture = None
    
    
    def loadImage(self, imagePath):
        """
        Load the texture data from the image file at the specified path.
        
        Returns True if the texture was loaded successfully.
        """
        
        try:
            image = osgDB.readImageFile(str(imagePath))
        except:
            image = None
        return self.setImage(image)
    
    
    def setImage(self, image):
        """
        Set the texture data from an image in memory.
        
        The image parameter must be an osg.Image instance.
        
        Returns True if the texture was set successfully.
        """
        
        if isinstance(image, osg.Image) and image.valid():
            self._texture = osg.Texture2D()
            self._texture.setFilter(osg.Texture.MIN_FILTER, osg.Texture.LINEAR)
            self._texture.setFilter(osg.Texture.MAG_FILTER, osg.Texture.LINEAR)
            self._texture.setImage(image)
            self._texture.setWrap(osg.Texture.WRAP_S, osg.Texture.REPEAT)
            self._texture.setWrap(osg.Texture.WRAP_T, osg.Texture.REPEAT)
            self._texture.setWrap(osg.Texture.WRAP_R, osg.Texture.REPEAT)
        else:
            self._texture = None
        
        return self._texture is not None
    
    
    def loadImageCube(self, imagePaths):
        """
        Load the texture data from the six image files at the specified paths.
        
        The imagePaths parameter should be a list of six paths to image files.  The order of images is: +X, -X, +Y, -Y, +Z, -Z.
        
        Returns True if the texture was loaded successfully.
        """
        
        images = []
        for imagePath in imagePaths:
            try:
                images += [osgDB.readImageFile(str(imagePath))]
            except:
                pass
        return self.setImageCube(images)
    
    
    def setImageCube(self, images):
        """
        Set the texture data from six images.
        
        The images parameter should be a list of six osg.Image instances.  The order of images is: +X, -X, +Y, -Y, +Z, -Z.
        
        Returns True if the texture was set successfully.
        """
        
        if isinstance(images, (list, tuple)) and len(images) == 6:
            faces = [osg.TextureCubeMap.POSITIVE_X, osg.TextureCubeMap.NEGATIVE_X, osg.TextureCubeMap.POSITIVE_Y, osg.TextureCubeMap.NEGATIVE_Y, osg.TextureCubeMap.POSITIVE_Z, osg.TextureCubeMap.NEGATIVE_Z]
            self._texture = osg.TextureCubeMap()
            for image, face in map(None, images, faces):
                if not isinstance(image, osg.Image) or not image.valid():
                    self._texture = None
                    break
                else:
                    image.flipVertical()
                    self._texture.setImage(face, image)
        else:
            self._texture = None
        
        if self._texture:
            self._texture.setFilter(osg.Texture.MIN_FILTER, osg.Texture.LINEAR)
            self._texture.setFilter(osg.Texture.MAG_FILTER, osg.Texture.LINEAR)
            self._texture.setWrap(osg.Texture.WRAP_S, osg.Texture.REPEAT)
            self._texture.setWrap(osg.Texture.WRAP_T, osg.Texture.REPEAT)
            self._texture.setWrap(osg.Texture.WRAP_R, osg.Texture.REPEAT)
        
        return self._texture is not None
    
    
    def isCube(self):
        return isinstance(self._texture, osg.TextureCubeMap)
    
    def textureData(self):
        return self._texture
