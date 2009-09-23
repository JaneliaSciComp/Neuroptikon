from Object import Object
from pydispatch import dispatcher
import xml.etree.ElementTree as ElementTree


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
    
    
class Pathway(Object):
    
    def __init__(self, region1, region2, region1Projects = None, region2Projects = None, *args, **keywords):
        """
        Pathways connect pairs of :class:`regions <Network.Region.Region>`.  They consist of bundles of :class:`neurites <Network.Neurite.Neurite>` which can be optionally specified.
        
        You create a pathway by :meth:`messaging <Network.Region.Region.projectToRegion>` one of the regions:
        
        >>> pathway_1_2 = region1.projectToRegion(region2)
        """
        
        Object.__init__(self, region1.network, *args, **keywords)
        
        self._neurites = []
        
        self.region1 = region1
        self.region1Projects = region1Projects
        self.region2 = region2
        self.region2Projects = region2Projects
    
    
    def defaultName(self):
        names = [str(self.region1.name), str(self.region2.name)]
        names.sort()
        return names[0] + ' <-> ' + names[1]
    
    
    @classmethod
    def _fromXMLElement(cls, network, xmlElement):
        object = super(Pathway, cls)._fromXMLElement(network, xmlElement)
        object._neurites = []
        terminusElements = xmlElement.findall('PathwayTerminus')
        if len(terminusElements) == 0:
            # Format since 0.9.4
            regionId = xmlElement.get('region1Id')
            object.region1 = network.objectWithId(regionId)
            if object.region1 is None:
                raise ValueError, gettext('Region with id "%s" does not exist') % (regionId)
            object.region1.pathways += [object]
            sends = str(xmlElement.get('region1Projects')).lower()
            if sends.lower() in ['true', 't', '1', 'yes']:
                object.region1Projects = True
            elif sends.lower() in ['false', 'f', '0', 'no']:
                object.region1Projects = False
            else:
                object.region1Projects = None
            regionId = xmlElement.get('region2Id')
            object.region2 = network.objectWithId(regionId)
            if object.region2 is None:
                raise ValueError, gettext('Region with id "%s" does not exist') % (regionId)
            object.region2.pathways += [object]
            sends = str(xmlElement.get('region2Projects')).lower()
            if sends.lower() in ['true', 't', '1', 'yes']:
                object.region2Projects = True
            elif sends.lower() in ['false', 'f', '0', 'no']:
                object.region2Projects = False
            else:
                object.region2Projects = None
        else:
            # Format prior to version 0.9.4
            terminus1 = PathwayTerminus._fromXMLElement(network, terminusElements[0])
            if terminus1 is None:
                raise ValueError, gettext('Could not create connection to first region of pathway')
            object.region1 = terminus1.region
            object.region1Projects = terminus1.sendsOutput
            terminus2 = PathwayTerminus._fromXMLElement(network, terminusElements[1])
            if terminus2 is None:
                raise ValueError, gettext('Could not create connection to second region of pathway')
            object.region2 = terminus2.region
            object.region2Projects = terminus2.sendsOutput
        return object
     
    
    def _toXMLElement(self, parentElement):
        pathwayElement = Object._toXMLElement(self, parentElement)
        pathwayElement.set('region1Id', str(self.region1.networkId))
        if self.region1Projects != None:
            pathwayElement.set('region1Projects', str(self.region1Projects).lower())
        pathwayElement.set('region2Id', str(self.region2.networkId))
        if self.region2Projects != None:
            pathwayElement.set('region2Projects', str(self.region2Projects).lower())
        return pathwayElement
    
    
    def _needsScriptRef(self):
        return any(self._neurites) or Object._needsScriptRef(self)
        
        
    def _creationScriptCommand(self, scriptRefs):
        return scriptRefs[self.region1.networkId] + '.projectToRegion'
    
    
    def _creationScriptParams(self, scriptRefs):
        args, keywords = Object._creationScriptParams(self, scriptRefs)
        args.insert(0, scriptRefs[self.region2.networkId])
        if self.region1Projects != True:
            keywords['knownProjection'] = str(self.region1Projects)
        if self.region2Projects != None:
            keywords['bidirectional'] = str(self.region2Projects)
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
        return Object.connections(self, recurse) + [self.region1, self.region2]
    
    
    def inputs(self, recurse = True):
        inputs = Object.inputs(self, recurse)
        if self.region1Projects:
            inputs += [self.region1]
        if self.region2Projects:
            inputs += [self.region2]
        return inputs
    
    
    def outputs(self, recurse = True):
        outputs = Object.outputs(self, recurse)
        if self.region1Projects:
            outputs += [self.region2]
        if self.region2Projects:
            outputs += [self.region1]
        return outputs
    
