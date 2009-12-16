#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

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
