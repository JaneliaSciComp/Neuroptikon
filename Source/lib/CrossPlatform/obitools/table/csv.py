"""
obitools.table.csv module provides an iterator adapter
allowing to parse csv (comma separatted value) file
"""

import re

def csvIterator(lineIterator,sep=','):
    '''
    Allows easy parsing of a csv file. This function
    convert an iterator on line over a csv text file
    in an iterator on data list. Each list corresponds
    to all values present n one line.
    
    @param lineIterator: iterator on text lines
    @type lineIterator: iterator
    @param sep: string of one letter used as separator
                blank charactere or " is not allowed as
                separator
    @type sep: string
    @return: an iterator on data list
    @rtype: iterator
    '''
    assert len(sep)==1 and not sep.isspace() and sep!='"'
    valueMatcher=re.compile('\s*((")(([^"]|"")*)"|([^%s]*?))\s*(%s|$)' % (sep,sep))
    def iterator():
        for l in lineIterator:
            yield _csvParse(l,valueMatcher)
    return iterator()
    
    
def _csvParse(line,valueMatcher):
    data=[]
    i = iter(valueMatcher.findall(line))
    m = i.next()
    if m[0]:
        while m[-1]!='':
            if m[1]=='"':
                data.append(m[2].replace('""','"'))
            else:
                data.append(m[0])
            m=i.next()
        if m[1]=='"':
            data.append(m[2].replace('""','"'))
        else:
            data.append(m[0])
    return data
        
        
        

        