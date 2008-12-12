from Object import *


class Synapse(Object):
    
    def __init__(self, network, presynapticNeurite=None, postsynapticNeurites=[], name=None):
        Object.__init__(self, network, name)
        self.presynapticNeurite = presynapticNeurite
        self.postsynapticNeurites = postsynapticNeurites
        self.excitatory = True
