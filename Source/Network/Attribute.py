from wx.py import dispatcher
import xml.etree.ElementTree as ElementTree
from datetime import datetime, date, time
    
class Attribute(object):
    
    STRING_TYPE = 'string'
    INTEGER_TYPE = 'integer'
    DECIMAL_TYPE = 'double'
    BOOLEAN_TYPE = 'boolean'
    DATETIME_TYPE = 'dateTime'
    DATE_TYPE = 'date'
    TIME_TYPE = 'time'
    TYPES = [STRING_TYPE, INTEGER_TYPE, DECIMAL_TYPE, BOOLEAN_TYPE, DATETIME_TYPE, DATE_TYPE, TIME_TYPE]
    NATIVE_TYPES = { STRING_TYPE: [str, unicode], INTEGER_TYPE: [int], DECIMAL_TYPE: [float], BOOLEAN_TYPE: [bool], DATETIME_TYPE: [datetime], DATE_TYPE: [date], TIME_TYPE: [time]}
    
    
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
        elif type == cls.DATETIME_TYPE:
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
            value = valueText.lower() in ['true', 't', 'yes', 'y', '1']
        elif type == Attribute.DATETIME_TYPE:
            value = datetime.strptime(valueText, '%Y-%m-%d %H:%M:%S')
        elif type == Attribute.DATE_TYPE:
            value = datetime.strptime(valueText, '%Y-%m-%d').date()
        elif type == Attribute.TIME_TYPE:
            value = datetime.strptime(valueText, '%H:%M:%S').time()
        
        return Attribute(object, name, type, value)
    
    
    def __init__(self, object, name = None, type = None, value = None):
        self.object = object    # The object that this attribute describes.
        self.name = name
        self.type = type
        self.value = value
    
    
    def toXMLElement(self, parentElement):
        element = ElementTree.SubElement(parentElement, 'Attribute', type = self.type)
        ElementTree.SubElement(element, 'Name').text = self.name
        if self.type == Attribute.DATETIME_TYPE:
            valueText = self.value.strftime('%Y-%m-%d %H:%M:%S')
        if self.type == Attribute.DATE_TYPE:
            valueText = self.value.strftime('%Y-%m-%d')
        elif self.type == Attribute.TIME_TYPE:
            valueText = self.value.strftime('%H:%M:%S')
        else:
            valueText = str(self.value)
        ElementTree.SubElement(element, 'Value').text = valueText
        return element
    
    
    def toScriptFile(self, scriptFile, scriptRefs):
        from Network import Network
        if isinstance(self.object, Network):
            scriptFile.write('network')
        else:
            scriptFile.write(scriptRefs[self.object.networkId])
        scriptFile.write('.addAttribute(\'' + self.name.replace('\\', '\\\\').replace('\'', '\\\'') + '\', Attribute.' + self.type.upper() + '_TYPE, ')
        if self.type == Attribute.STRING_TYPE:
            scriptFile.write('\'' + self.value.replace('\\', '\\\\').replace('\'', '\\\'') + '\'')
        elif self.type in (Attribute.INTEGER_TYPE, Attribute.DECIMAL_TYPE, Attribute.BOOLEAN_TYPE):
            scriptFile.write(str(self.value))
        elif self.type == Attribute.DATETIME_TYPE:
            scriptFile.write('datetime.strptime(\'' + self.value.strftime('%Y-%m-%d %H:%M:%S') + '\', \'%Y-%m-%d %H:%M:%S\')')
        elif self.type == Attribute.DATE_TYPE:
            scriptFile.write('datetime.strptime(\'' + self.value.strftime('%Y-%m-%d') + '\', \'%Y-%m-%d\').date()')
        elif self.type == Attribute.TIME_TYPE:
            scriptFile.write('datetime.strptime(\'' + self.value.strftime('%H:%M:%S') + '\', \'%H:%M:%S\').time()')
        scriptFile.write(')\n')
    
    
    def setName(self, name):
        if name != self.name:
            self.name = name
            dispatcher.send(('set', 'name'), self)
    
    
    def setType(self, type):
        if type not in Attribute.TYPES:
            raise ValueError, gettext("'%s' is an unknown type") % (type)
        
        if type != self.type:
            self.type = type
            originalValue = self.value
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
            elif type == Attribute.DATETIME_TYPE:
                if isinstance(self.value, date):
                    self.value = datetime.combine(self.value, datetime.now().time().replace(microsecond = 0))
                elif isinstance(self.value, time):
                    self.value = datetime.combine(date.today(), self.value)
                else:
                    self.value = datetime.now().replace(microsecond = 0)
            elif type == Attribute.DATE_TYPE:
                if isinstance(self.value, datetime):
                    self.value = self.value.date()
                else:
                    self.value = date.today()
            elif type == Attribute.TIME_TYPE:
                if isinstance(self.value, datetime):
                    self.value = self.value.time()
                else:
                    self.value = datetime.now().time().replace(microsecond = 0)
            dispatcher.send(('set', 'type'), self)
            if self.value != originalValue:
                dispatcher.send(('set', 'value'), self)
    
    
    def setValue(self, value):
        if value.__class__ not in Attribute.NATIVE_TYPES[self.type]:
            validTypes = Attribute.NATIVE_TYPES[self.type]
            validTypesString = "'" + validTypes[0].__name__ + "'"
            if len(validTypes) > 1:
                for validType in validTypes[1:-1]:
                    validTypesString = validTypesString + ", '" + validType.__name__ + "'"
                validTypesString = validTypesString + ' ' + gettext('or') + " '" + validTypes[-1].__name__ + "'"
            raise ValueError, gettext("Values of %s attributes must be of type %s") % (Attribute.displayNameForType(self.type).lower(), validTypesString)
            
        if value != self.value:
            self.value = value
            dispatcher.send(('set', 'value'), self)
