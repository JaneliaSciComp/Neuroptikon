'''

'''

from itertools import imap,count,chain

from itertools import imap,count,chain

class Table(list):
    """
    Tables are list of rows of the same model
    """
    def __init__(self, headers=None, 
                       types=None, 
                       colcount=None,
                       rowFactory=None,
                       subrowFactory=None):
        '''
        
        @param headers: the list of column header.
        
                        if this parametter is C{None}, C{colcount}
                        parametter must be set.
                        
        @type headers: C{list}, C{tuple} or and iterable object
        
        @param types: the list of data type associated to each column.
        
                      If this parametter is specified its length must be
                      equal to the C{headers} length or to C{colcount}.
                      
        @type types: C{list}, C{tuple} or and iterable object
        
        @param colcount: number of column in the created table.
                         
                         If C{headers} parametter is not C{None} this
                         parametter is ignored
                          
        @type colcount: int
        '''
        
        assert headers is not None or colcount is not None,\
            'headers or colcount parametter must be not None value'
            
        if headers is None:
            headers = tuple('Col_%d' % x for x in xrange(colcount))
        
        self.headers = headers
        self.types   = types
        self.colcount= len(self.headers)

        if rowFactory is None:
            self.rowFactory=TableRow
        else:
            self.rowFactory=rowFactory
            
        if subrowFactory is None:
            self.subrowFactory=TableRow
        else:
            self.subrowFactory=rowFactory
            
        
        self.likedTo=set()
        
                

    def isCompatible(self,data):
        assert isinstance(data,(Table,TableRow))
        return (self.colcount == data.colcount and
                (id(self.types)==id(data.types) or
                 self.types==data.types
                )
               )

    def __setitem__ (self,key,value):
        '''
        
        @param key:
        @type key: C{int}, C{slice} or C{str}
        @param value:
        @type value:
        '''

        if isintance(key,int):
            if not isinstance(value, TableRow):
                value = self.rowFactory(self,value)
            else:
                assert self.isCompatible(value)
            list.__setitem__(self,key,value.row)
                
        elif isinstance(key,slice):
            indices = xrange(key.indices(len(self)))
            for i,d in imap(None,indices,value):
                self[i]=d
        
        else:        
            raise TypeError, "Key must be an int or slice value"

    def __getitem__(self,key):
        '''
        this function has different comportements depending
        of the data type of C{key} and the table used.
        
        @param key: description of the table part to return
        @type key: C{int} or C{slice}
        
        @return: return a TableRow (if key is C{int})
                 or a subpart of the table (if key is C{slice}).
        '''
        if isinstance(key,int):
            return self.rowFactory(self,
                                   list.__getitem__(self,key))
        
        if isinstance(key,slice):
            newtable=Table(self.headers,self.types)
            indices = xrange(key.indices(len(self)))
            for i in indices:
                list.append(newtable,list.__getitem__(self,i))
            self.likedTo.add(newtable)
            return newtable

        raise TypeError
                                                     
        
    def __getslice__(self,x,y):
        return self.__getitem__(slice(x,y))
    
    def __iter__(self):
        return TableIterator(self)
    
    def __hash__(self):
        return id(self)
    
    def __add__(self,itable):
        return concatTables(self,itable)
    
    def _setTypes(self,types):
        if types is not None and not isinstance(type,tuple):
            types = tuple(x for x in types)
            
        assert types is None or len(types)==len(self._headers)
        
        self._types = types
        
        if types is not None:
            for row in self:
                row.castRow()
                
    def _getTypes(self):
        return self._types
    
    types = property(_getTypes,_setTypes)
    
    def _getHeaders(self):
        return self._headers
    
    def _setHeaders(self,headers):
        if not isinstance(headers, tuple):
            headers = tuple(x for x in headers)

        self._hindex = dict((k,i) for i,k in imap(None,count(),headers))
        self._headers=headers
        self.colcount=len(headers)
        
    headers=property(_getHeaders,_setHeaders)   
    
    def append(self,value):
        if not isinstance(value, TableRow):
            value = self.rowFactory(self,value)
        else:
            assert self.isCompatible(value)
        list.append(self,value.row)
        
    
           
class _Row(list):
    def __init__(self,data,size):
        if data is None:
            list.__init__(self,(None for x in xrange(size)))
        else:
            list.__init__(self,data)
            assert len(self)==size, \
              "Size of data is not correct (%d instead of %d)" % (len(self),size)
            
    def append(self,value):
        raise NotImplementedError, \
              "Rows cannot change of size"
              
    def pop(self,key=None):
        raise NotImplementedError, \
              "Rows cannot change of size"
              
    def extend(self,values):
        raise NotImplementedError, \
              "Rows cannot change of size"
              

              
            
class TableRow(object):    
    '''
    
    '''
    def __init__(self, table,
                       data=None,
                       ):

        self.table = table

        if isinstance(data,_Row):
            self.row=row
        else:
            data = self._castRow(data)
            self.row=_Row(data,self._colcount)
                
    def getType(self):
        return self.table.types
    
    def getHeaders(self):
        return self.table.headers
    
    def getHIndex(self):
        return self.table._hindex
    
    def getColCount(self):
        return self.table.colcount
    
    types  = property(getType,None,None,
                      "List of types associated to this row")
    headers= property(getHeaders,None,None,
                      "List of headers associated to this row")
    
    _hindex= property(getHIndex,None,None)
    _colcount = property(getColCount,None,None)
    
    def _castValue(t,x):
        '''
        Cast a value to a specified type, with exception of
        C{None} values that are returned without cast.
        
        @param t: the destination type
        @type t: C{type}
        @param x: the value to cast
        
        @return: the casted value or C{None}
        
        '''
        if x is None or t is None:
            return x
        else:
            return t(x)
        
    _castValue=staticmethod(_castValue)

    def _castRow(self,data):
        
        if not isinstance(data, (list,dict)):
            data=[x for x in data]
        
        if isinstance(data,list):
            assert len(data)==self._colcount, \
                   'values has not good length'
            if self.types is not None:
                data=[TableRow._castValue(t, x)
                       for t,x in imap(None,self.types,data)]
                
        elif isinstance(data,dict):
            lvalue = [None] * len(self.header)
            
            for k,v in data.items():
                try:
                    hindex = self._hindex[k]
                    if self.types is not None:
                        lvalue[hindex]=TableRow._castValue(self.types[hindex], v)
                    else:
                        lvalue[hindex]=v
                except KeyError:
                    info('%s is not a table column' % k)
                    
            data=lvalue
        else:
            raise TypeError
        
        return data
    
    def __getitem__(self,key):
        '''
        
        @param key:
        @type key:
        '''
        
        if isinstance(key,(int,slice)):
            return self.row[key]
        
        if isinstance(key,str):
            i = self._hindex[key]
            return self.row[i]
        
        raise TypeError, "Key must be an int, slice or str value"

    def __setitem__(self,key,value):
        '''
        
        @param key:
        @type key:
        @param value:
        @type value:
        '''
        
        if isinstance(key,str):
            key = self._hindex[key]
            
        elif isinstance(key,int):
            if self.types is not None:
                value = TableRow._castValue(self.types[key], value)
            self.row[key]=value
            
        elif isinstance(key,slice):
            indices = xrange(key.indices(len(self.row)))
            for i,v in imap(None,indices,value):
                self[i]=v
        else:        
            raise TypeError, "Key must be an int, slice or str value"
        
  
                
    def __iter__(self):
        '''
        
        '''
        return iter(self.row)
    
    def append(self,value):
        raise NotImplementedError, \
              "Rows cannot change of size"
              
    def pop(self,key=None):
        raise NotImplementedError, \
              "Rows cannot change of size"
              
    def extend(self,values):
        raise NotImplementedError, \
              "Rows cannot change of size"
              
    def __len__(self):
        return self._colcount
    
    def __repr__(self):
        return repr(self.row)
    
    def __str__(self):
        return str(self.row)
    
    def castRow(self):
        self.row = _Row(self._castRow(self.row),len(self.row))
        
    
class iTableIterator(object):
    
    def _getHeaders(self):
        raise NotImplemented
    
    def _getTypes(self):
        raise NotImplemented
    
    def _getRowFactory(self):
        raise NotImplemented
    
    def _getSubrowFactory(self):
        raise NotImplemented
    
    def _getColcount(self):
        return len(self._getTypes())

    def __iter__(self):
        return self
    
    headers = property(_getHeaders,None,None)
    types   = property(_getTypes,None,None)
    rowFactory    = property(_getRowFactory,None,None)
    subrowFactory = property(_getSubrowFactory,None,None)
    colcount = property(_getColcount,None,None)
    
    def columnIndex(self,name):
        if isinstance(name,str):
            return self._reference.headers.index(name)
        elif isinstance(name,int):
            lh = len(self._reference.headers)
            if name < lh and name >=0:
                return name
            elif name < 0 and name >= -lh:
                return lh - name
            raise IndexError
        raise TypeError
    
    def next(self):
        raise NotImplemented
    

class TableIterator(iTableIterator):
    
    def __init__(self,table):
        if not isinstance(table,Table):
            raise TypeError
        
        self._reftable=table
        self._i=0
        
    def _getHeaders(self):
        return self._reftable.headers
    
    def _getTypes(self):
        return self._reftable.types
    
    def _getRowFactory(self):
        return self._reftable.rowFactory
    
    def _getSubrowFactory(self):
        return self._reftable.subrowFactory
    
    def columnIndex(self,name):
        if isinstance(name,str):
            return self._reftable._hindex[name]
        elif isinstance(name,int):
            lh = len(self._reftable._headers)
            if name < lh and name >=0:
                return name
            elif name < 0 and name >= -lh:
                return lh - name
            raise IndexError
        raise TypeError
    
    
    def rewind(self):
        i=0
    
    def next(self):
        if self._i < len(self._reftable):
            rep=self._reftable[self._i]
            self._i+=1
            return rep
        else:
            raise StopIteration
        
    headers       = property(_getHeaders,None,None)
    types         = property(_getTypes,None,None)
    rowFactory    = property(_getRowFactory,None,None)
    subrowFactory = property(_getSubrowFactory,None,None)


class ProjectionIterator(iTableIterator):
    
    def __init__(self,tableiterator,*cols):
        self._reference = iter(tableiterator)
        
        assert isinstance(self._reference, iTableIterator)

        self._selected = tuple(self._reference.columnIndex(x)
                          for x in cols)
        self._headers = tuple(self._reference.headers[x] 
                         for x in self._selected)
        
        if self._reference.types is not None:
            self._types= tuple(self._reference.types[x] 
                         for x in self._selected)
        else:
            self._types=None
                
    def _getRowFactory(self):
        return self._reference.subrowFactory
    
    def _getSubrowFactory(self):
        return self._reference.subrowFactory
    
    def _getHeaders(self):
        return self._headers
    
    def _getTypes(self):
        return self._types
    
    headers = property(_getHeaders,None,None)
    types   = property(_getTypes,None,None)
    rowFactory    = property(_getRowFactory,None,None)
    subrowFactory = property(_getSubrowFactory,None,None)
    
    def next(self):
        value = self._reference.next()
        value = (value[x] for x in self._selected)
        return self.rowFactory(self,value)
    
class SelectionIterator(iTableIterator):
    def __init__(self,tableiterator,**conditions):
        self._reference = iter(tableiterator)
        
        assert isinstance(self._reference, iTableIterator)
        
        self._conditions=dict((self._reference.columnIndex(i),c) 
                              for i,c in conditions.iteritems())
    
    def _checkCondition(self,row):
        return reduce(lambda x,y : x and y,
                      (bool(self._conditions[i](row[i]))
                       for i in self._conditions),
                       True)
    
    def _getRowFactory(self):
        return self._reference.rowFactory
    
    def _getSubrowFactory(self):
        return self._reference.subrowFactory
    
    def _getHeaders(self):
        return self._reference.headers
    
    def _getTypes(self):
        return self._reference.types
        
    def next(self):
        row = self._reference.next()
        while not self._checkCondition(row):
            row = self._reference.next()
        return row
            

    headers = property(_getHeaders,None,None)
    types   = property(_getTypes,None,None)
    rowFactory    = property(_getRowFactory,None,None)
    subrowFactory = property(_getSubrowFactory,None,None)
    
    
class UnionIterator(iTableIterator):
    def __init__(self,*itables):
        self._itables=[iter(x) for x in itables]
        self._types = self._itables[0].types
        self._headers = self._itables[0].headers
        
        assert reduce(lambda x,y: x and y,
                      (    isinstance(z,iTableIterator) 
                       and len(z.headers)==len(self._headers)
                       for z in self._itables),
                    True)
        
        self._iterator = chain(*self._itables)
        
    def _getRowFactory(self):
        return self._itables[0].rowFactory
    
    def _getSubrowFactory(self):
        return self._itables[0].subrowFactory
    
    def _getHeaders(self):
        return self._headers
    
    def _getTypes(self):
        return self._types
    
    def next(self):
        value = self._iterator.next()
        return self.rowFactory(self,value.row)
    
    headers = property(_getHeaders,None,None)
    types   = property(_getTypes,None,None)
    rowFactory    = property(_getRowFactory,None,None)
    subrowFactory = property(_getSubrowFactory,None,None)
 
    
    
def tableFactory(tableiterator):
    tableiterator = iter(tableiterator)
    assert isinstance(tableiterator, iTableIterator)
    
    newtable = Table(tableiterator.headers,
                     tableiterator.types,
                     tableiterator.rowFactory,
                     tableiterator.subrowFactory)
    
    for r in tableiterator:
        newtable.append(r)
        
    return newtable

def projectTable(tableiterator,*cols):
    return tableFactory(ProjectionIterator(tableiterator,*cols))

def subTable(tableiterator,**conditions):
    return tableFactory(SelectionIterator(tableiterator,**conditions))
   
def concatTables(*itables):
    '''
    Concatene severals tables.
    
    concatenation is done using the L{UnionIterator<UnionIterator>}
    
    @type itables: iTableIterator or Table
    
    @return: a new Table
    @rtype: c{Table}
    
    @see: L{UnionIterator<UnionIterator>}
    '''
    return tableFactory(UnionIterator(*itables))
   
class TableIteratorAsDict(object):
    
    def __init__(self,tableiterator):
        self._reference = iter(tableiterator)
        
        assert isinstance(self._reference, iTableIterator)
        
        self._headers  = self._reference.headers
        self._types     = self._reference.types
        if self._types is not None:
            self._types = dict((n,t) 
                               for n,t in imap(None,self._headers,self._types))
        
    def __iter__(self):
        return self
    
    def next(self):
        value = self._reference.next()
        return dict((n,t)
                    for n,t in imap(None,self._headers,value))
        
    def _getHeaders(self):
        return self._headers
    
    def _getTypes(self):
        return self._types
    
    headers = property(_getHeaders,None,None)
    types   = property(_getTypes,None,None)
     