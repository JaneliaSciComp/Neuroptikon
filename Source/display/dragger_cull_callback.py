import osg

# This class is a hack so that the picking code knows which dragger under the LOD node was most recently rendered.

class DraggerCullCallback(osg.NodeCallback):
    
    def __init__(self, display, dragger):
        osg.NodeCallback.__init__(self)   
        self._display = display
        self._dragger = dragger
    
    
    def __call__(self, node, nv):
        self._display.activeDragger = self._dragger
        #print 'Dragger was not culled: ' + str(self)
        
        self.traverse(node, nv)
