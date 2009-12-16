#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

from visible import *

class DisplayRule:
    def __init__(self, display):
        self.display = display
        self.active = True
        self.predicate = None
        self._matchingObjects = []
        self.actions = []
    
    
    
