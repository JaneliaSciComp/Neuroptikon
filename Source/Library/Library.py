from LibraryItem import LibraryItem

class Library(object):
    
    def __init__(self):
        self._library = {}
    
    
    def add(self, item):
        if not issubclass(item.__class__, LibraryItem):
            raise ValueError, 'Library items must be instances of a subclass of LibraryItem'
        
        classKey = "_" + item.__class__.__name__.lower() + "Dict"
        if self._library.has_key(classKey):
            # This class of item has been added before.
            dict = self._library[classKey]
        else:
            # Create and retain a new dictionary for this class of item.
            dict = {}
            self._library[classKey] = dict
            # Add a method to ourself that returns the full list of items of this class.
            setattr(self, item.__class__.listProperty(), lambda: sorted(dict.values(), cmp=lambda x,y: cmp(x.name.lower(), y.name.lower())))
            # Add a method to ourself that performs a lookup of items of this class.
            setattr(self, item.__class__.lookupProperty(), lambda itemId: dict[itemId] if dict.has_key(itemId) else None)
        
        dict[item.identifier] = item
    
