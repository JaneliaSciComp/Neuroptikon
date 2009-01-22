'''
Module dedicated to compute observed divergeances from
an alignment. No distance correction is applied at all
'''

from itertools import imap

from obitools.distances import DistanceMatrix

class PairewiseGapRemoval(DistanceMatrix):
    '''
    Observed divergeance matrix from an alignment.
    Gap are removed from the alignemt on a pairewise
    sequence base
    '''
    
    def evaluateDist(self,x,y):
        '''
        Compute the observed divergeance from two sequences
        of an aligment. 
        
        @attention: For performance purpose this method should 
                    be directly used. use instead the __getitem__
                    method from DistanceMatrix.
                    
        @see: L{__getitem__}
        
        @param x: number of the fisrt sequence in the aligment
        @type x: int
        @param y: umber of the second sequence in the aligment
        @type y: int
        
     
        '''
        
        seq1 = self.aligment[x]
        seq2 = self.aligment[y]
        
        diff,tot = reduce(lambda x,y: (x[0]+y,x[1]+1),
                          (z[0]!=z[1] for z in imap(None,seq1,seq2)
                           if '-' not in z),(0,0))
        return float(diff)/tot
    
    
class Pairewise(DistanceMatrix):
    '''
    Observed divergeance matrix from an alignment.
    Gap are kept from the alignemt
    '''
    
    def evaluateDist(self,x,y):
        '''
        Compute the observed divergeance from two sequences
        of an aligment.
         
        @attention: For performance purpose this method should 
                    be directly used. use instead the __getitem__
                    method from DistanceMatrix.
                    
        @see: L{__getitem__}
        
        @param x: number of the fisrt sequence in the aligment
        @type x: int
        @param y: umber of the second sequence in the aligment
        @type y: int
        
     
        '''
        
        seq1 = self.aligment[x]
        seq2 = self.aligment[y]
        
        diff,tot = reduce(lambda x,y: (x[0]+y,x[1]+1),
                          (z[0]!=z[1] for z in imap(None,seq1,seq2)),
                          (0,0))
        return float(diff)/tot
    