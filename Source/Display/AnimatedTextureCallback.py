import osg
from datetime import datetime, timedelta

class AnimatedTextureCallback(osg.NodeCallback):
    # TODO: the app crashes on quit if one of these is still active
    
    def __init__(self, visible, textureUnit, textureMatrix, animationMatrix):
        osg.NodeCallback.__init__(self)   
        self._visible = visible
        self._textureUnit = textureUnit
        self._textureMatrix = textureMatrix
        self._matrix = animationMatrix
        self._lastUpdate = datetime.now()
    
    def __call__(self, node, nv):
        timeSinceLastUpdate = datetime.now() - self._lastUpdate
        if timeSinceLastUpdate > timedelta(0, 0.03):
            # TODO: determine the translation distance based of the time since the last update
            self._textureMatrix.getMatrix().postMult(self._matrix)
            
            self.traverse(node,nv)
            
            self._lastUpdate = datetime.now()
