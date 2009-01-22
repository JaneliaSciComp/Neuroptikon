import sys

from itertools import imap,count

def writePhylipMatrix(matrix):
    names = [x.id for x in matrix.aligment]
    pnames= [x[:10] for x in names]
    unicity={}
    redundent=[]
    for n in pnames:
        unicity[n]=unicity.get(n,0)+1
        redundent.append(unicity[n])

    for i,n,r in imap(None,count(),pnames,redundent):
        alternate = n
        if r > 1:
            while alternate in pnames:
                lcut = 9 - len(str(r)) 
                alternate = n[:lcut]+ '_%d' % r
                r+=1
        pnames[i]='%-10s' % alternate
        
    firstline = '%5d' % len(matrix.aligment)
    rep = [firstline]
    for i,n in imap(None,count(),pnames):
        line = [n]
        for j in xrange(i):
            line.append('%5.4f' % matrix[(j,i)])
        rep.append('  '.join(line))
    return '\n'.join(rep)
        
    
            
    
    