import threading

class TaskPool(object):
    
    def __init__(self,iterable,function,count=2):
        self.pool = []
        self.queue= []
        self.plock= threading.Lock()
        self.qlock= threading.Lock()
        self.function=function
        self.event=threading.Event()
        self.iterable=iterable
        for i in xrange(count):
            Task(self)

    def register(self,task):
        self.plock.acquire()
        self.pool.append(task)
        self.plock.release()
        self.ready(task)
        
    def unregister(self,task):
        task.thread.join()
        self.plock.acquire()
        self.pool.remove(task)
        self.plock.release()
        
        
    def ready(self,task):
        self.qlock.acquire()
        self.queue.append(task)
        self.qlock.release()
        self.event.set()
        
    def __iter__(self):
        for data in self.iterable:
            while not self.queue:
                self.event.wait()
            self.event.clear()
            self.qlock.acquire()
            task=self.queue.pop(0)
            self.qlock.release()
            if hasattr(task, 'rep'):
                yield task.rep
            #print "send ",data
            if isinstance(data,dict):
                task.submit(**data)
            else:
                task.submit(*data)
        
        while self.pool:
            self.pool[0].finish()
            while self.queue:
               self.event.clear()
               self.qlock.acquire()
               task=self.queue.pop(0)
               self.qlock.release()
               if hasattr(task, 'rep'):
                   yield task.rep
 
            
        
    

class Task(object):
    def __init__(self,pool):
        self.pool = pool
        self.lock = threading.Lock()
        self.dataOk = threading.Event()
        self.repOk = threading.Event()
        self.args = None
        self.kwargs=None
        self.stop=False
        self.thread = threading.Thread(target=self)
        self.thread.start()
        self.pool.register(self)
    
    def __call__(self):
        self.dataOk.wait()
        while(not self.stop):
            self.lock.acquire()
            self.dataOk.clear()
            self.rep=self.pool.function(*self.args,**self.kwargs)
            self.pool.ready(self)
            self.lock.release()
            self.dataOk.wait()
    
    def submit(self,*args,**kwargs):
        self.args=args
        self.kwargs=kwargs
        self.dataOk.set()
        
    def finish(self):
        self.lock.acquire()
        self.stop=True
        self.dataOk.set()
        self.pool.unregister(self)
                
   
