from obitools.fasta import fastaNucIterator
from obitools.cns import cnsTag

def cnsFastaIterator(file):
    
    x = fastaNucIterator(file, cnsTag)
    
    return x