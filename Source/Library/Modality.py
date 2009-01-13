from LibraryItem import LibraryItem

class Modality(LibraryItem):
    
    @classmethod
    def listProperty(cls):
        return 'modalities'
    
    
    @classmethod
    def lookupProperty(cls):
        return 'modality'
    

# Possible additional attributes for the future:  
#     Hierarchy, i.e. - electromagnetic (light, magnetic field), chemical (odor, taste), phsyical (sound, touch), etc..
