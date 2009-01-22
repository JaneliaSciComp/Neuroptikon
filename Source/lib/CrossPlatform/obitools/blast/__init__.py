from os import popen2
from itertools import imap,count

from obitools.table import iTableIterator,TableRow,Table,SelectionIterator
from obitools.utils import ColumnFile
from obitools.location import SimpleLocation
from obitools.fasta import formatFasta
import sys

class Blast(object):
    '''
    Run blast
    '''
    
    def __init__(self,mode,db,program='blastall',**options):
        self._mode = mode
        self._db = db
        self._program = program
        self._options = options

    def getMode(self):
        return self._mode


    def getDb(self):
        return self._db


    def getProgram(self):
        return self._program
    
    def _blastcmd(self):
        tmp = """%(program)s     \\
                    -p %(mode)s  \\
                    -d %(db)s    \\
                    -m 8         \\
                    %(options)s   \\
              """
        options = ' '.join(['-%s %s' % (x[0],str(x[1])) 
                               for x in self._options.iteritems()])
        data = {
                 'program' : self.program,
                 'db'      : self.db,
                 'mode'    : self.mode,
                 'options' : options
               }
        
        return tmp % data
    
    def __call__(self,sequence):
        '''
        Run blast with one sequence object
        @param sequence:
        @type sequence:
        '''
        cmd = self._blastcmd()
        
        (blast_in,blast_out) = popen2(cmd)
        
        print >>blast_in,formatFasta(sequence)
        blast_in.close()
        
        blast  = BlastResultIterator(blast_out)
        
        return blast
    
    mode = property(getMode, None, None, "Mode's Docstring")

    db = property(getDb, None, None, "Db's Docstring")

    program = property(getProgram, None, None, "Program's Docstring")


class NetBlast(Blast):
    '''
    Run blast on ncbi servers
    '''
    
    def __init__(self,mode,db,**options):
        '''
        
        @param mode:
        @param db:
        '''
        Blast.__init__(self, mode, db, 'blastcl3',**options)
        
        
class BlastResultIterator(iTableIterator):
    
    def __init__(self,blastoutput,query=None):
        '''
        
        @param blastoutput:
        @type blastoutput:
        '''
        self._blast = ColumnFile(blastoutput, 
                                 strip=True, 
                                 skip="#",
                                 sep="\t",
                                 types=self.types
                                 )
        self._query = query
        self._hindex = dict((k,i) for i,k in imap(None,count(),self._getHeaders()))
        
    def _getHeaders(self):
        return ('Query id','Subject id',
               '% identity','alignment length', 
               'mismatches', 'gap openings', 
               'q. start', 'q. end', 
               's. start', 's. end', 
               'e-value', 'bit score')
    
    def _getTypes(self):
        return (str,str,
                float,int,
                int,int,
                int,int,
                int,int,
                float,float)
    
    def _getRowFactory(self):
        return BlastMatch
    
    def _getSubrowFactory(self):
        return TableRow 
    
    def _getQuery(self):
        return self._query
    

    headers = property(_getHeaders,None,None)
    types   = property(_getTypes,None,None)
    rowFactory    = property(_getRowFactory,None,None)
    subrowFactory = property(_getSubrowFactory,None,None)
    query = property(_getQuery,None,None)
    
    def next(self):
        '''
        
        '''
        value = self._blast.next()
        return self.rowFactory(self,value)
        
        

class BlastResult(Table):
    '''
    Results of a blast run
    '''
    
class BlastMatch(TableRow):
    '''
    Blast high scoring pair between two sequences
    '''
    
    def getQueryLocation(self):
        l = SimpleLocation(self[6], self[7])
        return l
    
    def getSubjectLocation(self):
        l = SimpleLocation(self[8], self[9])
        return l
    
    def getSubjectSequence(self,database):
        return database[self[1]]
    
    def queryCov(self,query=None):
        '''
        Compute coverage of match on query sequence.
        
        @param query: the query sequence. Default is None.
                      In this case the query sequence associated
                      to this blast result is used.
        @type query: L{obitools.BioSequence}
        
        @return: coverage fraction 
        @rtype: float
        '''
        if query is None:
            query = self.table.query
        assert query is not None
        return float(self[7]-self[6]+1)/float(len(query))
        
    def __getitem__(self,key):
        if key=='query coverage' and self.table.query is not None:
            return self.queryCov()
        else:
            return TableRow.__getitem__(self,key)

class BlastCovMinFilter(SelectionIterator):
    
    def __init__(self,blastiterator,covmin,query=None,**conditions):
        if query is None:
            query = blastiterator.table.query
        assert query is not None
        SelectionIterator.__init__(self,blastiterator,**conditions)
        self._query = query
        self._covmin=covmin
        
    def _covMinPredicat(self,row):
        return row.queryCov(self._query)>=self._covmin
    
    def _checkCondition(self,row):
        return self._covMinPredicat(row) and SelectionIterator._checkCondition(self, row)
    
    
    