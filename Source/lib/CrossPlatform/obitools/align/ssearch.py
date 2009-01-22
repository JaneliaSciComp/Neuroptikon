import os
import re

from obitools.fasta import formatFasta

class SsearchParser(object):

    _matchQuery = re.compile("^Query:.+\n.+?>+([^ ]+)", re.MULTILINE)
    _matchLQuery = re.compile("^Query:.+\n.+?(\d+)(?= nt\n)", re.MULTILINE)
    _matchProp   = re.compile("^The best scores are:.*\n(.+?)>>>", re.DOTALL+re.MULTILINE)
    def __init__(self,file):
        if isinstance(file,str):
            file = open(file,'rU')
        self.data = file.read()
        self.query= SsearchParser._matchQuery.search(self.data).group(1)
        self.queryLength= int(SsearchParser._matchLQuery.search(self.data).group(1))
        props = SsearchParser._matchProp.search(self.data)
        if props:
            props=props.group(0).split('\n')[1:-2]
            self.props=[]
            for line in props:
                subject,tab = line.split('\t')
                tab=tab.split()
                ssp = subject.split()
                ac = ssp[0]
                dbl= int(ssp[-5][:-1])
                ident = float(tab[0])
                matchlen = int(tab[5]) - int(tab[4]) +1
                self.props.append({"ac"       :ac,
                                   "identity" :ident,
                                   "subjectlength":dbl,
                                   'matchlength' : matchlen})
                
def run(seq,database,program='fasta35',opts=''):
    ssearchin,ssearchout = os.popen2("%s %s %s" % (program,opts,database))
    print >>ssearchin,formatFasta(seq)
    ssearchin.close()
    result = SsearchParser(ssearchout)
    return seq,result

def ssearchIterator(sequenceIterator,database,program='ssearch35',opts=''):
    for seq in sequenceIterator:
        yield run(seq,database,program,opts)
    
            
