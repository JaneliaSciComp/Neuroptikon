import pyheapq

class NotImplemented(Exception):
    pass



class HeapSet(list):
    """
    This class tries to implement the 'index'-fnc of the list class
    more efficiently. Using this, you can chance the value of item in a
    heap in an efficient manner.
    Only those functionalities used in pyheapq.py file  are implemented.
    If you have one item in this tructure more than once, this class 
    does not work properly anymore..
    """
    def __init__(self, iterator = None):
        self.pos_dict = {}
        self.pop_begin = 0
        if iterator != None:
            #print "init thing"
            for i in iterator:
                self.append(i)

    def append(self, item):
        #print 'append', item
        if item in self.pos_dict:
            raise ValueError("item %s appended twice."%str(item))
        self.pos_dict[item] = self.pop_begin + len(self)
        list.append(self, item)

    def __setitem__(self,pos, item):
        #print 'setitem called.', 'pos', pos, 'item',item
        oldvalue = self.__getitem__(pos)
        if self.pos_dict[oldvalue] == pos:
            del self.pos_dict[oldvalue]

        list.__setitem__(self,pos, item)
        self.pos_dict[item] = self.pop_begin + pos


    def pop(self, pos = None):
        #print 'my pop called'
        #print "len", len(self), 'self.pop_begin', self.pop_begin
        if pos == None:
            item = list.pop(self)
            pos = len(self)
        elif pos == 0:
            item = list.pop(self,0)
            self.pop_begin += 1
        else:
            raise ValueError('pop is implemented just for begin and end')

        del self.pos_dict[item]
        #if self.pos_dict[item] == pos :
        #    del self.pos_dict[item]
        #else:
        #    raise Exception("item's index was not right %d vs %d"%(pos,  self.pos_dict[item]))

        if self.pop_begin >= 2147483647:
            self.pop_begin -= 2147483647
            for i in self.pos_dict:
                self.pos_dict[i] -= 2147483647

        return item

    def index(self,item):
        return self.pos_dict[item] - self.pop_begin

    def __str__(self):
        return list.__str__(self) + str(self.pos_dict) + "pops %d"%self.pop_begin


if __name__ == "__main__":


    print 'creation test'
    l = HeapSet([1,5,3,7,8,2,4,6])
    print l, dir(l)
    print l
    print 'length', len(l)

    print 'heapsort test'
    l = HeapSet([1,5,3,7,8,2,4,6])
    pyheapq.heapify(l)
    print l

    reslist = []

    while l:
        resitem = pyheapq.heappop(l)
        reslist.append(resitem)

    print 'this sould be sorted:', reslist


    print 'double insert test'
    l = HeapSet([])
    try:
        l.append(1)
        l.append(2)
        l.append(1)
    except ValueError, e:
        print "this should be VelueError:", e


    print 'simple modification of the heap:'

    reslist = []
    l = HeapSet([1,5,3,7,8,2,4,6])
    pyheapq.heapify(l)

    print '2 --> 0 and 5 --> 9'
    index2 = l.index(2)
    index5 = l.index(5)

    print "index of value 2", index2
    print "index of value 5", index5

    print l
    pyheapq.updateheapvalue(l,index2,0)
    pyheapq.updateheapvalue(l,index5,9)
    print l

    while l:
        resitem = pyheapq.heappop(l)
        reslist.append(resitem)

    print 'this sould be sorted:', reslist
    print l
