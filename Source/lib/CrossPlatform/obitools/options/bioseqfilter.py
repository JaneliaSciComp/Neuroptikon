import sys
import re

from obitools.options.taxonomyfilter import addTaxonomyFilterOptions
from obitools.options.taxonomyfilter import taxonomyFilterGenerator
    
def _sequenceOptionCallback(options,opt,value,parser):
    parser.values.sequencePattern = re.compile(value,re.I)
    
def _defintionOptionCallback(options,opt,value,parser):
    parser.values.definitionPattern = re.compile(value)
    
def _identifierOptionCallback(options,opt,value,parser):
    parser.values.identifierPattern = re.compile(value)
 
def _attributeOptionCallback(options,opt,value,parser):
    if not hasattr(options, 'attributePatterns'):
        options.attributePatterns={}
    attribute,pattern=value.split(':',1)
    parser.values.attributePatterns[attribute]=re.compile(pattern)

def _predicatOptionCallback(options,opt,value,parser):
    if not hasattr(options, 'predicats'):
        options.predicats=[]
    parser.values.predicats.append(value)
        
        
def addSequenceFilteringOptions(optionManager):
    
    optionManager.add_option('-s','--sequence',
                             action="callback", callback=_sequenceOptionCallback,
                             metavar="<REGULAR_PATTERN>",
                             type="string",
                             help="regular expression pattern used to select "
                                  "the sequence. The pattern is case insensitive")
    
    optionManager.add_option('-d','--definition',
                             action="callback", callback=_defintionOptionCallback,
                             type="string",
                             metavar="<REGULAR_PATTERN>",
                             help="regular expression pattern matched against "
                                  "the definition of the sequence. "
                                  "The pattern is case sensitive")
    
    optionManager.add_option('-i','--identifier',
                             action="callback", callback=_identifierOptionCallback,
                             type="string",
                             metavar="<REGULAR_PATTERN>",
                             help="regular expression pattern matched against "
                                  "the identifier of the sequence. "
                                  "The pattern is case sensitive")
    
    optionManager.add_option('-a','--attribute',
                             action="callback", callback=_defintionOptionCallback,
                             type="string",
                             metavar="<ATTRIBUTE_NAME>:<REGULAR_PATTERN>",
                             help="regular expression pattern matched against "
                                  "the attributes of the sequence. "
                                  "the value of this atribute is of the form : "
                                  "attribute_name:regular_pattern. "
                                  "The pattern is case sensitive."
                                  "Several -a option can be used on the same "
                                  "commande line.")
    
    optionManager.add_option('-A','--has-attribute',
                             action="append",
                             type="string",
                             dest="has_attribute",
                             default=[],
                             metavar="<ATTRIBUTE_NAME>",
                             help="select sequence with attribute <ATTRIBUTE_NAME> "
                                   "defined")
    
    optionManager.add_option('-p','--predicat',
                             action="append", dest="predicats",
                             metavar="<PYTHON_EXPRESSION>",
                             help="python boolean expression to be evaluated in the "
                                  "sequence context. The attribute name can be "
                                  "used in the expression as variable name ."
                                  "An extra variable named 'sequence' refers"
                                  "to the sequence object itself. "
                                  "Several -p option can be used on the same "
                                  "commande line.")
    
    optionManager.add_option('-L','--lmax',
                             action='store',
                             metavar="<##>",
                             type="int",dest="lmax",
                             help="keep sequences shorter than lmax")
                             
    optionManager.add_option('-l','--lmin',
                             action='store',
                             metavar="<##>",
                             type="int",dest="lmin",
                             help="keep sequences longer than lmin")
    
    optionManager.add_option('-v','--inverse-match',
                             action='store_true',
                             default=False,
                             dest="invertedFilter",
                             help="revert the sequence selection "
                                  "[default : %default]")
    
    addTaxonomyFilterOptions(optionManager)
    
                             
    
                             

def filterGenerator(options):
    taxfilter = taxonomyFilterGenerator(options)
    
    def sequenceFilter(seq):
        good = True
        
        if hasattr(options, 'sequencePattern'):
            good = bool(options.sequencePattern.search(str(seq)))
        
        if good and hasattr(options, 'identifierPattern'):
            good = bool(options.identifierPattern.search(seq.id))
            
        if good and hasattr(options, 'definitionPattern'):
            good = bool(options.definitionPattern.search(seq.definition))
            
        if good :
            good = reduce(lambda x,y:x and y,
                           (k in seq for k in options.has_attribute),
                           True)
            
        if good and hasattr(options, 'attributePatterns'):
            good = (reduce(lambda x,y : x and y,
                           (bool(options.attributePatterns[p].search(seq[p]))
                            for p in options.attributePatterns
                             if p in seq),True)
                    and
                    reduce(lambda x,y : x and y,
                           (bool(p in seq)
                            for p in options.attributePatterns),True)
                   )
            
        if good and hasattr(options, 'predicats') and options.predicats is not None:
            good = (reduce(lambda x,y: x and y,
                           (bool(eval(p,{'sequence':seq},seq))
                            for p in options.predicats),True)
                   )

        if good and hasattr(options, 'lmin') and options.lmin is not None:
            good = len(seq) >= options.lmin
            
        if good and hasattr(options, 'lmax') and options.lmax is not None:
            good = len(seq) <= options.lmax
        
        if good:
            good = taxfilter(seq)
            
        if hasattr(options, 'invertedFilter') and options.invertedFilter:
            good=not good
                       
        
        return good
    
    return sequenceFilter

def sequenceFilterIteratorGenerator(options):
    filter = filterGenerator(options)
    
    def sequenceFilterIterator(seqIterator):
        for seq in seqIterator:
            if filter(seq):
                yield seq
            
    return sequenceFilterIterator
    
   
    