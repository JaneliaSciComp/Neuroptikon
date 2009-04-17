import wx
import osg, osgDB
import os, sys
from LibraryItem import LibraryItem

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
            image = wx.GetApp().loadImage("Texture.png")
            if image is not None and image.IsOk():
                bitmap = wx.BitmapFromImage(image)
        except:
            pass
        return bitmap
    
    
    def loadImage(self, imagePath):
        try:
            image = osgDB.readImageFile(str(imagePath))
        except:
            image = None
        if image is not None and image.valid():
            self._texture = osg.Texture2D()
            self._texture.setFilter(osg.Texture2D.MIN_FILTER, osg.Texture2D.LINEAR);
            self._texture.setFilter(osg.Texture2D.MAG_FILTER, osg.Texture2D.LINEAR);
            self._texture.setImage(image)
            self._texture.setWrap(osg.Texture2D.WRAP_S,  osg.Texture2D.REPEAT)
            self._texture.setWrap(osg.Texture2D.WRAP_T,  osg.Texture2D.REPEAT)
            self._texture.setWrap(osg.Texture2D.WRAP_R,  osg.Texture2D.REPEAT)
        else:
            self._texture = None
        
        return self._texture is not None
    
    def textureData(self):
        return self._texture
