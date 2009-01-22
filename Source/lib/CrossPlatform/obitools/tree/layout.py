
class NodeLayout(dict):
    '''
    Layout data associated to a tree node.
    '''
    pass

class TreeLayout(dict):
    '''
    Description of a phylogenetic tree layout
    
    @see: 
    '''
    def addNode(self,node):
        self[node]=NodeLayout()
        
    def setAttribute(self,node,key,value):
        self[node][key]=value
        
    def hasAttribute(self,node,key):
        return key in self[node]
    
    def getAttribute(self,node,key,default=None):
        return self[node].get(key,default)
    
    def setNodesColor(self,color,predicat=True):
        '''
        
        @param color:
        @type color:
        @param predicat:
        @type predicat:
        '''
        for node in self:
            if callable(predicat):
                change = predicat(node)
            else:
                change = predicat
                
            if change:
                if callable(color):
                    c = color(node)
                else:
                    c = color
                self.setAttribute(node, 'color', color)
                
    def setCircular(self,iscircularpredicat):
        for node in self:
            if callable(iscircularpredicat):
                change = iscircularpredicat(node)
            else:
                change = iscircularpredicat
                
            if change:
                self.setAttribute(node, 'shape', 'circle')
            else:
                self.setAttribute(node, 'shape', 'square')
                
    def setRadius(self,radius,predicat=True):
        for node in self:
            if callable(predicat):
                change = predicat(node)
            else:
                change = predicat
                
            if change:
                if callable(radius):
                    r = radius(node)
                else:
                    r = radius
                self.setAttribute(node, 'radius', r)
                
def predicatGeneratorIsInfoEqual(info,value):
    def isInfoEqual(node):
        data = node._info
        return data is not None and info in data and data[info]==value
    
    return isInfoEqual

def isTerminalNode(node):
    return node._isterminal

def constantColorGenerator(color):
    def colorMaker(node):
        return color
    
    return colorMaker

def constantColorGenerator(color):
    def colorMaker(node):
        return color
    
    return colorMaker

def notPredicatGenerator(predicat):
    def notpred(x):
        return not predicat(x)
    return notpred




        