from LibraryItem import LibraryItem

class Neurotransmitter(LibraryItem):
    
    @classmethod
    def listProperty(cls):
        return 'neurotransmitters'
    
    
    @classmethod
    def lookupProperty(cls):
        return 'neurotransmitter'


# Possible additional attributes for the future:  
#     enzyme
#     activity (specific, probably specific, specificity uncertain, etc.)
