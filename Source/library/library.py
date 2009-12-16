#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

from library_item import LibraryItem
from library_frame import LibraryFrame
from pydispatch import dispatcher
from itertools import groupby

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
            setattr(self, item.__class__.listProperty(), lambda: sorted([value for value, group in groupby(dict.values())], cmp=lambda x,y: cmp(x.name.lower(), y.name.lower())))
            # Add a method to ourself that performs a lookup of items of this class.
            setattr(self, item.__class__.lookupProperty(), lambda itemId: dict.get(itemId, None))
            self._frame.addItemClass(item.__class__)
        
        dict[item.identifier] = item
        for synonym in item.synonyms:
            dict[synonym] = item
        
        dispatcher.send(('addition', item.__class__), self)
    
    
    def browse(self):
        self._frame.Show()
        self._frame.Raise()
    
