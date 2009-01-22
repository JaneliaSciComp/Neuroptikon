import threading
from logging import warning,info
from time import sleep,time

from obitools.parallel import TaskPool


class JobPool(dict):
    '''
    JobPool is dedicated to manage a job queue. These jobs
    will run in a limited number of thread. 
    '''
    
    def __init__(self,count,precision=0.01):
        '''
        
        @param count: number of thread dedicated to this JobPool
        @type count: int
        @param precision: delay between two check for new job (in second)
        @type precision: float
        '''
        self._iterator = JobIterator(self)
        self._taskPool = TaskPool(self._iterator, 
                                  self._runJob, 
                                  count)
        self._precision=precision
        self._toRun=set()
        self._runnerThread = threading.Thread(target=self._runner)
        self._runnerThread.start()
        self._finalyzed=False
        
    def _runner(self):
        for rep in self._taskPool:
            info('Job %d finnished' % id(rep))
        info('All jobs in %d JobPool finished' % id(self))
        
    def _jobIterator(self):
        return self._iterator
        
    def _runJob(self,job):
        job.started= time()
        info('Job %d started' % id(job))
        job.result = job()
        job.ended  = time()
        job.finished=True
        return job
        
    def submit(self,job,priority=1.0,userid=None):
        '''
        Submit a new job to the JobPool.
        
        @param job: the new submited job
        @type job: Job instance
        @param priority: priority level of this job (higher is better)
        @type priority: float
        @param userid: a user identifier (Default is None)
         
        @return: job identifier
        @rtype: int
        '''
        
        assert not self._finalyzed,\
          "This jobPool does not accept new job"
        if job.submitted is not None:
            warning('Job %d was already submitted' % id(job))
            return id(job)
        
        job.submitted = time()
        job.priority  = priority
        job.userid    = userid
        i=id(job)
        job.id=id
        self[i]=job
        self._toRun.add(job)
        
        info('Job %d submitted' % i)
        
        return i
        
    def finalyze(self):
        '''
        Indicate to the JobPool, that no new jobs will
        be submitted. 
        '''
        self._iterator.finalyze()
        self._finalyzed=True
        
    def __del__(self):
        self.finalyze()
        
        
class JobIterator(object):
    def __init__(self,pool):
        self._pool = pool
        self._finalyze=False
        self._nextLock=threading.Lock()
        
        
    def __iter__(self):
        return self
    
    def finalyze(self):
        '''
        Indicate to the JobIterator, that no new jobs will
        be submitted. 
        '''
        self._finalyze=True
    
    
    def next(self):
        '''
        
        @return: the next job to run       
        @rtype: Job instance
        '''
        self._nextLock.acquire()
        while self._pool._toRun or not self._finalyze:
            rep = None
            maxScore=0
            for k in self._pool._toRun:
                s = k.runScore()
                if s > maxScore:
                    maxScore=s
                    rep=k
            if rep is not None:
                self._pool._toRun.remove(rep)
                self._nextLock.release()
                return (rep,)
            sleep(self._pool._precision)
        self._nextLock.release()
        info('No more jobs in %d JobPool' % id(self._pool))
        raise StopIteration
            
        
        
class Job(object):
    
    def __init__(self,pool=None,function=None,*args,**kwargs):
        '''
        Create a new job
        
        @param pool: the jobpool used to run job. Can be None to not
                    execute the job immediately.
        @type pool: JobPool instance

        @param function: the function to run for the job
        @type function: callable object
        
        @param args: parametters for function call 
        @param kwargs: named parametters for function call 
        
        @precondition: function cannot be None
        '''
        assert function is not None
        self._args=args
        self._kwargs = kwargs
        self._function = function
        self.running = False
        self.finished= False
        self.submitted = None
        self.priority  = None
        self.userid    = None
        
        if pool is not None:
            pool.submit(self)
        
    def runScore(self):
        '''
        @return: the score used to ordonnance job in the queue
        @rtype: C{float}
        '''
        
        return (time() - self.submitted) * self.priority
    
    def __call__(self):
        return self._function(*self._args,**self._kwargs)
        
        
        
    
        
    
    