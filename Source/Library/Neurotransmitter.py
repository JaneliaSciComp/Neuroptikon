import wx
from LibraryItem import LibraryItem
from Network.Synapse import Synapse

class Neurotransmitter(LibraryItem):
    
    @classmethod
    def listProperty(cls):
        return 'neurotransmitters'
    
    
    @classmethod
    def lookupProperty(cls):
        return 'neurotransmitter'
    
    
    @classmethod
    def bitmap(cls):
        image = Synapse.image()
        if image == None:
            return None
        else:
            return wx.BitmapFromImage(image)


# Possible additional attributes for the future:  
#     enzyme
#     activity (specific, probably specific, specificity uncertain, etc.)
