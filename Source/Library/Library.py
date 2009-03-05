from LibraryItem import LibraryItem
from LibraryFrame import LibraryFrame
from wx.py import dispatcher

class Library(object):
    
    def __init__(self):
        self._library = {}
        self._frame = LibraryFrame()
    
    
    def add(self, item):
        if not issubclass(item.__class__, LibraryItem):
            raise ValueError, gettext('Library items must be instances of a subclass of LibraryItem')
        
        if item.__class__.__name__ in self._library:
            # This class of item has been added before.
            dict = self._library[item.__class__.__name__]
        else:
            # Create and retain a new dictionary for this class of item.
            dict = {}
            self._library[item.__class__.__name__] = dict
            # Add a method to ourself that returns the full list of items of this class.
            setattr(self, item.__class__.listProperty(), lambda: sorted(dict.values(), cmp=lambda x,y: cmp(x.name.lower(), y.name.lower())))
            # Add a method to ourself that performs a lookup of items of this class.
            setattr(self, item.__class__.lookupProperty(), lambda itemId: dict[itemId] if itemId in dict else None)
            self._frame.addItemClass(item.__class__)
        
        dict[item.identifier] = item
        
        dispatcher.send(('addition', item.__class__), self)
    
    
    def browse(self):
        self._frame.Show()
        self._frame.Raise()
    
