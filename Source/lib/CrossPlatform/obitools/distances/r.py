import sys

from itertools import imap,count

def writeRMatrix(matrix):
    names = [x.id for x in matrix.aligment]
    lmax = max(max(len(x) for x in names),5)
    lali = len(matrix.aligment)
    
    nformat = '%%-%ds' % lmax
    dformat = '%%%d.4f' % lmax

    pnames=[nformat % x for x in names]

    rep = ['  '.join(pnames)]
    
    for i in xrange(lali):
        line=[]
        for j in xrange(lali):
            line.append('%5.4f' % matrix[(j,i)])
        rep.append('  '.join(line))
    return '\n'.join(rep)
        
    
            