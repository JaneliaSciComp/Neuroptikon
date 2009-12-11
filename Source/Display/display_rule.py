from visible import *

class DisplayRule:
    def __init__(self, display):
        self.display = display
        self.active = True
        self.predicate = None
        self._matchingObjects = []
        self.actions = []
    
    
    
