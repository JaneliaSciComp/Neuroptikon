from Object import Object
import wx
import xml.etree.ElementTree as ElementTree

class Stimulus(Object):
    
    def __init__(self, network, target = None, modality = None, *args, **keywords):
        if target is None:
            raise ValueError, gettext('A stimulus must have a target')
        
        if not keywords.has_key('name') or keywords['name'] is None:
            keywords['name'] = modality.name
            
        Object.__init__(self, network, *args, **keywords)
        self.target = target
        self.modality = modality
    
    
    @classmethod
    def fromXMLElement(cls, network, xmlElement):
        object = super(Stimulus, cls).fromXMLElement(network, xmlElement)
        targetId = xmlElement.get('targetId')
        object.target = network.objectWithId(targetId)
        if object.target is None:
            raise ValueError, gettext('Object with id "%s" does not exist') % (targetId)
        object.target.stimuli.append(object)
        modalityId = xmlElement.get('modality')
        object.modality = wx.GetApp().library.modality(modalityId)
        if object.modality is None:
            raise ValueError, gettext('Modality "%s" does not exist') % (modalityId)
        return object
    
    
    def toXMLElement(self, parentElement):
        stimulusElement = Object.toXMLElement(self, parentElement)
        stimulusElement.set('targetId', str(self.target.networkId))
        stimulusElement.set('modality', self.modality.identifier)
        return stimulusElement
    
    
    def creationScriptCommand(self, scriptRefs):
        return scriptRefs[self.target.networkId] + '.stimulate'
    
    
    def creationScriptParams(self, scriptRefs):
        args, keywords = Object.creationScriptParams(self, scriptRefs)
        if self.modality is not None:
            keywords['modality'] = 'library.modality(\'' + self.modality.identifier.replace('\\', '\\\\').replace('\'', '\\\'') + '\')'
        return (args, keywords)
    
    
    def creationScript(self, scriptRefs):
        script = 'network.createStimulus(target = ' + scriptRefs[self.target.networkId]
        if self.modality is not None:
            script += ', modality = library.modality(\'' + self.modality.identifier + '\')'
        params = self.creationScriptParams(scriptRefs)
        if len(params) > 0:
            script += ', ' + ', '.join(params)
        script += ')'
        return script
    
    
    def outputs(self):
        return [self.target]
    
    
