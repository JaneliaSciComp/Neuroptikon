from Object import *
from Pathway import Pathway
import wx
from pydispatch import dispatcher
import xml.etree.ElementTree as ElementTree


class Region(Object):
    
    #TODO: sub region layout (layers, columns, etc)
    
    def __init__(self, network, parentRegion = None, ontologyTerm = None, *args, **keywords):
        """
        Regions represent a physical subset of a nervous system.  They can also be hierarchical with regions nested within other regions.  Regions can also be associated with an entry in one of the :class:`ontologies <Library.Ontology.Ontology>` in the library.
        
        You create a region by messaging a network:
        
        >>> region1 = network.createRegion(...)
        """
        
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
            parentRegion._addSubRegion(self)
    
    
    @classmethod
    def _fromXMLElement(cls, network, xmlElement):
        object = super(Region, cls)._fromXMLElement(network, xmlElement)
        object.parentRegion = None
        object.subRegions = []
        for regionElement in xmlElement.findall('Region'):
            region = Region._fromXMLElement(network, regionElement)
            if region is None:
                raise ValueError, gettext('Could not create region')
            region.parentRegion = object
            object.subRegions.append(region)
            network.addObject(region)
        ontologyElement = xmlElement.find('OntologyTerm')
        if ontologyElement is None:
            ontologyElement = xmlElement.find('ontologyTerm')
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
    
    
    def _toXMLElement(self, parentElement):
        regionElement = Object._toXMLElement(self, parentElement)
        if self.ontologyTerm is not None:
            ElementTree.SubElement(regionElement, 'OntologyTerm', ontologyId = str(self.ontologyTerm.ontology.identifier), ontologyTermId = str(self.ontologyTerm.identifier))
        for subRegion in self.subRegions:
            subRegion._toXMLElement(regionElement)
        return regionElement
    
    
    def _includeInScript(self, atTopLevel = False):
        # The root region will also add its sub-regions to the script
        return not atTopLevel or self.parentRegion is None
    
    
    def _needsScriptRef(self):
        return True
    
    
    def _creationScriptParams(self, scriptRefs):
        args, keywords = Object._creationScriptParams(self, scriptRefs)
        if self.parentRegion is not None:
            keywords['parentRegion'] = '' + scriptRefs[self.parentRegion.networkId]
        if self.ontologyTerm is not None:
            ontologyId = str(self.ontologyTerm.ontology.identifier).replace('\\', '\\\\').replace('\'', '\\\'')
            termId = str(self.ontologyTerm.identifier).replace('\\', '\\\\').replace('\'', '\\\'')
            keywords['ontologyTerm'] = 'library.ontology(\'%s\').findTerm(name = \'%s\')' % (ontologyId, termId)
        return (args, keywords)
    
    
    def _creationScriptChildren(self):
        children = Object._creationScriptChildren(self)
        children.extend(self.subRegions)
        return children
    
    
    def _addSubRegion(self, subRegion):
        self.subRegions.append(subRegion)
        subRegion.parentRegion = self
        dispatcher.send(('set', 'subRegions'), self)
    
    
    def addPathwayToRegion(self, otherRegion, sendsOutput = None, receivesInput = None, name = None):
        """ This method is deprecated, please use projectToRegion instead. """
        pathway = self.projectToRegion(otherRegion, sendsOutput == True, bidirectional = receivesInput, name = name)
        pathway.region1Projects = sendsOutput
        return pathway
    
    
    def projectToRegion(self, otherRegion, knownProjection = True, bidirectional = None, name = None):
        """ Add a pathway connecting this region to the other region. 
        
        The knownProjection parameter indicates whether this region sends information to the other region.  It should be True, False or None (unknown). 
        
        The bidirectional parameter indicates whether the other region sends information back to this region.  It should be True, False or None (unknown). 
        
        Returns the pathway object that is created. """
        
        if not isinstance(otherRegion, Region) or otherRegion.network != self.network:
            raise TypeError, 'The otherRegion argument passed to projectToRegion() must be a region from the same network.'
        if knownProjection not in (True, False, None):
            raise ValueError, 'The knownProjection argument passed to projectToRegion() must be True, False or None'
        if bidirectional not in (True, False, None):
            raise ValueError, 'The bidirectional argument passed to projectToRegion() must be True, False or None'
        
        pathway = Pathway(region1 = self, region2 = otherRegion, region1Projects = True if knownProjection else None, region2Projects = bidirectional, name = name)
        self.pathways.append(pathway)
        otherRegion.pathways.append(pathway)
        self.network.addObject(pathway)
        return pathway
    
    
    def connections(self, recurse = True):
        connections = Object.connections(self, recurse) + self.pathways + self.arborizations
        if recurse:
            for subRegion in self.subRegions:
                connections += subRegion.connections() 
        return connections
    
    
    def inputs(self, recurse = True):
        inputs = Object.inputs(self, recurse)
        for pathway in self.pathways:
            if pathway.region1 == self and pathway.region2Projects or pathway.region2 == self and pathway.region1Projects:
                inputs.append(pathway)
        for arborization in self.arborizations:
            if arborization.sendsOutput:
                inputs.append(arborization)
        if recurse:
            for subRegion in self.subRegions:
                inputs += subRegion.inputs() 
        return inputs
    
    
    def outputs(self, recurse = True):
        outputs = Object.outputs(self, recurse)
        for pathway in self.pathways:
            if pathway.region1 == self and pathway.region1Projects or pathway.region2 == self and pathway.region2Projects:
                outputs.append(pathway)
        for arborization in self.arborizations:
            if arborization.receivesInput:
                outputs.append(arborization)
        if recurse:
            for subRegion in self.subRegions:
                outputs += subRegion.outputs() 
        return outputs
    
    
    def allSubRegions(self):
        allSubRegions = list()
        for subRegion in self.subRegions:
            allSubRegions += [subRegion] + subRegion.allSubRegions()
        return allSubRegions
