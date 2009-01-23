from Object import *


class Synapse(Object):
    
    def __init__(self, network, presynapticNeurite = None, postsynapticNeurites = [], *args, **keywords):
        Object.__init__(self, network, *args, **keywords)
        self.presynapticNeurite = presynapticNeurite
        self.postsynapticNeurites = postsynapticNeurites
        self.excitatory = True
