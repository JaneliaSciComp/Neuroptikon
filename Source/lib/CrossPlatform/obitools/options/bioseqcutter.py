import sys
from logging import debug

def _beginOptionCallback(options,opt,value,parser):
    def beginCutPosition(seq):
        debug("begin = %s" % value )
        return eval(value,{'sequence':seq},seq) - 1
    
    parser.values.beginCutPosition=beginCutPosition
    
def _endOptionCallback(options,opt,value,parser):
    def endCutPosition(seq):
        return eval(value,{'sequence':seq},seq)

    parser.values.endCutPosition=endCutPosition
    
    
    

def addSequenceCuttingOptions(optionManager):
    
    optionManager.add_option('-b','--begin',
                             action="callback", callback=_beginOptionCallback,
                             metavar="<PYTHON_EXPRESSION>",
                             type="string",
                             help="python expression to be evaluated in the "
                                  "sequence context. The attribute name can be "
                                  "used in the expression as variable name. "
                                  "An extra variable named 'sequence' refers "
                                  "to the sequence object itself. ")
    
    optionManager.add_option('-e','--end',
                             action="callback", callback=_endOptionCallback,
                             metavar="<PYTHON_EXPRESSION>",
                             type="string",
                             help="python expression to be evaluated in the "
                                  "sequence context. The attribute name can be "
                                  "used in the expression as variable name ."
                                  "An extra variable named 'sequence' refers"
                                  "to the sequence object itself. ")


def cutterGenerator(options):
    
    def sequenceCutter(seq):

        lseq = len(seq)
        
        if hasattr(options, 'beginCutPosition'):
            begin = int(options.beginCutPosition(seq))
        else:
            begin = 0

        if hasattr(options, 'endCutPosition'):
            end = int(options.endCutPosition(seq))
        else:
            end = lseq
            
        if begin > 0 or end < lseq:
            seq = seq[begin:end]
            seq['subsequence']="%d..%d" % (begin+1,end)

        return seq
            
    return sequenceCutter

def cutterIteratorGenerator(options):
    _cutter = cutterGenerator(options)
    
    def sequenceCutterIterator(seqIterator):
        for seq in seqIterator:
            yield _cutter(seq)
            
    return sequenceCutterIterator

    
