"""
    kb package is devoted to manage access to postgresql database from python
    script
"""


class Connection(object):

    def __init__(self):
        raise RuntimeError('pyROM.KB.Connection is an abstract class')

    def cursor(self):
        raise RuntimeError('pyROM.KB.Connection.cursor is an abstract function')

    def commit(self):
        raise RuntimeError('pyROM.KB.Connection.commit is an abstract function')

    def rollback(self):
        raise RuntimeError('pyROM.KB.Connection.rollback is an abstract function')
        
    def __call__(self,query):
        return self.cursor().execute(query)
    

class Cursor(object):

    def __init__(self,db):
        raise RuntimeError('pyROM.KB.Cursor is an abstract class')

    def execute(self,query):
        raise RuntimeError('pyROM.KB.Cursor.execute is an abstract function')
        
    __call__=execute
    
    
_current_connection = None  # Static variable used to store connection to KB

def getConnection(*args,**kargs):
    """
        return a connection to the database.
        When call from database backend no argument are needed.
        All connection returned by this function 
    """
    global _current_connection
    
    if _current_connection==None or args or kargs :
        try:
            from obischemas.kb import backend
            _current_connection = backend.Connection()
        except ImportError:
            from obischemas.kb import extern
            _current_connection = extern.Connection(*args,**kargs)
    return _current_connection
    
 
