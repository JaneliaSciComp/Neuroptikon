import re
from obitools.word import wordDist

def rePredicatGenerator(regex):
    regex = re.compile(regex,re.I)
    def predicat(w):
        return bool(regex.search(w))
    return predicat

def gcUpperBondGenerator(count):
    def predicat(w):
        c = w.count('g')+w.count('c')
        return c <= count
    return predicat

def homoPolymerGenerator(count):
    pattern = '(.)' + '\\1' * (count -1)
    return rePredicatGenerator(pattern)

def distMinGenerator(word,dmin):
    def predicat(w):
        return w==word or wordDist(w, word) >= dmin 
    return predicat