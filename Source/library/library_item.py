import wx

class LibraryItem(object):
    
    @classmethod
    def displayName(cls):
        """ This name will be used whenever the type of this item must be displayed. """
        return cls.__name__
    
    
    @classmethod
    def listProperty(cls):
        """ A method of this name will be added to the library which will return the list of known instances of this class of item """
        return 'libraryItems'
    
    
    @classmethod
    def lookupProperty(cls):
        """ A method of this name will be added to the library which will look up (by identifier) a known instance of this class of item """
        return 'libraryItem'
    
    
    @classmethod
    def bitmap(cls):
        return None
    
    
    @classmethod
    def frameClass(cls):
        return None
    
    
    def __init__(self, identifier = None, name = None, abbreviation = None, *args, **keywordsArgs):
        object.__init__(self, *args, **keywordsArgs)
        
        if identifier is None:
            raise ValueError, gettext('Library items must have an identifier.')
        
        self.identifier = identifier
        self.name = name
        if abbreviation is None:
            self.abbreviation = name
        else:
            self.abbreviation = abbreviation
        
        self.frame = None
    
    
    def browse(self):
        if self.__class__.frameClass() is None:
            wx.Bell()
        else:
            if self.frame is None:
                self.frame = self.__class__.frameClass()(self)
            self.frame.Show()
            self.frame.Raise()
