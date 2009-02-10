import wx
from LibraryItem import LibraryItem
from Network.Stimulus import Stimulus

class Modality(LibraryItem):
    
    @classmethod
    def listProperty(cls):
        return 'modalities'
    
    
    @classmethod
    def lookupProperty(cls):
        return 'modality'
    
    
    @classmethod
    def bitmap(cls):
        image = Stimulus.image()
        if image is None or not image.IsOk():
            return None
        else:
            return wx.BitmapFromImage(image)
    
    

# Possible additional attributes for the future:  
#     Hierarchy, i.e. - electromagnetic (light, magnetic field), chemical (odor, taste), phsyical (sound, touch), etc..
