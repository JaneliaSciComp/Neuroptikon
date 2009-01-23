from Object import *
from Pathway import Pathway
from pydispatch import dispatcher


class Region(Object):
    #TODO: sub region layout (layers, columns, etc)
    #TODO: atlasIsosurface
    
    def __init__(self, network, parentRegion = None, ontologyTerm = None, *args, **keywords):
        if ontologyTerm is not None:
            if 'name' not in keywords:
                keywords['name'] = ontologyTerm.name
            if 'abbreviation' not in keywords and ontologyTerm.abbreviation is not None:
                keywords['abbreviation'] = ontologyTerm.abbreviation
        
        Object.__init__(self, network, *args, **keywords)
        
        self.parentRegion = None
        self.subRegions = []
        self.ontologyTerm = ontologyTerm
        self.arborizations = []
        self.pathways = []
        if parentRegion is not None:
            parentRegion.addSubRegion(self)
    
    
    def addSubRegion(self, subRegion):
        self.subRegions.append(subRegion)
        subRegion.parentRegion = self
        dispatcher.send(('set', 'subRegions'), self)
    
    
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
    
