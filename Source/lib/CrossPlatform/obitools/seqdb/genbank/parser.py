import re
import sys

import obitools.seqdb.genbank as gb
from obitools.seqdb import nucEntryIterator,aaEntryIterator

_featureMatcher = re.compile('^FEATURES.+\n(?=ORIGIN)',re.DOTALL + re.M)

_headerMatcher = re.compile('^LOCUS.+(?=\nFEATURES)', re.DOTALL + re.M)
_seqMatcher    = re.compile('(?<=ORIGIN).+(?=//\n)', re.DOTALL + re.M)
_cleanSeq      = re.compile('[ \n0-9]+')
_acMatcher     = re.compile('(?<=^ACCESSION   ).+',re.M)
_deMatcher     = re.compile('(?<=^DEFINITION  ).+\n( .+\n)*',re.M)
_cleanDe       = re.compile('\n *')

def __gbparser(text):
    try:
        header = _headerMatcher.search(text).group()
        ft     = _featureMatcher.search(text).group()
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

def genbankParser(text):
    return gb.GbSequence(*__gbparser(text))
    
    
def genbankIterator(file):
    for e in nucEntryIterator(file):
        yield genbankParser(e)
    
    
def genpepParser(text):
    return gb.GpepSequence(*__gbparser(text))
    
    
def genpepIterator(file):
    for e in aaEntryIterator(file):
        yield genpepParser(e)
    
    