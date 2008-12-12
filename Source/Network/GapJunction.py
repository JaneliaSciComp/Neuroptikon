from Object import Object

class GapJunction(Object):
    
    # TODO: gap junctions can be directional
    
    def __init__(self, network, neurite1, neurite2, name=None):
        Object.__init__(self, network, name)
        self.neurites = set([neurite1, neurite2])
