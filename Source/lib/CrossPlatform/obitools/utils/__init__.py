import sys

import time
import re
import shelve

from threading import Lock
from itertools import imap,count

import urllib2

from obitools.gzip import GzipFile
from obitools.zipfile import ZipFile


def universalOpen(file,*options):
    '''
    Open a file gziped or not.
    
    If file is a C{str} instance, file is
    concidered as a file name. In this case 
    the C{.gz} suffixe is tested to eventually
    open it a a gziped file.
    
    If file is an other kind of object, it is assumed
    that this object follow the C{file} interface 
    and it is return as is.
    
    @param file: the file to open
    @type file: C{str} or a file like object
    
    @return: an iterator on text lines.
    '''
    if isinstance(file,str):
        if urllib2.urlparse.urlparse(file)[0]=='':
            rep = open(file,*options)
        else:
            rep  = urllib2.urlopen(file)
            
        if file[-3:] == '.gz':
            rep = GzipFile(fileobj=rep)
        if file[-4:] == '.zip':
            zip = ZipFile(file=rep)
            data = zip.infolist()
            assert len(data)==1,'Only zipped file containning a single file can be open'
            name = data[0].filename
            rep = zip.open(name)
    else:
        rep = file
    return rep

def universalTell(file):
    '''
    Return the position in the file even if
    it is a gziped one.
    
    @param file: the file to check
    @type file: a C{file} like instance
    
    @return: position in the file
    @rtype:  C{int}
    '''
    if isinstance(file, GzipFile):
        file=file.myfileobj
    return file.tell()

def fileSize(file):
    '''
    Return the file size even if it is a 
    gziped one.
    
    @param file: the file to check
    @type file: a C{file} like instance
    
    @return: the size of the file
    @rtype: C{int}
    '''
    if isinstance(file, GzipFile):
        file=file.myfileobj
    pos = file.tell()
    file.seek(0,2)
    length = file.tell()
    file.seek(pos,0)
    return length

def progressBar(pos,max,reset=False,delta=[]):
    if reset:
        del delta[:]
    if not delta:
        delta.append(time.time())
        delta.append(time.time())

    delta[1]=time.time()
    elapsed = delta[1]-delta[0]
    percent = float(pos)/max * 100
    remain = time.strftime('%H:%M:%S',time.gmtime(elapsed / percent * (100-percent)))
    bar = '#' * int(percent/2)
    bar+= '|/-\\-'[pos % 5]
    bar+= ' ' * (50 - int(percent/2))
    sys.stderr.write('\r%5.1f %% |%s] remain : %s' %(percent,bar,remain))

def endLessIterator(endedlist):
    for x in endedlist:
        yield x
    while(1):
        yield endedlist[-1]
    
    
def multiLineWrapper(lineiterator):
    '''
    Aggregator of strings.
    
    @param lineiterator: a stream of strings from an opened OBO file.
    @type lineiterator: a stream of strings.
    
    @return: an aggregated stanza.
    @rtype: an iterotor on str
    
    @note: The aggregator aggregates strings from an opened OBO file.
    When the length of a string is < 2, the current stanza is over.
    '''
    
    for line in lineiterator:
        rep = [line]
        while len(line)>=2 and line[-2]=='\\':
            rep[-1]=rep[-1][0:-2]
            try:
                line = lineiterator.next()
            except StopIteration:
                raise FileFormatError
            rep.append(line)
        yield ''.join(rep)
    
    
def skipWhiteLineIterator(lineiterator):
    '''
    Curator of stanza.
    
    @param lineiterator: a stream of strings from an opened OBO file.
    @type lineiterator: a stream of strings.
    
    @return: a stream of strings without blank strings.
    @rtype: a stream strings
    
    @note: The curator skip white lines of the current stanza.
    '''
    
    for line in lineiterator:
        cleanline = line.strip()
        if cleanline:
            yield line
        else:
            print 'skipped'
    

class ColumnFile(object):
    
    def __init__(self,stream,sep=None,strip=True,types=None,skip=None):
        self._stream = universalOpen(stream)
        self._delimiter=sep
        self._strip=strip
        if types:
            self._types=[x for x in types]
            for i in xrange(len(self._types)):
                if self._types[i] is bool:
                    self._types[i]=ColumnFile.str2bool
        else:
            self._types=None
        
        self._skip = skip
        if skip is not None:
            self._lskip= len(skip)
        else:
            self._lskip= 0
            
    def str2bool(x):
        return bool(eval(x.strip()[0].upper(),{'T':True,'V':True,'F':False}))
                    
    str2bool = staticmethod(str2bool)
            
        
    def __iter__(self):
        return self
    
    def next(self):
        ligne = self._stream.next()
        if self._skip is not None:
            while ligne[0:self._lskip]==self._skip:
                ligne = self._stream.next()
        data = ligne.split(self._delimiter)
        if self._strip or self._types:
            data = [x.strip() for x in data]
        if self._types:
            it = endLessIterator(self._types)
            data = [x[1](x[0]) for x in ((y,it.next()) for y in data)]
        return data
    
    def tell(self):
        return universalTell(self._stream)

                    
class CachedDB(object):
    
    def __init__(self,cachefile,masterdb):
        self._cache = shelve.open(cachefile,'c')
        self._db = masterdb
        self._lock=Lock()
        
    def _cacheSeq(self,seq):
        self._lock.acquire()
        self._cache[seq.id]=seq
        self._lock.release()
        return seq
        
    def __getitem__(self,ac):
        if isinstance(ac,str):
            self._lock.acquire()
            if ac in self._cache:
#                print >>sys.stderr,"Use cache for %s" % ac
                data = self._cache[ac]
                self._lock.release()

            else:
                self._lock.release()
                data = self._db[ac]
                self._cacheSeq(data)
            return data
        else:
            self._lock.acquire()
            acs = [[x,self._cache.get(x,None)] for x in ac]
            self._lock.release()
            newacs = [ac for ac,cached in acs if cached is None]
            if newacs:
                newseqs = self._db[newacs]
            else:
                newseqs = iter([])
            for r in acs:
                if r[1] is None:
                    r[1]=self._cacheSeq(newseqs.next())
#                else:
#                    print >>sys.stderr,"Use cache for %s" % r[0]
            return (x[1] for x in acs)
            
