from Object import Object

class GapJunction(Object):
    
    # TODO: gap junctions can be directional
    
    def __init__(self, network, neurite1, neurite2, *args, **keywords):
        Object.__init__(self, network, *args, **keywords)
        self.neurites = set([neurite1, neurite2])
