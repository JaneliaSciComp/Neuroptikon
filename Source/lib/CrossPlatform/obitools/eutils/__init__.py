import time
from urllib2 import urlopen
import shelve
from threading import Lock
import sys

class EUtils(object):
    '''
    
    '''

    _last_request=0
    _interval=3
    
    def __init__(self):
        self._lock = Lock()
    
    def wait(self):
        now=time.time() 
        delta = now - EUtils._last_request
        while delta < EUtils._interval:
            time.sleep(delta)
            now=time.time() 
            delta = now - EUtils._last_request
        
    def _sendRequest(self,url):
        self.wait()
        EUtils._last_request=time.time()
        t = EUtils._last_request
        print >>sys.stderr,"Sending request to NCBI @ %f" % t
        data = urlopen(url).read()
        print >>sys.stderr,"Data red from NCBI @ %f (%f)" % (t,time.time()-t)
        return data
    
    def setInterval(self,seconde):
        EUtils._interval=seconde
            
    
class EFetch(EUtils):
    '''
    
    '''
    def __init__(self,db,tool='OBITools',
                 retmode='text',rettype="native",
                 server='eutils.ncbi.nlm.nih.gov'):
        EUtils.__init__(self)
        self._url = "http://%s/entrez/eutils/efetch.fcgi?db=%s&tool=%s&retmode=%s&rettype=%s"
        self._url = self._url % (server,db,tool,retmode,rettype)
        

    def get(self,**args):
        key = "&".join(['%s=%s' % x for x in args.items()])
        return self._sendRequest(self._url +"&" + key)
    
