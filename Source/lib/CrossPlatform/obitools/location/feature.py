from obitools.location import Location,locationGenerator
import logging
import sys
import re


        
        
_featureMatcher = re.compile('^(FT|  )   [^ ].+\n((FT|  )    .+\n)+',re.M)
_featureCleaner = re.compile('^FT',re.M)


def textFeatureIterator(fttable):
    '''
    Iterate through a textual description of a feature table in a genbank
    or embl format. Return at each step a text representation of each individual
    feature composing the table.
    
    @param fttable:  a string corresponding to the feature table of a genbank
                     or an embl entry
                      
    @type fttable: C{str}
    
    @return: an iterator on str
    @rtype: iterator
    
    @see: L{ftParser}
    '''
    for m in _featureMatcher.finditer(fttable):
        t = m.group()
        t = _featureCleaner.sub('  ',t)
        yield t
        
_qualifierMatcher = re.compile('(?<=^ {21}/).+(\n {21}[^/].+)*',re.M)
_qualifierCleanner= re.compile("^ +",re.M)
        
def qualifierIterator(qualifiers):
    '''
    Parse a textual description of a feature in embl or genbank format
    as returned by the textFeatureIterator iterator and iterate through 
    the key, value qualified defining this location.
     
    @param qualifiers: substring containing qualifiers
    @type qualifiers: str
    
    @return: an iterator on tuple (key,value), where keys are C{str}
    @rtype: iterator
    '''
    for m in _qualifierMatcher.finditer(qualifiers):
        t = m.group()
        t = _qualifierCleanner.sub('',t)
        t = t.split('=',1)
        if len(t)==1:
            t = (t[0],None)
        else:
            if t[0]=='translation':
                value = t[1].replace('\n','')
            else:
                value = t[1].replace('\n',' ')
            try:
                value = eval(value)
            except:
                pass
            t = (t[0],value)
        yield t
    
     
_ftmatcher = re.compile('(?<=^ {5})\S+')
_locmatcher= re.compile('(?<=^.{21})[^/]+',re.DOTALL)
_cleanloc  = re.compile('[\s\n]+')
_qualifiersMatcher = re.compile('^ +/.+',re.M+re.DOTALL)

def ftParser(feature):
    fttype = _ftmatcher.search(feature).group()
    location=_locmatcher.search(feature).group()
    location=_cleanloc.sub('',location)
    qualifiers=_qualifiersMatcher.search(feature)
    if qualifiers is not None:
        qualifiers=qualifiers.group()
    else:
        qualifiers=""
        logging.debug("Qualifiers regex not matching on \n=====\n%s\n========" % feature)
        
    return fttype,location,qualifiers


class Feature(dict,Location):
    def __init__(self,type,location):
        self._fttype=type
        self._loc=location

    def getFttype(self):
        return self._fttype

        
    def extractSequence(self,sequence,withQualifier=False):
        seq = self._loc.extractSequence(sequence)
        if withQualifier:
            seq.getInfo().update(self)
        return seq
    
    def isDirect(self):
        return self._loc.isDirect()

    def isSimple(self):
        return self._loc.isSimple()
    
    def isFullLength(self):
        return self._loc.isFullLength()

    def simplify(self):
        f = Feature(self._fttype,self._loc.simplify())
        f.update(self)
        return f
    
    def locStr(self):
        return str(self._loc)
    
    def needNucleic(self):
        return self._loc.needNucleic()
    
    def __str__(self):
        return repr(self)
    
    def __repr__(self):
        return str((self.ftType,str(self._loc),dict.__repr__(self)))
    
    def __cmp__(self,y):
        return self._loc.__cmp__(y)
    
    def _getglocpos(self):
        return self._loc._getglocpos()

    ftType = property(getFttype, None, None, "Feature type name")

    def shift(self,s):
        assert (self.getBegin() + s) > 0,"shift to large (%d)" % s 
        if s == 0:
            return self
        f = Feature(self._fttype,self._loc.shift(s))
        f.update(self)
        return f

    
    def getBegin(self):
        return self._loc.getBegin()
    
    def getEnd(self):
        return self._loc.getEnd()
    
    begin = property(getBegin,None,None,"beginning position of the location")
    end = property(getEnd,None,None,"ending position of the location")
    

def featureFactory(featureDescription):
    fttype,location,qualifiers = ftParser(featureDescription)
    location = locationGenerator(location)
    feature = Feature(fttype,location)
    feature.raw  = featureDescription

    for k,v in qualifierIterator(qualifiers):
        feature.setdefault(k,[]).append(v)
        
    return feature
        
def featureIterator(featureTable,skipError=False):
    for tft in textFeatureIterator(featureTable):
        try:
            feature = featureFactory(tft)
        except AssertionError,e:
            logging.debug("Parsing error on feature :\n===============\n%s\n===============" % tft)
            if not skipError:
                raise e
            logging.debug("\t===> Error skipped")
            continue
            
        yield feature
        