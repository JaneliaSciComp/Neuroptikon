from pydispatch import dispatcher
import xml.etree.ElementTree as ElementTree
from datetime import datetime, date, time
import copy

    
class Attribute(object):
    
    #: for type<'str'> values
    STRING_TYPE = 'string'
    #: for type<'int'> values
    INTEGER_TYPE = 'integer'
    #: for type<'float'> values
    DECIMAL_TYPE = 'double'
    #: for type<'bool'> values
    BOOLEAN_TYPE = 'boolean'
    #: for type<'datetime.datetime'> values
    DATETIME_TYPE = 'dateTime'
    #: for type<'datetime.date'> values
    DATE_TYPE = 'date'
    #: for type<'datetime.time'> values
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
    def _fromXMLElement(cls, object, xmlElement):
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
        self._name = name
        self._type = type
        self._value = value
    
    
    def _toXMLElement(self, parentElement):
        element = ElementTree.SubElement(parentElement, 'Attribute', type = self._type)
        ElementTree.SubElement(element, 'Name').text = self._name
        if self._type == Attribute.DATETIME_TYPE:
            valueText = self._value.strftime('%Y-%m-%d %H:%M:%S')
        if self._type == Attribute.DATE_TYPE:
            valueText = self._value.strftime('%Y-%m-%d')
        elif self._type == Attribute.TIME_TYPE:
            valueText = self._value.strftime('%H:%M:%S')
        else:
            valueText = str(self._value)
        ElementTree.SubElement(element, 'Value').text = valueText
        return element
    
    
    def _toScriptFile(self, scriptFile, scriptRefs):
        from Network import Network
        if isinstance(self.object, Network):
            scriptFile.write('network')
        else:
            scriptFile.write(scriptRefs[self.object.networkId])
        typeString = 'DECIMAL' if self._type == Attribute.DECIMAL_TYPE else self._type.upper()
        scriptFile.write('.addAttribute(\'' + self._name.replace('\\', '\\\\').replace('\'', '\\\'') + '\', Attribute.' + typeString + '_TYPE, ')
        if self._type == Attribute.STRING_TYPE:
            scriptFile.write('\'' + self._value.replace('\\', '\\\\').replace('\'', '\\\'') + '\'')
        elif self._type in (Attribute.INTEGER_TYPE, Attribute.DECIMAL_TYPE, Attribute.BOOLEAN_TYPE):
            scriptFile.write(str(self._value))
        elif self._type == Attribute.DATETIME_TYPE:
            scriptFile.write('datetime.strptime(\'' + self._value.strftime('%Y-%m-%d %H:%M:%S') + '\', \'%Y-%m-%d %H:%M:%S\')')
        elif self._type == Attribute.DATE_TYPE:
            scriptFile.write('datetime.strptime(\'' + self._value.strftime('%Y-%m-%d') + '\', \'%Y-%m-%d\').date()')
        elif self._type == Attribute.TIME_TYPE:
            scriptFile.write('datetime.strptime(\'' + self._value.strftime('%H:%M:%S') + '\', \'%H:%M:%S\').time()')
        scriptFile.write(')\n')
    
    
    def setName(self, name):
        """
        Set the name of the attribute.
        """
        
        if name != self._name:
            self._name = name
            dispatcher.send(('set', 'name'), self)
            from Object import Object
            if isinstance(self.object, Object):
                self.object.network.setModified(True)
            else:
                self.object.setModified(True)
    
    
    def name(self):
        """
        Return the name of the attribute.
        
        Altering the contents of the returned value will have no effect on the attribute.  You must call setName() to make any changes.
        """
        
        return str(self._name)
    
    
    def setType(self, type):
        """
        Set the type of the attribute.
        
        An attempt will be made to convert the existing attribute value to the new type otherwise a default value will be used.
        """
        
        if type not in Attribute.TYPES:
            raise ValueError, gettext("'%s' is an unknown type") % (type)
        
        if type != self._type:
            self._type = type
            originalValue = self._value
            if type == Attribute.STRING_TYPE:
                self._value = ''
            elif type == Attribute.INTEGER_TYPE:
                try:
                    self._value = int(self._value)
                except:
                    self._value = 0
            elif type == Attribute.DECIMAL_TYPE:
                try:
                    self._value = float(self._value)
                except:
                    self._value = 0.0
            elif type == Attribute.BOOLEAN_TYPE:
                self._value = True
            elif type == Attribute.DATETIME_TYPE:
                if isinstance(self.value, date):
                    self._value = datetime.combine(self._value, datetime.now().time().replace(microsecond = 0))
                elif isinstance(self._value, time):
                    self._value = datetime.combine(date.today(), self._value)
                else:
                    self._value = datetime.now().replace(microsecond = 0)
            elif type == Attribute.DATE_TYPE:
                if isinstance(self.value, datetime):
                    self._value = self._value.date()
                else:
                    self._value = date.today()
            elif type == Attribute.TIME_TYPE:
                if isinstance(self.value, datetime):
                    self._value = self._value.time()
                else:
                    self._value = datetime.now().time().replace(microsecond = 0)
            dispatcher.send(('set', 'type'), self)
            if self._value != originalValue:
                dispatcher.send(('set', 'value'), self)
            from Object import Object
            if isinstance(self.object, Object):
                self.object.network.setModified(True)
            else:
                self.object.setModified(True)
    
    
    def type(self):
        """
        Return the type of the attribute.
        """
        
        return str(self._type)
    
    
    def setValue(self, value):
        """
        Set the value of the attribute.
        
        If the type of the given value does not match the attribute's type then an exception will be raised. 
        """
        
        if value.__class__ not in Attribute.NATIVE_TYPES[self._type]:
            validTypes = Attribute.NATIVE_TYPES[self._type]
            validTypesString = "'" + validTypes[0].__name__ + "'"
            if len(validTypes) > 1:
                for validType in validTypes[1:-1]:
                    validTypesString = validTypesString + ", '" + validType.__name__ + "'"
                validTypesString = validTypesString + ' ' + gettext('or') + " '" + validTypes[-1].__name__ + "'"
            raise ValueError, gettext("Values of %s attributes must be of type %s") % (Attribute.displayNameForType(self._type).lower(), validTypesString)
            
        if value != self._value:
            self._value = value
            dispatcher.send(('set', 'value'), self)
            from Object import Object
            if isinstance(self.object, Object):
                self.object.network.setModified(True)
            else:
                self.object.setModified(True)
    
    
    def value(self):
        """
        Return a copy of the attribute's value.
        
        Altering the contents of the returned value will have no effect on the attribute.  You must call setValue() to make any changes.
        """
        
        return copy.copy(self._value)
