from logging import debug,root,DEBUG



from obitools.word import wordSelector,allWordIterator
from obitools.word import predicat
import sys



def _acceptedOptionCallback(options,opt,value,parser):
    if not hasattr(parser.values, 'acceptedOligo'):
        parser.values.acceptedOligo=[]
    parser.values.acceptedOligo.append(predicat.rePredicatGenerator(value))
    
def _rejectedOptionCallback(options,opt,value,parser):
    debug(value)
    if not hasattr(parser.values, 'rejectedOligo'):
        parser.values.rejectedOligo=[]
    parser.values.rejectedOligo.append(predicat.rePredicatGenerator(value))
    


def addOligoOptions(optionManager):
    
    optionManager.add_option('-L','--oligo-list',
                             action="store", dest="oligoList",
                             metavar="<filename>",
                             type="str",
                             help="filename containing a list of oligonucleotide")

    
    optionManager.add_option('-s','--oligo-size',
                             action="store", dest="oligoSize",
                             metavar="<###>",
                             type="int",
                             help="Size of oligonucleotide to generate")

    optionManager.add_option('-f','--family-size',
                             action="store", dest="familySize",
                             metavar="<###>",
                             type="int",
                             help="Size of oligonucleotide family to generate")

    optionManager.add_option('-d','--distance',
                             action="store", dest="oligoDist",
                             metavar="<###>",
                             type="int",
                             default=1,
                             help="minimal distance between two oligonucleotides")

    optionManager.add_option('-g','--gc-max',
                             action="store", dest="gcMax",
                             metavar="<###>",
                             type="int",
                             default=0,
                             help="maximum count of G or C nucleotide acceptable in a word")

    optionManager.add_option('-a','--accepted',
                             action="callback", callback=_acceptedOptionCallback,
                             metavar="<regular pattern>",
                             type="str",
                             help="pattern of accepted oligonucleotide")

    optionManager.add_option('-r','--rejected',
                             action="callback", callback=_rejectedOptionCallback,
                             metavar="<regular pattern>",
                             type="str",
                             help="pattern of rejected oligonucleotide")

    optionManager.add_option('-p','--homopolymere',
                             action="store", dest="homopolymere",
                             metavar="<###>",
                             type="int",
                             default=0,
                             help="reject oligo with homopolymere longer than.")

    optionManager.add_option('-P','--homopolymere-min',
                             action="store", dest="homopolymere_min",
                             metavar="<###>",
                             type="int",
                             default=0,
                             help="accept only oligo with homopolymere longer than.")

def dnaWordIterator(options):
    
    assert options.oligoSize is not None or options.oligoList is not None,"option -s or --oligo-size must be specified"
    assert options.familySize is not None,"option -f or --family-size must be specified"
    assert options.oligoDist is not None,"option -d or --distance must be specified"
    
    if options.oligoList is not None:
        words = (x.strip().lower() for x in open(options.oligoList))
    else:
        words = allWordIterator(options.oligoSize)
    #seed  = 'a' * options.oligoSize
    
    if not hasattr(options, "acceptedOligo") or options.acceptedOligo is None:
        options.acceptedOligo=[]
    
    if not hasattr(options, "rejectedOligo") or options.rejectedOligo is None:
        options.rejectedOligo=[]
        
    #options.acceptedOligo.append(predicat.distMinGenerator(seed, options.oligoDist))
    
    if options.homopolymere:
        options.rejectedOligo.append(predicat.homoPolymerGenerator(options.homopolymere))
        
    if options.homopolymere_min:
        options.acceptedOligo.append(predicat.homoPolymerGenerator(options.homopolymere_min))
        
    if options.gcMax:
        options.rejectedOligo.append(predicat.gcUpperBondGenerator(options.gcMax))
    
    return wordSelector(words, options.acceptedOligo, options.rejectedOligo)
