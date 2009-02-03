class LibraryItem(object):
    
    @classmethod
    def listProperty(cls):
        """ A methd of this name will be added to the library which will return the list of known instances of this class of item """
        return 'libraryItems'
    
    
    @classmethod
    def lookupProperty(cls):
        """ A methd of this name will be added to the library which will look up (by identifier) a known instance of this class of item """
        return 'libraryItem'
    
    
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
