from obitools.utils import skipWhiteLineIterator,multiLineWrapper
from obitools.utils import universalOpen
from obitools.format.genericparser import genericEntryIteratorGenerator
from logging import debug,warning

import re


#################################################################################
##                           Stanza preparation area                           ##
#################################################################################


class FileFormatError(Exception):
    '''
       An error derived from the class Exception.
    ''' 
    pass

_oboEntryIterator = genericEntryIteratorGenerator(endEntry='^ *$',
                                                  strip=True)

def stanzaIterator(inputfile):
    '''
    Iterator of stanza. The stanza are the basic units of OBO files.
    
    @param inputfile: a stream of strings from an opened OBO file.
    @type inputfile: a stream of strings
    
    @return: a stream of stanza
    @rtype: a stream of aggregated strings
    
    @note: The iterator constructs stanza by aggregate strings from the
    OBO file.
    '''
    inputfile = universalOpen(inputfile)
    inputfile = multiLineWrapper(inputfile)
    return _oboEntryIterator(inputfile)
    
    

#################################################################################
##                      Trailing Modifiers treatment area                      ##
#################################################################################


class TrailingModifier(dict):
    '''
       A class object which inherits from the class dict. Trailing modifiers can be found
       at the end of TaggedValue objects when they exist.
    '''
    
    _match_brace = re.compile('(?<=\ {)[^\]]*(\}) *( !|$)')

    def __init__(self,string):
        
        ## search for trailing modifiers signals
        trailing_modifiers = TrailingModifier._match_brace.search(string)
        
        ## the trailing modifiers exist
        if trailing_modifiers:
            trailing_modifiers=trailing_modifiers.group(0).strip()
            print trailing_modifiers
            ## creates and feeds the dictionary of trailing modifiers
            dict.__init__(self,(x.strip().split('=',1) for x in trailing_modifiers.split(',')))
            
        
def trailingModifierFactory(string):
    '''
    Dispatcher of trailing modifiers.
    
    @param string: a string from a TaggedValue object with a trailing modifiers signal.
    @type string: string
    
    @return: a class object
    
    @note: The dispatcher is currently very simple. Only one case is treated by the function.
    `the function returns a class object inherited from the class dict if the trailing modifiers
    exist, None if they don't.
    '''
    
    trailing_modifiers = TrailingModifier(string)
    if not trailing_modifiers:
        trailing_modifiers=None
    return trailing_modifiers


#################################################################################
##                          TaggedValue treatment area                         ##
#################################################################################


class TaggedValue(object):
    '''
       A couple 'tag:value' of an OBOEntry.
    ''' 

    _match_value   = re.compile('(("(\\\\"|[^\"])*")|(\\\\"|[^\"]))*?( !| {|$)')
    _split_comment = re.compile('^!| !')
    _match_quotedString = re.compile('(?<=")(\\\\"|[^\"])*(?=")')
    _match_bracket = re.compile('\[[^\]]*\]')

    def __init__(self,line):
        '''
        Constructor of the class TaggedValue.
        
        @param line: a line of an OBOEntry composed of a tag and a value.
        @type line: string
        
        @note: The constructor separates tags from right terms. 'value' is extracted 
        from right terms using a regular expression (value is at the beginning of the
        string, between quotes or not). Then, 'comment' is extracted from the rest of the 
        string using another regular expression ('comment' is at the end of the string 
        after a '!'. By default, 'comment' is set to None). Finally, 'trailing_modifiers'
        are extracted from the last string using another regular expression.
        The tag, the value, the comment and the trailing_modifiers are saved.
        '''
        
        debug("tagValueParser : %s" % line)

        ## by default :
        trailing_modifiers = None
        comment = None
        
        ## the tag is saved. 'right' is composed of the value, the comment and the trailing modifiers
        tag,rigth = line.split(':',1)
        
        ## the value is saved
        value = TaggedValue._match_value.search(rigth).group(0)
        debug("Extracted value : %s" % value)
        
        ## if there is a value AND a sign of a comment or trailing modifiers
        if value and value[-1] in '!{':
            lvalue = len(value)
            ## whatever it is a comment or trailing modifiers, it is saved into 'extra'
            extra = rigth[lvalue-1:].strip()
            ## a comment is extracted
            extra =TaggedValue._split_comment.split(extra,1)
            ## and saved if it exists
            if len(extra)==2:
                comment=extra[1].strip()
            ## trailing modifiers are extracted
            extra=extra[0]
            trailing_modifiers = trailingModifierFactory(extra)
            ## the value is cleaned of any comment or trailing modifiers signals
            value = value[0:-1]
            
        if tag=='use_term':
            tag='consider'
            raise DeprecationWarning,"user_term is a deprecated tag, you should instead use consider"
        
        ## recording zone
        self.value  =value.strip()
        self.tag    = tag
        self.__doc__=comment
        self.trailing_modifiers=trailing_modifiers
        
    def __str__(self):
        return str(self.value)
    
    def __repr__(self):
        return '''"""%s"""''' % str(self)


class NameValue(TaggedValue):
    '''
       A couple 'name:value' inherited from the class TaggedValue. Used to manage name tags.
    ''' 
    
    def __init__(self,line):
        
        ## no use of the TaggedValue constructor. The NameValue is very simple.
        tag,rigth = line.split(':',1)
        
        ## recording zone
        self.value = rigth.strip()
        self.tag = 'name'
        self.__doc__=None
        self.trailing_modifiers=None
        
        
        
class DefValue(TaggedValue):
    '''
       A couple 'def:value' inherited from the class TaggedValue. Used to manage def tags.
    ''' 
    
    def __init__(self,line):
        '''
        Constructor of the class DefValue.
        
        @param line: a line of an OBOEntry composed of a tag named 'def' and a value.
        @type line: string
        
        @note: The constructor calls the TaggedValue constructor. A regular expression 
        is used to extract the 'definition' from TaggedValue.value (definition is a not 
        quoted TaggedValue.value). A regular expression is used to extract 'dbxrefs' 
        from the aggedValue.value without the definition (dbxrefs are between brackets
        and definition can be so). Definition is saved as the new value of the DefValue.
        dbxrefs are saved.
        '''
        
        ## use of the TaggedValue constructor
        TaggedValue.__init__(self, line)
        
        ## definition, which is quoted, is extracted from the standard value of a TaggedValue.
        definition = TaggedValue._match_quotedString.search(self.value).group(0)
        
        ## the standard value is cleaned of the definition.
        cleanvalue = self.value.replace(definition,'')
        cleanvalue = cleanvalue.replace('  ',' ')
        
        ## dbxrefs are searched into the rest of the standard value.
        dbxrefs    = TaggedValue._match_bracket.search(cleanvalue).group(0)
        
        ## recording zone
        self.tag = 'def'
        ## the value of a DefValue is not the standard value but the definition.
        self.value=definition
        self.dbxrefs=xrefFactory(dbxrefs)
        
        
class SynonymValue(TaggedValue):
    '''
       A couple 'synonym:value' inherited from the class TaggedValue. Used to manage 
       synonym tags, exact_synonym tags, broad_synonym tags and narrow_synonym tags.
    ''' 
    
    _match_scope = re.compile('(?<="")[^\[]*(?=\[|$)')
    
    def __init__(self,line):
        '''
        Constructor of the class SynonymValue.
        
        @param line: a line of an OBOEntry composed of a tag named 'synonym' or
        'exact_synonym' or 'broad_synonym' or 'narrow_synonym' and a value.
        @type line: string
        
        @note: SynonymValue is composed of a tag, a value, a scope, a list of types and 
        dbxrefs.
        The constructor calls the TaggedValue constructor. A regular expression 
        is used to extract 'definition' from TaggedValue.value (definition is a not 
        quoted TaggedValue.value). Definition is saved as the new value of the class
        SynonymValue.
        A regular expression is used to extract 'attributes' from the rest of the
        string. Attributes may contain an optional synonym scope and an optional list 
        of synonym types. The scope is extracted from attributes or set by default to
        'RELATED'. It is saved as the scope of the class. The types are the rest of the 
        attributes and are saved as the list of types of the class.
        For deprecated tags 'exact_synonym', 'broad_synonym' and 'narrow_synonym', tag
        is set to 'synonym' and scope is set respectively to 'EXACT', 'BROAD' and 'NARROW'.
        A regular expression is used to extract 'dbxrefs' from the TaggedValue.value 
        without the definition (dbxrefs are between brackets and definition can be so).
        dbxrefs are saved.
        '''
        
        ## use of the TaggedValue constructor
        TaggedValue.__init__(self, line)
        
        ## definition, which is quoted, is extracted from the standard value of a TaggedValue.
        definition = TaggedValue._match_quotedString.search(self.value).group(0)
        
        ## the standard value is cleaned of the definition.
        cleanvalue = self.value.replace(definition,'')
        cleanvalue = cleanvalue.replace('  ',' ')
        
        ## 1) attributes are searched into the rest of the standard value.
        ## 2) then they are stripped.
        ## 3) then they are split on every ' '.
        ## 4) finally they are ordered into a set.
        attributes = set(SynonymValue._match_scope.search(cleanvalue).group(0).strip().split())
        
        ## the scopes are the junction between the attributes and a set of specific terms. 
        scopes     = attributes & set(['RELATED','EXACT','BROAD','NARROW'])
        
        ## the types are the rest of the attributes.
        types      = attributes - scopes
        
        ## this is a constraint of the OBO format
        assert len(scopes)< 2,"Only one synonym scope allowed"
        
        ## the scope of the SynonymValue is into scopes or set by default to RELATED
        if scopes:
            scope = scopes.pop()
        else:
            scope = 'RELATED'
        
        ## Specific rules are defined for the following tags :    
        if self.tag == 'exact_synonym':
            raise DeprecationWarning,'exact_synonym is a deprecated tag use instead synonym tag'
            self.tag   = 'synonym'
            scope = 'EXACT'
            
        if self.tag == 'broad_synonym':
            raise DeprecationWarning,'broad_synonym is a deprecated tag use instead synonym tag'
            self.tag   = 'synonym'
            scope = 'BROAD'
            
        if self.tag == 'narrow_synonym':
            raise DeprecationWarning,'narrow_synonym is a deprecated tag use instead synonym tag'
            self.tag   = 'synonym'
            scope = 'NARROW'
            
        if self.tag == 'systematic_synonym':
            #raise DeprecationWarning,'narrow_synonym is a deprecated tag use instead sysnonym tag'
            self.tag   = 'synonym'
            scope = 'SYSTEMATIC'
        
        ## this is our own constraint. deprecated tags are not saved by this parser.    
        assert self.tag =='synonym',"%s synonym type is not managed" % self.tag
        
        ## dbxrefs are searched into the rest of the standard value.
        dbxrefs    = TaggedValue._match_bracket.search(cleanvalue).group(0)
        
        ## recording zone
        ## the value of a SynonymValue is not the standard value but the definition.
        self.value   = definition
        self.dbxrefs = xrefFactory(dbxrefs)
        self.scope   = scope
        self.types   = list(types)
        
    def __eq__(self,b):
        return ((self.value==b.value) and (self.dbxrefs==b.dbxrefs) 
                and (self.scope==b.scope) and (self.types==b.types)
                and (self.__doc__==b.__doc__) and (self.tag==b.tag)
                and (self.trailing_modifiers==b.trailing_modifiers))
        
    def __hash__(self):
        return (reduce(lambda x,y:x+y,(hash(z) for z in [self.__doc__,
                                                         self.value,
                                                         frozenset(self.dbxrefs),
                                                         self.scope,
                                                         frozenset(self.types),
                                                         self.tag,
                                                         self.trailing_modifiers]),0)) % (2**31)
        
        
class XrefValue(TaggedValue):
    '''
       A couple 'xref:value' inherited from the class TaggedValue. Used to manage 
       xref tags.
    ''' 
    
    def __init__(self,line):
        
        ## use of the TaggedValue constructor
        TaggedValue.__init__(self, line)
        
        ## use the same function as the dbxrefs
        self.value=xrefFactory(self.value)
        
        if self.tag in ('xref_analog','xref_unk'):
            raise DeprecationWarning,'%s is a deprecated tag use instead sysnonym tag' % self.tag
            self.tag='xref'
        
        ## this is our own constraint. deprecated tags are not saved by this parser.    
        assert self.tag=='xref'
        
        
class RelationshipValue(TaggedValue):
    '''
       A couple 'xref:value' inherited from the class TaggedValue. Used to manage 
       xref tags.
    ''' 
    
    def __init__(self,line):
        
        ## use of the TaggedValue constructor
        TaggedValue.__init__(self, line)
        
        ## the value is split on the first ' '.
        value = self.value.split(None,1)
        
        ## succesful split !
        if len(value)==2:
            relationship=value[0]
            term=value[1]
        ## unsuccesful split. The relationship is set by default to IS_A
        else:
            relationship='is_a'
            term=value[0]
        
        ## recording zone    
        self.value=term
        self.relationship=relationship
        
        
class NamespaceValue(TaggedValue):
    def __init__(self,line):
        TaggedValue.__init__(self, line)
        
class RemarkValue(TaggedValue):
    def __init__(self,line):
        TaggedValue.__init__(self, line)
#        label,value = self.value.split(':',1)
#        label = label.strip()
#        value = value.strip()
#        self.value=value
#        self.label=label
    
    
def taggedValueFactory(line):
    '''
    A function used to dispatch lines of an OBOEntry between the class TaggedValue
    and its inherited classes.
    
    @param line: a line of an OBOEntry composed of a tag and a value.
    @type line: string
    
    @return: a class object
    '''
    
    if (line[0:9]=='namespace' or
          line[0:17]=='default-namespace'):
        return NamespaceValue(line)
    ## DefValue is an inherited class of TaggedValue
    elif line[0:3]=='def':
        return DefValue(line)
    ## SynonymValue is an inherited class of TaggedValue
    elif ((line[0:7]=="synonym" and line[0:14]!="synonymtypedef") or
          line[0:13]=="exact_synonym" or
          line[0:13]=="broad_synonym" or
          line[0:14]=="narrow_synonym"):
        return SynonymValue(line)
    ## XrefValue is an inherited class of TaggedValue
    elif line[0:4]=='xref':
        return XrefValue(line)
    ## NameValue is an inherited class of TaggedValue
    elif line[0:4]=='name':
        return NameValue(line)
    ## RelationshipValue is an inherited class of TaggedValue
    elif (line[0:15]=='intersection_of' or
          line[0:8] =='union_of' or
          line[0:12]=='relationship'):
        return RelationshipValue(line)
    elif (line[0:6]=='remark'):
        return RemarkValue(line)
    ## each line is a couple : tag / value (and some more features)
    else:
        return TaggedValue(line)


#################################################################################
##                               Xref treatment area                           ##
#################################################################################

    
    
class Xref(object):
    '''
       A xref object of an OBOentry. It may be the 'dbxrefs' of SynonymValue and 
       DefValue objects or the 'value' of XrefValue objects.
    '''
    
    __splitdata__ = re.compile(' +(?=["{])')
    
    def __init__(self,ref):
        if ref == '' :                    #
            ref  = None                   #
            data = ''                     #
        else :                            # Modifs JJ sinon erreur : list index out of range
            data = Xref.__splitdata__.split(ref,1)      #
            ref  = data[0]                #
        description=None
        trailing_modifiers = None
        if len(data)> 1:
            extra = data[1]
            description = TaggedValue._match_quotedString.search(extra)
            if description is not None:
                description = description.group(0)
                extra.replace(description,'')
            trailing_modifiers=trailingModifierFactory(extra)
        self.reference=ref
        self.description=description
        self.trailing_modifiers=trailing_modifiers
        
    def __eq__(self,b):
        return ((self.reference==b.reference) and (self.description==b.description) 
                and (self.trailing_modifiers==b.trailing_modifiers))
        
    def __hash__(self):
        return (reduce(lambda x,y:x+y,(hash(z) for z in [self.reference,
                                                         self.description,
                                                         self.trailing_modifiers]),0)) % (2**31)
        
        
def xrefFactory(string):
    '''
    Dispatcher of xrefs.
    
    @param string: a string (between brackets) from an inherited TaggedValue object with a dbxrefs 
                   signal (actually, the signal can only be found into SynonymValue and DefValue 
                   objects) or a string (without brackets) from a XrefValue object.
    @type string: string
    
    @return: a class object
    
    @note: The dispatcher treats differently the strings between brackets (from SynonymValue and 
    DefValue objects) and without brackets (from XrefValue objects).
    '''
    
    string = string.strip()
    if string[0]=='[':
        return [Xref(x.strip()) for x in string[1:-1].split(',')]  
    else:
        return Xref(string)
    

#################################################################################
##                              Stanza treatment area                          ##
#################################################################################
                
                
class OBOEntry(dict):
    '''
       An entry of an OBOFile. It can be a header (without a stanza name) or
       a stanza (with a stanza name between brackets). It inherits from the class dict.
    '''
    _match_stanza_name = re.compile('(?<=^\[)[^\]]*(?=\])')
    
    def __init__(self,stanza):
        ## tests if it is the header of the OBO file (returns TRUE) or not (returns FALSE)
        self.isHeader = stanza[0]!='['
        lines = stanza.split('\n')
        ## not the header : there is a [stanzaName]
        if not self.isHeader:
            self.stanzaName = lines[0].strip()[1:-1]
            lines=lines[1:]
        ## whatever the stanza is. 
        for line in lines:
            ## each line is a couple : tag / value
            taggedvalue = taggedValueFactory(line)
            if taggedvalue.tag in self:
                self[taggedvalue.tag].append(taggedvalue)
            else:
                self[taggedvalue.tag]=[taggedvalue]
    
        
    def parseStanzaName(stanza):
        sm = OBOEntry._match_stanza_name.search(stanza)
        if sm:
            return sm.group(0)
        else:
            return None
        
    parseStanzaName=staticmethod(parseStanzaName)           
        
        
    
class OBOTerm(OBOEntry):
    '''
       A stanza named 'Term'. It inherits from the class OBOEntry.
    '''
    def __init__(self,stanza):
        
        ## use of the OBOEntry constructor.
        OBOEntry.__init__(self, stanza)
        
        assert self.stanzaName=='Term'
        assert 'id' in self and len(self['id'])==1,"An OBOTerm must have an id"
        assert 'name' in self and len(self['name'])==1,"An OBOTerm must have a name"
        assert 'namespace' not in self or len(self['namespace'])==1, "Only one namespace is allowed for an OBO term"
        
        assert 'def' not in self or len(self['def'])==1,"Only one definition is allowed for an OBO term"
        assert 'comment' not in self or len(self['comment'])==1,"Only one comment is allowed for an OBO term"

        assert 'union_of' not in self or len(self['union_of'])>=2,"Only one union relationship is allowed for an OBO term"
        assert 'intersection_of' not in self or len(self['intersection_of'])>=2,"Only one intersection relationship is allowed for an OBO term"

        if self._isObsolete():
            assert 'is_a' not in self
            assert 'relationship' not in self
            assert 'inverse_of' not in self
            assert 'disjoint_from' not in self
            assert 'union_of' not in self
            assert 'intersection_of' not in self
            
        assert 'replaced_by' not in self or self._isObsolete()
        assert 'consider' not in self or self._isObsolete()
    
    ## make-up functions.            
    def _getDefinition(self):
        if 'def' in self:
            return self['def'][0]
        return None
    
    def _getId(self):
        return self['id'][0]
    
    def _getNamespace(self):
        return self['namespace'][0]
    
    def _getName(self):
        return self['name'][0]
    
    def _getComment(self):
        if 'comment' in self:
            return self['comment'][0]
        return None

    def _getAltIds(self):
        if 'alt_id' in self:
            return list(set(self.get('alt_id',None)))
        return None
        
    def _getIsA(self):
        if 'is_a' in self:
            return list(set(self.get('is_a',None)))
        return None
    
    def _getSynonym(self):
        if 'synonym' in self :
            return list(set(self.get('synonym',None)))
        return None
        
    def _getSubset(self):
        if self.get('subset',None) != None:
            return list(set(self.get('subset',None)))
        else:
            return None
        
    def _getXref(self):
        if 'xref' in self:
            return list(set(self.get('xref',None)))
        return None
    
    def _getRelationShip(self):
        if 'relationship' in self:
            return list(set(self.get('relationship',None)))
        return None
            
    def _getUnion(self):
        return list(set(self.get('union_of',None)))

    def _getIntersection(self):
        return list(set(self.get('intersection_of',None)))
        
    def _getDisjonction(self):
        return list(set(self.get('disjoint_from',None)))
    
    def _isObsolete(self):
        return 'is_obsolete' in self and str(self['is_obsolete'][0])=='true'
    
    def _getReplaceBy(self):
        if 'replaced_by' in self:
            return list(set(self.get('replaced_by',None)))
        return None
    
    def _getConsider(self):
        if 'consider' in self:
            return list(set(self.get('consider',None)))
        return None

    ## automatically make-up !
    definition         = property(_getDefinition,None,None)
    id                 = property(_getId,None,None) 
    namespace          = property(_getNamespace,None,None)
    name               = property(_getName,None,None) 
    comment            = property(_getComment,None,None)
    alt_ids            = property(_getAltIds,None,None)
    is_a               = property(_getIsA,None,None)
    synonyms           = property(_getSynonym,None,None)
    subsets            = property(_getSubset,None,None)
    xrefs              = property(_getXref,None,None)
    relationship       = property(_getRelationShip,None,None)
    union_of           = property(_getUnion,None,None)
    intersection_of    = property(_getIntersection,None,None)
    disjoint_from      = property(_getDisjonction,None,None)
    is_obsolete        = property(_isObsolete,None,None)
    replaced_by         = property(_getReplaceBy,None,None)
    consider           = property(_getConsider,None,None)      
    
            
def OBOEntryFactory(stanza):
    '''
    Dispatcher of stanza.
    
    @param stanza: a stanza composed of several lines.
    @type stanza: text
    
    @return: an C{OBOTerm} | C{OBOEntry} instance
    
    @note: The dispatcher treats differently the stanza which are OBO "Term"
    and the others.
    '''
    
    stanzaType = OBOEntry.parseStanzaName(stanza)
    
    if stanzaType=="Term":
        return OBOTerm(stanza)
    else:
        return OBOEntry(stanza)
    
def OBOEntryIterator(file):
    entries =  stanzaIterator(file)
    for e in entries:
        debug(e)
        yield OBOEntryFactory(e)
        
        
