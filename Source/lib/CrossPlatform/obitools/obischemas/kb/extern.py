"""
Module : KB.extern
Author : Eric Coissac
Date   : 03/05/2004

Module wrapping psycopg interface module to allow connection
to a postgresql databases with the same interface from
backend and external script.

This module define a class usable from external script 
"""


import psycopg2
import sys
from obischemas import kb

class Connection(kb.Connection):

    def __init__(self,*connectParam,**kconnectParam):
        if connectParam:
            self.connectParam=={'dsn':connectParam}
        else:
            self.connectParam=kconnectParam 
        print self.connectParam
        self.db = psycopg2.connect(**(self.connectParam))

    def restart(self):
	ok=1
	while (ok and ok < 1000):
	  try:	
	    self.db = psycopg2.connect(**self.connectParam)
	  except:
            ok+=1
	  else:
            ok=0

	    
    def cursor(self):
        curs = Cursor(self.db)
        if hasattr(self,'autocommit') and self.autocommit:
            curs.autocommit = self.autocommit
        return curs
    
    def commit(self):
        self.db.commit()

    def rollback(self):
        if hasattr(self,'db'):
            self.db.rollback()

    def __del__(self):
        if hasattr(self,'db'):
            self.rollback()
        
class Cursor(kb.Cursor):

    def __init__(self,db):
	self.db   = db
        self.curs = db.cursor()
        
    def execute(self,query):
        try:
            self.curs.execute(query)
            if hasattr(self,'autocommit') and self.autocommit:
                self.db.commit()
        except psycopg2.ProgrammingError,e:
            print >>sys.stderr,"===> %s" % query
            raise e
        except psycopg2.IntegrityError,e:
            print >>sys.stderr,"---> %s" % query
            raise e
        try:
           label = [x[0] for x in self.curs.description]
           return [dict(map(None,label,y))
                   for y in self.curs.fetchall()]
        except TypeError:
           return []
