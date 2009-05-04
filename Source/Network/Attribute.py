from wx.py import dispatcher
import xml.etree.ElementTree as ElementTree
    
    
class Attribute(object):
    
    STRING_TYPE = 'string'
    INTEGER_TYPE = 'integer'
    DECIMAL_TYPE = 'double'
    BOOLEAN_TYPE = 'boolean'
    DATE_TIME_TYPE = 'dateTime'
    DATE_TYPE = 'date'
    TIME_TYPE = 'time'
    TYPES = [STRING_TYPE, INTEGER_TYPE, DECIMAL_TYPE, BOOLEAN_TYPE, DATE_TIME_TYPE, DATE_TYPE, TIME_TYPE]
    
    @classmethod
    def displayNameForType(cls, type):
        if type == cls.STRING_TYPE:
            return gettext('String')
        elif type == cls.INTEGER_TYPE:
            return gettext('Integer')
        elif type == cls.DECIMAL_TYPE:
            return gettext('Decimal')
        elif type == cls.BOOLEAN_TYPE:
            return gettext('True or False')
        elif type == cls.DATE_TIME_TYPE:
            return gettext('Date & Time')
        elif type == cls.DATE_TYPE:
            return gettext('Date')
        elif type == cls.TIME_TYPE:
            return gettext('Time')
        else:
            return gettext('Unknown Type')
    
    @classmethod
    def fromXMLElement(cls, object, xmlElement):
        name = xmlElement.findtext('Name')
        type = xmlElement.get('type')
        value = xmlElement.findtext('Value')
        
        return Attribute(object, name, type, value)
    
    
    def __init__(self, object, name = None, type = None, value = None):
        self.object = object
        self.name = name
        self.type = type
        self.value = value
    
    
    def toXMLElement(self, parentElement):
        element = ElementTree.SubElement(parentElement, 'Attribute', type = self.type)
        ElementTree.SubElement(element, 'Name').text = self.name
        ElementTree.SubElement(element, 'Value').text = self.value
        return element
    
    
    def setName(self, name):
        self.name = name
        dispatcher.send(('set', 'name'), self)
    
    
    def setType(self, type):
        self.type = type
        # TODO: try to convert the value, else use a default
        dispatcher.send(('set', 'type'), self)
    
    
    def setValue(self, value):
        # TODO: make sure value is valid for the current type
        self.value = value
        dispatcher.send(('set', 'value'), self)
