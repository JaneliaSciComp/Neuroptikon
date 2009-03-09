from Object import Object
from wx.py import dispatcher
import xml.etree.ElementTree as ElementTree


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
    
    
    def toXMLElement(self, parentElement):
        terminusElement = ElementTree.SubElement(parentElement, self.__class__.__name__, regionId = str(self.region.networkId))
        if self.sendsOutput is not None:
            terminusElement.set('sends', 'true' if self.sendsOutput else 'false')
        if self.receivesInput is not None:
            terminusElement.set('receives', 'true' if self.receivesInput else 'false')
        return terminusElement
    
    
    def __setattr__(self, name, value):
        # Send out a message whenever one of this object's values changes.  This is needed, for example, to allow the GUI to update when an object is modified via the console or a script.
        hasPreviousValue = hasattr(self, name)
        if hasPreviousValue:
            previousValue = getattr(self, name)
        object.__setattr__(self, name, value)
        if not hasPreviousValue or getattr(self, name) != previousValue:
            dispatcher.send(('set', name), self)
    
    
class Pathway(Object):
    
    def __init__(self, region1, region2, *args, **keywords):
        Object.__init__(self, region1.network, *args, **keywords)
        
        self.neurites = []
        
        self.terminus1 = PathwayTerminus(self, region1)
        self.terminus2 = PathwayTerminus(self, region2)
    
    
    @classmethod
    def fromXMLElement(cls, network, xmlElement):
        object = super(Pathway, cls).fromXMLElement(network, xmlElement)
        object.neurites = []
        terminusElements = xmlElement.findall('PathwayTerminus')
        if len(terminusElements) != 2:
            raise ValueError, gettext('A pathway must have two and only two termini.')
        object.terminus1 = PathwayTerminus.fromXMLElement(network, terminusElements[0])
        if object.terminus1 is None:
            raise ValueError, gettext('Could not create pathway terminus')
        object.terminus1.pathway = object
        object.terminus2 = PathwayTerminus.fromXMLElement(network, terminusElements[1])
        if object.terminus2 is None:
            raise ValueError, gettext('Could not create pathway terminus')
        object.terminus2.pathway = object
        return object
     
    
    def toXMLElement(self, parentElement):
        pathwayElement = Object.toXMLElement(self, parentElement)
        self.terminus1.toXMLElement(pathwayElement)
        self.terminus2.toXMLElement(pathwayElement)
        return pathwayElement
   
    
    def addNeurite(self, neurite):
        neurite.setPathway(self)
    
    
    def inputs(self):
        inputs = Object.inputs(self)
        if terminus1.receivesInput:
            inputs.append(terminus1.region)
        if terminus2.receivesInput:
            inputs.append(terminus2.region)
        return inputs
    
    
    def outputs(self):
        outputs = Object.outputs(self)
        if terminus1.sendsOutput:
            inputs.append(terminus1.region)
        if terminus2.sendsOutput:
            inputs.append(terminus2.region)
        return outputs
    
