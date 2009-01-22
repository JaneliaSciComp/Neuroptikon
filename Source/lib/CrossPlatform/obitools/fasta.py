"""
fasta module provides functions to read and write sequences in fasta format.


"""

from obitools.format.genericparser import genericEntryIteratorGenerator
from obitools import bioSeqGenerator,BioSequence,AASequence,NucSequence
from obitools.align import alignmentReader
from obitools.utils import universalOpen
import re

_parseFastaTag=re.compile('([a-zA-Z]\w*) *= *([^;]+);')

fastaEntryIterator=genericEntryIteratorGenerator(startEntry='^>')


def parseFastaDescription(ds,tagparser=_parseFastaTag):
    info = dict((x[0],x[1].strip()) 
                for x in tagparser.findall(ds))
    definition = tagparser.sub('',ds).strip()    
    for k in info:
        try:
            info[k]=eval(info[k])
        except:
            pass

    return definition,info

def _fastaJoinSeq(seqarray):
    return  ''.join([x.strip() for x in seqarray])

def fastaParser(seq,bioseqfactory,tagparser=_parseFastaTag,joinseq=_fastaJoinSeq):
    '''
    Parse a fasta record.
    
    @attention: internal purpuse function
    
    @param seq: a sequence object containing all lines corresponding
                to one fasta sequence
    @type seq: C{list} or C{tuple} of C{str}
    
    @param bioseqfactory: a callable object return a BioSequence
                          instance.
    @type bioseqfactory: a callable object
    
    @param tagparser: a compiled regular expression usable
                      to identify key, value couples from 
                      title line.
    @type tagparser: regex instance
    
    @return: a C{BioSequence} instance   
    '''
    seq = seq.split('\n')
    title = seq[0].strip()[1:].split(None,1)
    id=title[0]
    if len(title) == 2:
        definition,info=parseFastaDescription(title[1], tagparser)
    else:
        info= {}
        definition=None

    seq=joinseq(seq[1:])
    return bioseqfactory(id, seq, definition,**info)

def fastaNucParser(seq,tagparser=_parseFastaTag,joinseq=_fastaJoinSeq):
    return fastaParser(seq,NucSequence,tagparser=_parseFastaTag,joinseq=_fastaJoinSeq)

def fastaAAParser(seq,tagparser=_parseFastaTag,joinseq=_fastaJoinSeq):
    return fastaParser(seq,AASequence,tagparser=_parseFastaTag,joinseq=_fastaJoinSeq)

def fastaIterator(file,bioseqfactory=bioSeqGenerator,tagparser=_parseFastaTag,joinseq=_fastaJoinSeq):
    '''
    iterate through a fasta file sequence by sequence.
    Returned sequences by this iterator will be BioSequence
    instances

    @param file: a line iterator containing fasta data or a filename
    @type file:  an iterable object or str
    @param bioseqfactory: a callable object return a BioSequence
                          instance.
    @type bioseqfactory: a callable object

    @param tagparser: a compiled regular expression usable
                      to identify key, value couples from 
                      title line.
    @type tagparser: regex instance
    
    @return: an iterator on C{BioSequence} instance
 
    @see: L{fastaNucIterator}
    @see: L{fastaAAIterator}

    '''

    for entry in fastaEntryIterator(file):
        yield fastaParser(entry,bioseqfactory,tagparser,joinseq)

def fastaNucIterator(file,tagparser=_parseFastaTag):
    '''
    iterate through a fasta file sequence by sequence.
    Returned sequences by this iterator will be NucSequence
    instances
    
    @param file: a line iterator containint fasta data
    @type file: an iterable object

    @param tagparser: a compiled regular expression usable
                      to identify key, value couples from 
                      title line.
    @type tagparser: regex instance
    
    @return: an iterator on C{NucBioSequence} instance
    
    @see: L{fastaIterator}
    @see: L{fastaAAIterator}
    '''
    return fastaIterator(file, NucSequence,tagparser)

def fastaAAIterator(file,tagparser=_parseFastaTag):
    '''
    iterate through a fasta file sequence by sequence.
    Returned sequences by this iterator will be AASequence
    instances
    
    @param file: a line iterator containing fasta data
    @type file: an iterable object
    
    @param tagparser: a compiled regular expression usable
                      to identify key, value couples from 
                      title line.
    @type tagparser: regex instance
    
    @return: an iterator on C{AABioSequence} instance

    @see: L{fastaIterator}
    @see: L{fastaNucIterator}
    '''
    return fastaIterator(file, AASequence,tagparser)

def formatFasta(data,gbmode=False):
    '''
    Convert a seqence or a set of sequences in a
    string following the fasta format
    
    @param data: sequence or a set of sequences
    @type data: BioSequence instance or an iterable object 
                on BioSequence instances
                
    @param gbmode: if set to C{True} identifier part of the title
                   line follows recommendation from nbci to allow
                   sequence indexing with the blast formatdb command.
    @type gbmode: bool
                
    @return: a fasta formated string
    @rtype: str
    '''
    if isinstance(data, BioSequence):
        data = [data]
    rep = []
    for sequence in data:
        seq = str(sequence)
        if sequence.definition is None:
            definition=''
        else:
            definition=sequence.definition
        frgseq = '\n'.join([seq[x:x+60] for x in xrange(0,len(seq),60)])
        info='; '.join(['%s=%s' % x for x in sequence._info.items()])
        if info:
            info=info+';'
        id = sequence.id
        if gbmode:
            if 'gi' in sequence:
                id = "gi|%s|%s" % (sequence['gi'],id)
            else:
                id = "lcl|%s|" % (id)
        title='>%s %s %s' %(id,info,definition)
        rep.append("%s\n%s" % (title,frgseq))
    return '\n'.join(rep)
