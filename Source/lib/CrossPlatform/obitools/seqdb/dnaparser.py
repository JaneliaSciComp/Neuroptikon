from obitools.format.sequence import embl,fasta,genbank

class UnknownFormatError(Exception):
    pass

def whichParser(seq):
    if seq[0]=='>':
        return fasta.fastaNucParser
    if seq[0:2]=='ID':
        return embl.emblParser
    if seq[0:5]=='LOCUS':
        return genbank.genbankParser
    raise UnknownFormatError,"Unknown nucleic format"

def nucleicParser(seq):
    return whichParser(seq)(seq)
