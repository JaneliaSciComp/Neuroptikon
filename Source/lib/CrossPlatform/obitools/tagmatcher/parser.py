import re
import sys

from obitools import tagmatcher
from obitools.seqdb import nucEntryIterator
from obitools.location.feature import Feature
from obitools.location import locationGenerator

_seqMatcher    = re.compile('(?<=TG   )[acgtrymkwsbdhvnACGTRYMKWSBDHVN]+')
_cdMatcher     = re.compile('(?<=CD   ) *([^:]+?) +: +([0-9]+)')
_loMatcher     = re.compile('(?<=LO   ) *([ACGTRYMKWSBDHVN]+) +([^ ]+) +([^ ]+) +\(([0-9]+)\)')
_dmMatcher     = re.compile('(?<=DM   )[0-9]+')
_rmMatcher     = re.compile('(?<=RM   )[0-9]+')


def __tagmatcherparser(text):
    try:
        seq    = _seqMatcher.search(text).group()
        cd     = dict((x[0],int(x[1])) for x in  _cdMatcher.findall(text))
        locs = []
        
        for (match,ac,loc,err) in _loMatcher.findall(text):
            feat = Feature('location', locationGenerator(loc))
            feat['error']=int(err)
            feat['match']=match
            feat['contig']=ac
            locs.append(feat)
            
        dm = int(_dmMatcher.search(text).group())
        rm = int(_rmMatcher.search(text).group())
        
    except AttributeError,e:
        print >>sys.stderr,'======================================================='
        print >>sys.stderr,text
        print >>sys.stderr,'======================================================='
        raise e
    
    return (seq,cd,locs,dm,rm)

def tagMatcherParser(text):
    return tagmatcher.TagMatcherSequence(*__tagmatcherparser(text))
    
    
class TagMatcherIterator(object):
    _cdheadparser  = re.compile('condition [0-9]+ : (.+)') 

    def __init__(self,file):
        self._ni = nucEntryIterator(file)
        self.header=self._ni.next()
        self.conditions=TagMatcherIterator._cdheadparser.findall(self.header)
        
    def next(self):
        return tagMatcherParser(self._ni.next())
    
    def __iter__(self):
        return self
    
def formatTagMatcher(tmseq,reader=None):
    if isinstance(tmseq, TagMatcherIterator):
        return tmseq.header
    
    assert isinstance(tmseq,tagmatcher.TagMatcherSequence),'Only TagMatcherSequence can be used'
    lo = '\n'.join(['LO   %s %s %s (%d)' % (l['match'],l['contig'],l.locStr(),l['error']) 
                    for l in tmseq['locations']])     
    if reader is not None:
        cd = '\n'.join(['CD   %s : %d' % (x,tmseq['conditions'][x])
                        for x in reader.conditions])
    else:   
        cd = '\n'.join(['CD   %s : %d' % (x,tmseq['conditions'][x])
                        for x in tmseq['conditions']])
        
    tg = 'TG   %s' % str(tmseq)
    
    e=[tg]
    if cd:
        e.append(cd)
    if lo:
        e.append(lo)
    
    tm = 'TM   %d' % tmseq['tm']
    dm = 'DM   %d' % tmseq['dm']
    rm = 'RM   %d' % tmseq['rm']
    
    e.extend((tm,dm,rm,'//'))
    
    return '\n'.join(e)
         
    

