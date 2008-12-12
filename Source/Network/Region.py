from Object import *
from Pathway import Pathway


class Region(Object):
    #TODO: sub region layout (layers, columns, etc)
    #TODO: atlasIsosurface
    
    def __init__(self, network, name=None):
        Object.__init__(self, network, name)
        self.subRegions = []
        self.arborizations = []
        self.pathways = []
    
    def addSubRegion(self, subRegion):
        self.subRegions.append(subRegion)
    
    def addPathwayToRegion(self, otherRegion, name=None):
        pathway = Pathway(self, otherRegion, name)
        self.pathways.append(pathway)
        otherRegion.pathways.append(pathway)
        self.network.addObject(pathway)
        return pathway
    
    def inputs(self):
        inputs = Object.inputs(self)
        for pathway in self.pathways:
            inputs.append(pathway)
        for arborization in self.arborizations:
            if arborization.sendsOutput:
                inputs.append(arborization)
        # TODO: sub-regions
        return inputs
    
    def outputs(self):
        outputs = Object.outputs(self)
        for pathway in self.pathways:
            outputs.append(pathway)
        for arborization in self.arborizations:
            if arborization.receivesInput:
                outputs.append(arborization)
        # TODO: sub-regions
        return outputs
    
