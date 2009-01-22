from obitools.format.genericparser import GenericParser
from obitools.utils import universalOpen
from obitools.fasta import parseFastaDescription
from obitools import NucSequence

from itertools import imap

import sys

_contigIterator=GenericParser('^CO ')

_contigIterator.addParseAction('AF', '\nAF +(\S+) +([UC]) +(-?[0-9]+)')
_contigIterator.addParseAction('RD', '\nRD +(\S+) +([0-9]+) +([0-9]+) +([0-9]+) *\n([A-Za-z\n*]+?)\n\n')
_contigIterator.addParseAction('DS', '\nDS +(.+)')
_contigIterator.addParseAction('CO',  '^CO (\S+)')

def contigIterator(file):
    file = universalOpen(file)
    for entry in _contigIterator(file):
        contig=[]
        for rd,ds,af in map(None,entry['RD'],entry['DS'],entry['AF']):
            id = rd[0]
            shift = int(af[2])
            if shift < 0:
                print >> sys.stderr,"Sequence %s in contig %s has a negative paddng value %d : skipped" % (id,entry['CO'][0],shift)
                #continue
                
            definition,info = parseFastaDescription(ds)
            info['shift']=shift
            seq = rd[4].replace('\n','').replace('*','-').strip()
            contig.append(NucSequence(id,seq,definition,**info))
          
        maxlen = max(len(x)+x['shift'] for x in contig)
        minshift=min(x['shift'] for x in contig)
        rep = []
        
        for s in contig:
            info = s.getTags()
            info['shift']-=minshift-1
            head = '-' * (info['shift']-1)
            
            tail = (maxlen + minshift - len(s) - info['shift'] - 1)
            info['tail']=tail
            newseq = NucSequence(s.id,head + s.seq+ '-' * tail,s.definition,**info)
            rep.append(newseq) 
              
        yield entry['CO'][0],rep
    