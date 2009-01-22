"""
    Module providing high level functions to manage command line options.
"""
import logging

import sys
from logging import debug

from optparse import OptionParser

from obitools.utils import universalOpen

def getOptionManager(optionDefinitions,entryIterator=None):
    '''
    Build an option manager fonction. that is able to parse
    command line options of the script.
    
    @param optionDefinitions: list of function describing a set of 
                              options. Each function must allows as
                              unique parametter an instance of OptionParser.
    @type optionDefinitions:  list of functions.
    
    @param entryIterator:     an iterator generator function returning
                              entries from the data files. 
                              
    @type entryIterator:      an iterator generator function with only one
                              parametter of type file
    '''
    parser = OptionParser()
    parser.add_option('--DEBUG',
                      action="store_true", dest="debug",
                      default=False,
                      help="Set logging in debug mode")

    parser.add_option('--no-psyco',
                      action="store_true", dest="noPsyco",
                      default=False,
                      help="Don't use psyco even if it installed")

    for f in optionDefinitions:
        f(parser)
        
    def commandLineAnalyzer():
        options,files = parser.parse_args()
        if options.debug:
            logging.root.setLevel(logging.DEBUG)
        
        i = allEntryIterator(files,entryIterator)
        return options,i
    
    return commandLineAnalyzer

_currentInputFileName=None

def currentInputFileName():
    return _currentInputFileName

def allEntryIterator(files,entryIterator):
    global _currentInputFileName
    if files :
        for f in files:
            _currentInputFileName=f
            f = universalOpen(f)
            debug(f)
            if entryIterator is None:
                for line in f:
                    yield line
            else:
                for entry in entryIterator(f):
                    yield entry
    else:
        if entryIterator is None:
            for line in sys.stdin:
                yield line
        else:
            for entry in entryIterator(sys.stdin):
                yield entry
            
            