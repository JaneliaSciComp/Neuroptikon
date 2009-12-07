import Neuroptikon
from neuro_object import NeuroObject
from Pathway import Pathway
import xml.etree.ElementTree as ElementTree
from pydispatch import dispatcher


class Region(NeuroObject):
    
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
        
        NeuroObject.__init__(self, network, *args, **keywords)
        
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
        region = super(Region, cls)._fromXMLElement(network, xmlElement)
        region.parentRegion = None
        region.subRegions = []
        for subRegionElement in xmlElement.findall('Region'):
            subRegion = Region._fromXMLElement(network, subRegionElement)
            if subRegion is None:
                raise ValueError, gettext('Could not create region')
            subRegion.parentRegion = region
            region.subRegions.append(subRegion)
            network.addObject(subRegion)
        ontologyElement = xmlElement.find('OntologyTerm')
        if ontologyElement is None:
            ontologyElement = xmlElement.find('ontologyTerm')
        if ontologyElement is None:
            region.ontologyTerm = None
        else:
            ontology = Neuroptikon.library.ontology(ontologyElement.get('ontologyId'))
            if ontology is None:
                raise ValueError, gettext('Could not find ontology "%s"') % (ontologyElement.get('ontologyId'))
            else:
                termId = ontologyElement.get('ontologyTermId')
                if termId in ontology:
                    region.ontologyTerm = ontology[termId]
                else:
                    raise ValueError, gettext('Could not find ontology term "%s"') % (termId)
        region.arborizations = []
        region.pathways = []
        region.neurons = []
        return region
    
    
    def _toXMLElement(self, parentElement):
        regionElement = NeuroObject._toXMLElement(self, parentElement)
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
        args, keywords = NeuroObject._creationScriptParams(self, scriptRefs)
        if self.parentRegion is not None:
            keywords['parentRegion'] = '' + scriptRefs[self.parentRegion.networkId]
        if self.ontologyTerm is not None:
            ontologyId = str(self.ontologyTerm.ontology.identifier).replace('\\', '\\\\').replace('\'', '\\\'')
            termId = str(self.ontologyTerm.identifier).replace('\\', '\\\\').replace('\'', '\\\'')
            keywords['ontologyTerm'] = 'library.ontology(\'%s\').findTerm(name = \'%s\')' % (ontologyId, termId)
        return (args, keywords)
    
    
    def _creationScriptChildren(self):
        return NeuroObject._creationScriptChildren(self) + self.subRegions
    
    
    def _addSubRegion(self, subRegion):
        self.subRegions.append(subRegion)
        subRegion.parentRegion = self
        dispatcher.send(('set', 'subRegions'), self)
    
    
    def addPathwayToRegion(self, otherRegion, sendsOutput = None, receivesInput = None, name = None):
        """ This method is deprecated, please use projectToRegion instead. """
        pathway = self.projectToRegion(otherRegion, sendsOutput == True, bidirectional = receivesInput, name = name)
        pathway.region1Projects = sendsOutput
        return pathway
    
    
    def projectToRegion(self, otherRegion, knownProjection = True, bidirectional = None, activation = None, backActivation = None, name = None):
        """ Add a pathway connecting this region to the other region. 
        
        The knownProjection parameter indicates whether this region sends information to the other region.  It should be True, False or None (unknown). 
        
        The bidirectional parameter indicates whether the other region sends information back to this region.  It should be True, False or None (unknown). 
        
        The activation and backActivation parameters indicate how the pathway activates the other and this region, respectively.  It should be 'excitatory', 'inhibitory' or None (unknown).
        
        Returns the pathway object that is created.
        """
        
        if not isinstance(otherRegion, Region) or otherRegion.network != self.network:
            raise TypeError, 'The otherRegion argument passed to projectToRegion() must be a region from the same network.'
        if knownProjection not in (True, False, None):
            raise ValueError, 'The knownProjection argument passed to projectToRegion() must be True, False or None'
        if bidirectional not in (True, False, None):
            raise ValueError, 'The bidirectional argument passed to projectToRegion() must be True, False or None'
        if activation not in ('excitatory', 'inhibitory', None):
            raise ValueError, 'The activation argument passed to projectToRegion() must be \'excitatory\', \'inhibitory\' or None'
        if backActivation not in ('excitatory', 'inhibitory', None):
            raise ValueError, 'The backActivation argument passed to projectToRegion() must be \'excitatory\', \'inhibitory\' or None'
        
        pathway = Pathway(region1 = self, region2 = otherRegion, region1Projects = True if knownProjection else None, region2Projects = bidirectional, region1Activation = backActivation, region2Activation = activation, name = name)
        self.pathways.append(pathway)
        otherRegion.pathways.append(pathway)
        self.network.addObject(pathway)
        return pathway
    
    
    def connections(self, recurse = True):
        connections = NeuroObject.connections(self, recurse) + self.pathways + self.arborizations
        if recurse:
            for subRegion in self.subRegions:
                connections += subRegion.connections() 
        return connections
    
    
    def inputs(self, recurse = True):
        inputs = NeuroObject.inputs(self, recurse)
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
        outputs = NeuroObject.outputs(self, recurse)
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
    
    
    def defaultVisualizationParams(self):
        params = NeuroObject.defaultVisualizationParams(self)
        params['size'] = (0.1, 0.1, 0.1)
        if self.parentRegion:
            params['parent'] = self.parentRegion
        if any(self.subRegions) or any(self.neurons):
            params['children'] = self.subRegions + self.neurons
        return params
