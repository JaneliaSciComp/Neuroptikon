from Object import Object
from wx.py import dispatcher
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
    def fromXMLElement(cls, network, xmlElement):
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
        Object.__init__(self, region1.network, *args, **keywords)
        
        self.neurites = []
        
        self.region1 = region1
        self.region1Projects = region1Projects
        self.region2 = region2
        self.region2Projects = region2Projects
    
    
    def defaultName(self):
        names = [str(self.region1.name), str(self.region2.name)]
        names.sort()
        return names[0] + ' <-> ' + names[1]
    
    
    @classmethod
    def fromXMLElement(cls, network, xmlElement):
        object = super(Pathway, cls).fromXMLElement(network, xmlElement)
        object.neurites = []
        terminusElements = xmlElement.findall('PathwayTerminus')
        if len(terminusElements) == 0:
            # Format since 0.9.4
            regionId = xmlElement.get('region1Id')
            object.region1 = network.objectWithId(regionId)
            if object.region1 is None:
                raise ValueError, gettext('Region with id "%s" does not exist') % (regionId)
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
            sends = str(xmlElement.get('region2Projects')).lower()
            if sends.lower() in ['true', 't', '1', 'yes']:
                object.region2Projects = True
            elif sends.lower() in ['false', 'f', '0', 'no']:
                object.region2Projects = False
            else:
                object.region2Projects = None
        else:
            # Format prior to version 0.9.4
            terminus1 = PathwayTerminus.fromXMLElement(network, terminusElements[0])
            if terminus1 is None:
                raise ValueError, gettext('Could not create connection to first region of pathway')
            object.region1 = terminus1.region
            object.region1Projects = terminus1.sendsOutput
            terminus2 = PathwayTerminus.fromXMLElement(network, terminusElements[1])
            if terminus2 is None:
                raise ValueError, gettext('Could not create connection to second region of pathway')
            object.region2 = terminus2.region
            object.region2Projects = terminus2.sendsOutput
        return object
     
    
    def toXMLElement(self, parentElement):
        pathwayElement = Object.toXMLElement(self, parentElement)
        pathwayElement.set('region1Id', str(self.region1.networkId))
        if self.region1Projects != None:
            pathwayElement.set('region1Projects', str(self.region1Projects).lower())
        pathwayElement.set('region2Id', str(self.region2.networkId))
        if self.region2Projects != None:
            pathwayElement.set('region2Projects', str(self.region2Projects).lower())
        return pathwayElement
    
    
    def needsScriptRef(self):
        return len(self.neurites) > 0 or Object.needsScriptRef(self)
        
        
    def creationScriptCommand(self, scriptRefs):
        return scriptRefs[self.region1.networkId] + '.projectToRegion'
    
    
    def creationScriptParams(self, scriptRefs):
        args, keywords = Object.creationScriptParams(self, scriptRefs)
        args.insert(0, scriptRefs[self.terminus2.region.networkId])
        if self.region1Projects is not None:
            keywords['sendsOutput'] = str(self.region1Projects)
        if self.region2Projects is not None:
            keywords['bidirectional'] = str(self.region2Projects)
        return (args, keywords)
   
    
    def addNeurite(self, neurite):
        neurite.setPathway(self)
    
    
    def inputs(self):
        inputs = Object.inputs(self)
        if region1Projects == None or region1Projects:
            inputs.append(region1)
        if region2Projects == None or region2Projects:
            inputs.append(region2)
        return inputs
    
    
    def outputs(self):
        outputs = Object.outputs(self)
        if region1Projects == None or region1Projects:
            inputs.append(region2)
        if region2Projects == None or region2Projects:
            inputs.append(region1)
        return outputs
    
