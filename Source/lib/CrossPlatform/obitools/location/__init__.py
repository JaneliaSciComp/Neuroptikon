from obitools.sequenceencoder import Complement
import obitools
import re

class Location(object):
    """
    Define a location on a sequence.  
    """
    
    def extractSequence(self,sequence):
        '''
        Extract subsequence corresponding to a Location.
        
        @param sequence: 
        @type sequence: C{BioSequence} or C{str}
        '''
        assert isinstance(sequence, (obitools.BioSequence,str)), \
           "sequence must be an instance of str or BioSequence"
           
        if isinstance(sequence, str):
            seq = self._extractSequence(sequence)
        else:
            if isinstance(sequence, obitools.AASequence):
                assert not self.needNucleic(), \
                    "This location can be used only with Nucleic sequences"
            seq = self._extractSequence(str(sequence))
            
            if isinstance(sequence, obitools.AASequence):
                st = obitools.AASequence
            else:
                st = obitools.NucSequence
            
            seq = st(sequence.id,
                     seq,
                     sequence.definition,
                     **sequence.getTags())
            seq['location']=str(self)
            
            if 'length' in  sequence.getTags():
                seq['length']=len(seq)
                
        return seq

    def isDirect(self):
        return None

    def isSimple(self):
        '''
        Indicate if a location is composed of a single continuous 
        region or is composed by the junction of several locations
        by the C{join} operator.
        
        @return: C{True} if the location is composed of a single
                 continuous region.
        @rtype: bool
        '''
        
        return None
    
    def isFullLength(self):
        return None
    
    def needNucleic(self):
        '''
        If a location contains a complement operator, it can be use
        only on nucleic sequence.
        
        @return: C{True} if location contains a complement operator
        @rtype: bool
        '''
        return None
    
    def getGloc(self):
        loc = self.simplify()
        assert loc.isDirect() is not None,"Gloc cannot be created for multi oriented location : %s" % str(loc)
        positions = ','.join([str(x) for x in loc._getglocpos()])
        return "(%s,%s)" % ({True:'T',False:'F'}[loc.isDirect()],
                            positions)

    def shift(self,s):
        return None
    
    def getBegin(self):
        return None
    
    def getEnd(self):
        return None
    
    def getFivePrime(self):
        return self.getBegin()
    
    def getThreePrime(self):
        return self.getEnd()
    
    begin = property(getBegin,None,None,"beginning position of the location")
    end = property(getEnd,None,None,"ending position of the location")
    fivePrime=property(getFivePrime,None,None,"5' potisition of the location")
    threePrime=property(getThreePrime,None,None,"3' potisition of the location")
       
    def __abs__(self):
        assert self.isDirect() is not None,"Abs operator cannot be applied on non oriented location"
        if self.isDirect():
            return self
        else:
            return ComplementLocation(self).simplify()
       
    def __cmp__(self,y):
        if self.begin < y.begin:
            return -1
        if self.begin > y.begin:
            return 1
        if self.isDirect() == y.isDirect():
            return 0
        if self.isDirect() and not y.isDirect():
            return -1
        return 1
    
class SimpleLocation(Location):
    """
    A simple location is describe a continuous region of 
    a sequence define by a C{begin} and a C{end} position.
    """
    
    def __init__(self,begin,end):
        '''
        Build a new C{SimpleLocation} instance. Valid
        position are define on M{[1,N]} with N the length
        of the sequence.
        
        @param begin: start position of the location
        @type begin:  int
        @param end:   end position of the location
        @type end:    int
        '''
        assert begin > 0 and end > 0
        
        self._begin = begin
        self._end   = end
        
    def _extractSequence(self,sequence):
        
        assert (    self._begin < len(sequence) 
                and self._end <= len(sequence)), \
                "Sequence length %d is too short" % len(sequence)
                
        return sequence[self._begin-1:self._end]
    
    def isDirect(self):
        return True
    
    def isSimple(self):
        return True
    
    def isFullLength(self):
        return not (self.before or self.after)
    
    def simplify(self):
        if self._begin == self._end:
            return PointLocation(self._begin)
        else:
            return self
    
    def needNucleic(self):
        return False

    def __str__(self):
        before = {True:'<',False:''}[self.before]
        after  = {True:'>',False:''}[self.after]
        return "%s%d..%s%d" % (before,self._begin,after,self._end)
    
    def shift(self,s):
        assert (self._begin + s) > 0,"shift to large (%d)" % s 
        if s == 0:
            return self
        return SimpleLocation(self._begin + s, self._end + s)

    def _getglocpos(self):
        return (self.begin,self.end)
    
    def getGloc(self):
        positions = ','.join([str(x) for x in self._getglocpos()])
        return "(%s,%s)" % ({True:'T',False:'F'}[self.isDirect()],
                            positions)
    
    def getBegin(self):
        return self._begin
    
    def getEnd(self):
        return self._end
    
    
    begin = property(getBegin,None,None,"beginning position of the location")
    end = property(getEnd,None,None,"ending position of the location")
    
class PointLocation(Location):
    """
    A point location describes a location on a sequence
    limited to a single position
    """
    
    def __init__(self,position):
        assert position > 0
        self._pos=position
    
    def _extractSequence(self,sequence):
        
        assert self._end <= len(sequence), \
                "Sequence length %d is too short" % len(sequence)
                
        return sequence[self._pos-1]

    def isDirect(self):
        return True

    def isSimple(self):
        return True
    
    def isFullLength(self):
        return True

    def simplify(self):
        return self
    
    def needNucleic(self):
        return False

    def shift(self,s):
        assert (self._pos + s) > 0,"shift to large (%d)" % s 
        if s == 0:
            return self
        return PointLocation(self._pos + s)

    def _getglocpos(self):
        return (self._pos,self._pos)
    
    def getBegin(self):
        return self._pos
    
    def getEnd(self):
        return self._pos
    
    begin = property(getBegin,None,None,"beginning position of the location")
    end = property(getEnd,None,None,"ending position of the location")

    def __str__(self):
        return str(self._pos)
    
class CompositeLocation(Location):
    """
    """
    def __init__(self,locations):            
        self._locs = tuple(locations)
        
        
    def _extractSequence(self,sequence):
        seq = ''.join([x._extractSequence(sequence)
                       for x in self._locs])
        return seq
    
    def isDirect(self):
        hasDirect,hasReverse = reduce(lambda x,y: (x[0] or y,x[1] or not y),
                            (z.isDirect() for z in self._locs),(False,False))
        
        if hasDirect and not hasReverse:
            return True
        if hasReverse and not hasDirect:
            return False
        
        return None


    def isSimple(self):
        return False
    
    
    def simplify(self):
        if len(self._locs)==1:
            return self._locs[0]
        
        rep = CompositeLocation(x.simplify() for x in self._locs)
        
        if reduce(lambda x,y : x and y,
                      (isinstance(z, ComplementLocation) 
                       for z in self._locs)):
            rep = ComplementLocation(CompositeLocation(x._loc.simplify() 
                                                       for x in rep._locs[::-1]))
            
        return rep

    def isFullLength(self):
        return reduce(lambda x,y : x and y, (z.isFullLength() for z in self._locs),1)

    def needNucleic(self):
        return reduce(lambda x,y : x or y, 
                      (z.needNucleic for z in self._locs),
                      False)

    def _getglocpos(self):
        return reduce(lambda x,y : x + y,
                      (z._getglocpos() for z in self._locs))


    def getBegin(self):
        return min(x.getBegin() for x in self._locs)
    
    def getEnd(self):
        return max(x.getEnd() for x in self._locs)
    
    def shift(self,s):
        assert (self.getBegin() + s) > 0,"shift to large (%d)" % s 
        if s == 0:
            return self
        return CompositeLocation(x.shift(s) for x in self._locs)

    
    begin = property(getBegin,None,None,"beginning position of the location")
    end = property(getEnd,None,None,"ending position of the location")

   
    def __str__(self):
        return "join(%s)" % ','.join([str(x) 
                                      for x in self._locs])
    
class ComplementLocation(Location):
    """
    """
    
    def __init__(self,location):
        self._loc = location
        
    def _extractSequence(self,sequence):
        seq = self._loc._extractSequence(sequence)
        seq = Complement.encode(seq)
        return seq
    
    def isDirect(self):
        return False
    
    def isSimple(self):
        return self._loc.isSimple()

    def isFullLength(self):
        return self._loc.isFullLength()
    
    def simplify(self):
        if isinstance(self._loc, ComplementLocation):
            return self._loc._loc.simplify()
        else:
            return self

    def needNucleic(self):
        return True

    def __str__(self):
        return "complement(%s)" % self._loc
    
    def shift(self,s):
        assert (self.getBegin() + s) > 0,"shift to large (%d)" % s 
        if s == 0:
            return self
        return ComplementLocation(self._loc.shift(s))

    def _getglocpos(self):
        return self._loc._getglocpos()

    def getBegin(self):
        return self._loc.getBegin()
    
    def getEnd(self):
        return self._loc.getEnd()

    def getFivePrime(self):
        return self.getEnd()
    
    def getThreePrime(self):
        return self.getBegin()
    
    
    begin = property(getBegin,None,None,"beginning position of the location")
    end = property(getEnd,None,None,"ending position of the location")
    fivePrime=property(getFivePrime,None,None,"5' potisition of the location")
    threePrime=property(getThreePrime,None,None,"3' potisition of the location")

    
                                    #
                                    # Internal functions used for location parsing
                                    #
    
def __sublocationIterator(text):
    sl = []
    plevel=0
    for c in text:
        assert plevel>=0,"Misformated location : %s" % text
        if c == '(':
            plevel+=1
            sl.append(c)
        elif c==')':
            plevel-=1
            sl.append(c)
        elif c==',' and plevel == 0:
            assert sl,"Misformated location : %s" % text
            yield ''.join(sl)
            sl=[]
        else:
            sl.append(c)
    assert sl and plevel==0,"Misformated location : %s" % text
    yield ''.join(sl)
    

    
                                    #
                                    # Internal functions used for location parsing
                                    #

__simplelocparser = re.compile('(?P<before><?)(?P<from>[0-9]+)(\.\.(?P<after>>?)(?P<to>[0-9]+))?')

    
def __locationParser(text):
    text=text.strip()
    if text[0:5]=='join(':
        assert text[-1]==')',"Misformated location : %s" % text
        return CompositeLocation(__locationParser(sl) for sl in __sublocationIterator(text[5:-1]))
    elif text[0:11]=='complement(':
        assert text[-1]==')',"Misformated location : %s" % text
        subl = tuple(__locationParser(sl) for sl in __sublocationIterator(text[11:-1]))
        if len(subl)>1:
            subl = CompositeLocation(subl)
        else:
            subl = subl[0]
        return ComplementLocation(subl)
    else:
        data = __simplelocparser.match(text)
        assert data is not None,"Misformated location : %s" % text
        data = data.groupdict()
        if not data['to'] :
            sl = PointLocation(int(data['from']))
        else:
            sl = SimpleLocation(int(data['from']),int(data['to']))
        sl.before=data['before']=='<'
        sl.after=data['after']=='>'
        return sl
            
def locationGenerator(locstring):
    '''
    Parse a location string as present in genbank or embl file.
    
    @param locstring: string description of the location in embl/gb format
    @type locstring: str
    
    @return: a Location instance
    @rtype: C{Location} subclass instance
    '''
    return __locationParser(locstring)


_matchExternalRef = re.compile('[A-Za-z0-9_|]+(\.[0-9]+)?(?=:)')

def extractExternalRefs(locstring):
    '''
    When a location describe external references (ex: D28156.1:1..>1292)
    separate the external reference part of the location and the location
    by itself.
    
    @param locstring: text representation of the location.
    @type locstring: str
    
    @return: a tuple with a set of string describing accession number
             of the referred sequences and a C{Location} instance.
            
    @rtype: tuple(set,Location)
    '''
    m = set(x.group() for x in _matchExternalRef.finditer(locstring))
    clean = re.compile(':|'.join([re.escape(x) for x in m])+':')
    cloc = locationGenerator(clean.sub('',locstring))
        
    return m,cloc


    
    
    
