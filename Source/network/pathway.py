#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

import neuroptikon
from neuro_object import NeuroObject
from pydispatch import dispatcher


# Legacy class used by versions prior to 0.9.4.  Preserved here to allow loading of older XML files.
class PathwayTerminus(object):
    def __init__(self, pathway, region, sendsOutput=None, receivesInput=None):
        object.__init__(self)
        
        self.pathway = pathway
        self.region = region
        self.sendsOutput = sendsOutput
        self.receivesInput = receivesInput
    
    
    @classmethod
    def _fromXMLElement(cls, network, xmlElement):
        regionId = xmlElement.get('regionId')
        region = network.objectWithId(regionId)
        if region is None:
            raise ValueError, gettext('Region with id "%s" does not exist') % (regionId)
        sends = xmlElement.get('sends')
        if sends == 'true':
            sends = True
        elif sends == 'false':
            sends = False
        else:
            sends = None
        receives = xmlElement.get('receives')
        if receives == 'true':
            receives = True
        elif receives == 'false':
            receives = False
        else:
            receives = None
        return PathwayTerminus(network, region, sends, receives)
    
    
class Pathway(NeuroObject):
    
    def __init__(self, region1, region2, region1Projects = None, region1Activation = None, region2Projects = None, region2Activation = None, *args, **keywords):
        """
        Pathways connect pairs of :class:`regions <Network.Region.Region>`.  They consist of bundles of :class:`neurites <Network.Neurite.Neurite>` which can be optionally specified.
        
        You create a pathway by :meth:`messaging <Network.Region.Region.projectToRegion>` one of the regions:
        
        >>> pathway_1_2 = region1.projectToRegion(region2)
        """
        
        NeuroObject.__init__(self, region1.network, *args, **keywords)
        
        self._neurites = []
        
        self.region1 = region1
        self.region1Projects = region1Projects
        self.region1Activation = region1Activation
        self.region2 = region2
        self.region2Projects = region2Projects
        self.region2Activation = region2Activation
    
    
    def defaultName(self):
        names = [str(self.region1.name), str(self.region2.name)]
        names.sort()
        return names[0] + ' <-> ' + names[1]
    
    
    @classmethod
    def _fromXMLElement(cls, network, xmlElement):
        pathway = super(Pathway, cls)._fromXMLElement(network, xmlElement)
        pathway._neurites = []
        terminusElements = xmlElement.findall('PathwayTerminus')
        if len(terminusElements) == 0:
            # Format since 0.9.4
            regionId = xmlElement.get('region1Id')
            pathway.region1 = network.objectWithId(regionId)
            if pathway.region1 is None:
                raise ValueError, gettext('Region with id "%s" does not exist') % (regionId)
            pathway.region1.pathways += [pathway]
            sends = str(xmlElement.get('region1Projects')).lower()
            if sends.lower() in ['true', 't', '1', 'yes']:
                pathway.region1Projects = True
            elif sends.lower() in ['false', 'f', '0', 'no']:
                pathway.region1Projects = False
            else:
                pathway.region1Projects = None
            pathway.region1Activation = xmlElement.get('region1Activation')
            regionId = xmlElement.get('region2Id')
            pathway.region2 = network.objectWithId(regionId)
            if pathway.region2 is None:
                raise ValueError, gettext('Region with id "%s" does not exist') % (regionId)
            pathway.region2.pathways += [pathway]
            sends = str(xmlElement.get('region2Projects')).lower()
            if sends.lower() in ['true', 't', '1', 'yes']:
                pathway.region2Projects = True
            elif sends.lower() in ['false', 'f', '0', 'no']:
                pathway.region2Projects = False
            else:
                pathway.region2Projects = None
            pathway.region2Activation = xmlElement.get('region2Activation')
        else:
            # Format prior to version 0.9.4
            terminus1 = PathwayTerminus._fromXMLElement(network, terminusElements[0])
            if terminus1 is None:
                raise ValueError, gettext('Could not create connection to first region of pathway')
            pathway.region1 = terminus1.region
            pathway.region1Projects = terminus1.sendsOutput
            terminus2 = PathwayTerminus._fromXMLElement(network, terminusElements[1])
            if terminus2 is None:
                raise ValueError, gettext('Could not create connection to second region of pathway')
            pathway.region2 = terminus2.region
            pathway.region2Projects = terminus2.sendsOutput
        return pathway
     
    
    def _toXMLElement(self, parentElement):
        pathwayElement = NeuroObject._toXMLElement(self, parentElement)
        pathwayElement.set('region1Id', str(self.region1.networkId))
        if self.region1Projects != None:
            pathwayElement.set('region1Projects', str(self.region1Projects).lower())
            if self.region1Projects and self.region2Activation is not None:
                pathwayElement.set('region2Activation', self.region2Activation)
        pathwayElement.set('region2Id', str(self.region2.networkId))
        if self.region2Projects != None:
            pathwayElement.set('region2Projects', str(self.region2Projects).lower())
            if self.region2Projects and self.region1Activation is not None:
                pathwayElement.set('region1Activation', self.region1Activation)
        return pathwayElement
    
    
    def _needsScriptRef(self):
        return any(self._neurites) or NeuroObject._needsScriptRef(self)
        
        
    def _creationScriptCommand(self, scriptRefs):
        return scriptRefs[self.region1.networkId] + '.projectToRegion'
    
    
    def _creationScriptParams(self, scriptRefs):
        args, keywords = NeuroObject._creationScriptParams(self, scriptRefs)
        args.insert(0, scriptRefs[self.region2.networkId])
        if self.region1Projects != True:
            keywords['knownProjection'] = str(self.region1Projects)
        elif self.region2Activation is not None:
            keywords['activation'] = self.region2Activation
        if self.region2Projects != None:
            keywords['bidirectional'] = str(self.region2Projects)
        elif self.region1Activation is not None:
            keywords['backActivation'] = self.region1Activation
        return (args, keywords)
   
    
    def addNeurite(self, neurite):
        """
        Add the given :class:`neurite <Network.Neurite.Neurite>` to this pathway.
        """
        
        if neurite not in self._neurites:
            self._neurites += [neurite]
            neurite.setPathway(self)
            dispatcher.send(('set', 'neurites'), self)
     
    
    def removeNeurite(self, neurite):
        """
        Remove the given :class:`neurite <Network.Neurite.Neurite>` from this pathway.
        """
        
        if neurite in self._neurites:
            self._neurites.remove(neurite)
            neurite.setPathway(None)
            dispatcher.send(('set', 'neurites'), self)
    
    
    def neurites(self):
        """
        Return a list of the :class:`neurites <Network.Neurite.Neurite>` in this pathway.
        """
        
        return list(self._neurites)
    
    
    
    def regions(self):
        """
        Return a tuple containing the :class:`regions <Network.Region.Region>` connected by this pathway.
        """
        return (self.region1, self.region2)
    
    
    def connections(self, recurse = True):
        return NeuroObject.connections(self, recurse) + [self.region1, self.region2]
    
    
    def inputs(self, recurse = True):
        inputs = NeuroObject.inputs(self, recurse)
        if self.region1Projects:
            inputs += [self.region1]
        if self.region2Projects:
            inputs += [self.region2]
        return inputs
    
    
    def outputs(self, recurse = True):
        outputs = NeuroObject.outputs(self, recurse)
        if self.region1Projects:
            outputs += [self.region2]
        if self.region2Projects:
            outputs += [self.region1]
        return outputs
    
    
    def disconnectFromNetwork(self):
        self.region1.pathways.remove(self)
        self.region2.pathways.remove(self)
    
    
    def defaultVisualizationParams(self):
        params = NeuroObject.defaultVisualizationParams(self)
        params['shape'] = 'Line'
        params['color'] = (0.0, 0.0, 0.0)
        params['pathEndPoints'] = (self.region1, self.region2)
        params['flowTo'] = self.region1Projects
        params['flowFrom'] = self.region2Projects
        if self.region1Projects:
            if self.region2Activation == 'excitatory':
                params['flowToColor'] = (0.5, 0.5, 1.0)
            elif self.region2Activation == 'inhibitory':
                params['flowToColor'] = (1.0, 0.5, 0.5)
        if self.region2Projects:
            if self.region1Activation == 'excitatory':
                params['flowFromColor'] = (0.5, 0.5, 1.0)
            elif self.region1Activation == 'inhibitory':
                params['flowFromColor'] = (1.0, 0.5, 0.5)
        return params
    
