from obitools.obischemas import kb
__connection__ = None

def initConnection(options):
    global __connection__
    param = {}
    if hasattr(options, "dbname") and options.dbname is not None:
        param["database"]=options.dbname
    if hasattr(options, "dbhost") and options.dbhost is not None:
        param["host"]=options.dbhost
    if hasattr(options, "dbuser") and options.dbuser is not None:
        param["username"]=options.dbuser
    if hasattr(options, "dbpassword") and options.dbpassword is not None:
        param["password"]=options.dbpassword
        
    __connection__=kb.getConnection(**param)
    __connection__.autocommit=options.autocommit

def getConnection(options=None):
    global __connection__

    if options is not None:
        initConnection(options)
    
    assert __connection__ is not None,"database connection is not initialized"
        
    return __connection__
   