from Object import *
from Pathway import Pathway
import wx
from wx.py import dispatcher
import xml.etree.ElementTree as ElementTree


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
        self.neurons = []
        if parentRegion is not None:
            parentRegion.addSubRegion(self)
    
    
    @classmethod
    def fromXMLElement(cls, network, xmlElement):
        object = super(Region, cls).fromXMLElement(network, xmlElement)
        object.parentRegion = None
        object.subRegions = []
        for regionElement in xmlElement.findall('Region'):
            region = Region.fromXMLElement(network, regionElement)
            if region is None:
                raise ValueError, gettext('Could not create region')
            region.parentRegion = object
            object.subRegions.append(region)
            network.addObject(region)
        ontologyElement = xmlElement.find('OntologyTerm')
        if ontologyElement is None:
            object.ontologyTerm = None
        else:
            ontology = wx.GetApp().library.ontology(ontologyElement.get('ontologyId'))
            if ontology is None:
                raise ValueError, gettext('Could not find ontology "%s"') % (ontologyElement.get('ontologyId'))
            else:
                termId = ontologyElement.get('ontologyTermId')
                if termId in ontology:
                    object.ontologyTerm = ontology[termId]
                else:
                    raise ValueError, gettext('Could not find ontology term "%s"') % (termId)
        object.arborizations = []
        object.pathways = []
        object.neurons = []
        return object
    
    
    def toXMLElement(self, parentElement):
        regionElement = Object.toXMLElement(self, parentElement)
        if self.ontologyTerm is not None:
            ElementTree.SubElement(regionElement, 'ontologyTerm', ontologyId = str(self.ontologyTerm.ontology.identifier), ontologyTermId = str(self.ontologyTerm.identifier))
        for subRegion in self.subRegions:
            subRegion.toXMLElement(regionElement)
        return regionElement
    
    
    def addSubRegion(self, subRegion):
        self.subRegions.append(subRegion)
        subRegion.parentRegion = self
        dispatcher.send(('set', 'subRegions'), self)
    
    
    def addPathwayToRegion(self, otherRegion, sendsOutput = None, receivesInput = None, name = None):
        pathway = Pathway(self, otherRegion, name = name, sendsOutput = sendsOutput, receivesInput = receivesInput)
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
    
