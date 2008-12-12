"""Interaction mode for examining objects"""

class DragManager (eventmanager.EventManager):
    """Interaction EventManager for "Examine" mode

    This interaction manager implements an examine mode
    similar to that found in VRML97 browsers.  Pointing
    to an object and dragging up/down left/right causes
    the viewpoint to orbit around the object as if the
    object were held in the hand and being rotated.

    The manager uses the trackball thereby the dragwatcher
    to provide screen-relative scaling of the input.  In
    other words, distances are measured as fractions of
    the distance to the edge of the screen.
    """
    type = "drag"
    def __init__ (self, display, visible, event):
        """Initialise the ExamineManager

        display -- Display instance
        center -- object-space coordinates about which to revolve
        event -- event which began the examine interaction.
        """
        self.client = display
        self.draggedItem = visible
        self.lastDragPoint = event.getPickPoint()
        eventmanager.EventManager.__init__ (self)
        self.button = event.button
        self.OnBind()
    ### client API
    def update( self, event ):
        '''Update the examine trackball with new mouse event

        This updates the internal position, then triggers a redraw of the display.
        '''
        x, y = event.getPickPoint()
        x -= self.lastDragPoint[0]
        y -= self.lastDragPoint[1]
        self.draggedItem.offsetPosition((x, y, 0))
        self.lastDragPoint = event.getPickPoint()
        self.client.triggerRedraw()
    def release( self, event ):
        """Trigger cleanup of the examine mode"""
        self.OnUnBind()
    def cancel(self, event):
        """Cancel the examine mode, return to original position and orientation"""
        self.OnUnBind()

    ### Customisation points
        
    def OnBind( self ):
        """Bind the events needing binding to run the examine mode
        Customisation point for those needing custom controls"""
        self.client.captureEvents("mousebutton", self)
        self.client.captureEvents("mousemove", self)
    def OnUnBind( self ):
        """UnBind the events for the examine mode
        Customisation point for those needing custom controls"""
        self.client.captureEvents("mousemove", None)
        self.client.captureEvents("mousebutton", None)
    def ProcessEvent (self, event):
        """Respond to events from the system
        Customisation point for those needing custom controls"""
        if event.type == "mousemove":
            self.update (event)
        elif event.type == "mousebutton":
            if event.button == self.button and event.state == 0: # mouse released
                self.release (event)
            elif event.state == 0: # mouse released, not our button, cancel
                self.cancel( event )
        
