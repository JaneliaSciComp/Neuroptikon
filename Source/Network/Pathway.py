from Object import Object
from wx.py import dispatcher


class PathwayTerminus(object):
    def __init__(self, pathway, region, sendsOutput=None, receivesInput=None):
        object.__init__(self)
        
        self.pathway = pathway
        self.region = region
        self.sendsOutput = sendsOutput
        self.receivesInput = receivesInput
    
    
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
    
