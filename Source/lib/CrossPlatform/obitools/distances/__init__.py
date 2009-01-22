class DistanceMatrix(object):
    
    def __init__(self,alignment):
        '''
        DistanceMatrix constructor.
        
            @param alignment: aligment used to compute distance matrix
            @type alignment: obitools.align.Alignment
        '''
        self.aligment = alignment
        self.matrix = [[None] * (x+1) for x in xrange(len(alignment))]
        
    def evaluateDist(self,x,y):
        raise NotImplementedError
        
    def __getitem__(self,key):
        assert isinstance(key,(tuple,list)) and len(key)==2, \
               'key must be a tuple or a list of two integers'
        x,y = key
        if y < x:
            z=x
            x=y
            y=z
        rep = self.matrix[y][x]
        if rep is None:
            rep = self.evaluateDist(x,y)
            self.matrix[y][x] = rep
            
        return rep