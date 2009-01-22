import re
import sys

from obitools.seqdb import embl
from obitools.seqdb import nucEntryIterator

_featureMatcher = re.compile('(^FT  .*\n)+', re.M)
_cleanFT       = re.compile('^FT',re.M)

_headerMatcher = re.compile('^ID.+(?=\nFH  )', re.DOTALL)
_seqMatcher    = re.compile('(^    ).+(?=//\n)', re.DOTALL + re.M)
_cleanSeq      = re.compile('[ \n0-9]+')
_acMatcher     = re.compile('(?<=^AC   ).+',re.M)
_deMatcher     = re.compile('(^DE   .+\n)+',re.M)
_cleanDe       = re.compile('(^|\n)DE +')

def __emblparser(text):
    try:
        header = _headerMatcher.search(text).group()

        ft     = _featureMatcher.search(text).group()
        ft     = _cleanFT.sub('  ',ft)
        
        seq    = _seqMatcher.search(text).group()
        seq    = _cleanSeq.sub('',seq).upper()
        
        acs    = _acMatcher.search(text).group()
        acs    = acs.split()
        ac     = acs[0]
        acs    = acs[1:]
        
        de     = _deMatcher.search(header).group()
        de     = _cleanDe.sub(' ',de).strip().strip('.')
    except AttributeError,e:
        print >>sys.stderr,'======================================================='
        print >>sys.stderr,text
        print >>sys.stderr,'======================================================='
        raise e
    
    return (ac,seq,de,header,ft,acs)

def emblParser(text):
    return embl.EmblSequence(*__emblparser(text))
    
    
def emblIterator(file):
    for e in nucEntryIterator(file):
        yield emblParser(e)
    
    