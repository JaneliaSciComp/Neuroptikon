from wx.py import dispatcher
import xml.etree.ElementTree as ElementTree
from datetime import datetime, date, time
    
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
        valueText = xmlElement.findtext('Value')
        if type == Attribute.STRING_TYPE:
            value = valueText
        elif type == Attribute.INTEGER_TYPE:
            try:
                value = int(valueText)
            except:
                value = 0
        elif type == Attribute.DECIMAL_TYPE:
            try:
                value = float(valueText)
            except:
                value = 0.0
        elif type == Attribute.BOOLEAN_TYPE:
            value = valueText in ['True', 'T', '1']
        elif type == Attribute.DATE_TIME_TYPE:
            value = datetime.strptime(valueText, '%Y-%m-%d %H:%M:%S')
        elif type == Attribute.DATE_TYPE:
            value = datetime.strptime(valueText, '%Y-%m-%d').date()
        elif type == Attribute.TIME_TYPE:
            value = datetime.strptime(valueText, '%H:%M:%S').time()
        
        return Attribute(object, name, type, value)
    
    
    def __init__(self, object, name = None, type = None, value = None):
        self.object = object
        self.name = name
        self.type = type
        self.value = value
    
    
    def toXMLElement(self, parentElement):
        element = ElementTree.SubElement(parentElement, 'Attribute', type = self.type)
        ElementTree.SubElement(element, 'Name').text = self.name
        if self.type == Attribute.DATE_TIME_TYPE:
            valueText = self.value.strftime('%Y-%m-%d %H:%M:%S')
        elif self.type == Attribute.TIME_TYPE:
            valueText = self.value.strftime('%H:%M:%S')
        else:
            valueText = str(self.value)
        ElementTree.SubElement(element, 'Value').text = valueText
        return element
    
    
    def setName(self, name):
        self.name = name
        dispatcher.send(('set', 'name'), self)
    
    
    def setType(self, type):
        if type not in Attribute.TYPES:
            raise ValueError, gettext('Unknown type %s') % (type)
        
        if type != self.type:
            self.type = type
            if type == Attribute.STRING_TYPE:
                self.value = ''
            elif type == Attribute.INTEGER_TYPE:
                try:
                    self.value = int(self.value)
                except:
                    self.value = 0
            elif type == Attribute.DECIMAL_TYPE:
                try:
                    self.value = float(self.value)
                except:
                    self.value = 0.0
            elif type == Attribute.BOOLEAN_TYPE:
                self.value = True
            elif type == Attribute.DATE_TIME_TYPE:
                self.value = datetime.now()
            elif type == Attribute.DATE_TYPE:
                self.value = date.today()
            elif type == Attribute.TIME_TYPE:
                self.value = datetime.now().time()
            dispatcher.send(('set', 'type'), self)
            dispatcher.send(('set', 'value'), self)
    
    
    def setValue(self, value):
        # TODO: make sure value is valid for the current type
        self.value = value
        dispatcher.send(('set', 'value'), self)
