import osg, osgGA, osgManipulator, osgUtil, osgViewer


class PickHandler(osgGA.GUIEventHandler): 
    """PickHandler -- A GUIEventHandler that implements picking."""
    
    def __init__(self, display):
        self._display = display
        self._lastMouse = (0, 0)
        self.pointerInfo = osgManipulator.PointerInfo()
        self.dragger = None
        osgGA.GUIEventHandler.__init__(self)
    
    
    def handle(self, eventAdaptor, actionAdaptor, object, nodeVisitor):
        eventWasHandled = False
        viewer = osgViewer.GUIActionAdapterToViewer(actionAdaptor)
        if viewer:
            eventtype = eventAdaptor.getEventType()
            if eventtype == eventAdaptor.PUSH:
                self.pointerInfo.reset()
                self._lastMouse = (eventAdaptor.getX(), eventAdaptor.getY())
                eventWasHandled = self.drag(eventAdaptor, viewer)
            elif eventtype == eventAdaptor.MOVE:
                self._lastMouse = (eventAdaptor.getX(), eventAdaptor.getY())
                eventWasHandled = False
            elif eventtype == eventAdaptor.DRAG:
                if self.dragger != None:
                    self.pointerInfo.setCamera(viewer.getCamera())
                    self.pointerInfo.setMousePosition(eventAdaptor.getX(), eventAdaptor.getY())
                    eventWasHandled = self.dragger.handle(self.pointerInfo, eventAdaptor, actionAdaptor)
                    if eventWasHandled:
                        self._display.visibleWasDragged()
                        
            elif eventtype == eventAdaptor.RELEASE:
                if self.dragger != None:
                    self.pointerInfo.setCamera(viewer.getCamera())
                    self.pointerInfo.setMousePosition(eventAdaptor.getX(), eventAdaptor.getY())
                    eventWasHandled = self.dragger.handle(self.pointerInfo, eventAdaptor, actionAdaptor)
                    self.dragger = None
                    self.pointerInfo.reset()
                    # TODO: is this where visible's size and position should get updated?
                elif self._lastMouse == (eventAdaptor.getX(), eventAdaptor.getY()):
                    eventWasHandled = self.pick(eventAdaptor.getXnormalized(), eventAdaptor.getYnormalized(), viewer)
        return eventWasHandled
    
    
    def drag(self, eventAdaptor, viewer):
        eventWasHandled = False
        if viewer.getSceneData():
            # TODO: This is a major hack.  The intersection code below always picks the composite dragger, even if it isn't being rendered.  So we remove the inactive dragger while picking.
            # TODO: Figure out how to make the intersection code honor the LOD and get rid of the DraggerCullCallback class.
            if self._display.draggerLOD is not None:
                if self._display.activeDragger == self._display.simpleDragger:
                    self._display.draggerLOD.removeChild(self._display.compositeDragger)
                if self._display.activeDragger == self._display.compositeDragger:
                    self._display.draggerLOD.removeChild(self._display.simpleDragger)
            x, y = eventAdaptor.getXnormalized(), eventAdaptor.getYnormalized()
            picker = osgUtil.LineSegmentIntersector(osgUtil.Intersector.PROJECTION, x, y)
            intersectionVisitor = osgUtil.IntersectionVisitor(picker)
            intersectionVisitor.setTraversalMode(osg.NodeVisitor.TRAVERSE_ACTIVE_CHILDREN)
            viewer.getCamera().accept(intersectionVisitor)
            if picker.containsIntersections():
                self.pointerInfo.setCamera(viewer.getCamera())
                self.pointerInfo.setMousePosition(eventAdaptor.getX(), eventAdaptor.getY())
                for intersection in picker.getIntersections():
                    localPoint = intersection.getLocalIntersectPoint()  # have to do stupid conversion from Vec3d to Vec3
                    self.pointerInfo.addIntersection(intersection.nodePath, osg.Vec3(localPoint.x(), localPoint.y(), localPoint.z()))
                intersection = picker.getFirstIntersection()
                for node in intersection.nodePath:
                    self.dragger = osgManipulator.NodeToDragger(node)
                    if self.dragger is not None:
                        self.dragger.handle(self.pointerInfo, eventAdaptor, viewer)
                        eventWasHandled = True
                        break
            if self._display.draggerLOD is not None:
                if self._display.activeDragger == self._display.simpleDragger:
                    self._display.draggerLOD.addChild(self._display.compositeDragger)
                if self._display.activeDragger == self._display.compositeDragger:
                    self._display.draggerLOD.addChild(self._display.simpleDragger)
        return eventWasHandled
    
    
    # TODO: have this return the picked object (or None) and leave the action up to the caller
    def pick(self, x, y, viewer):
        if viewer.getSceneData():
            picker = osgUtil.LineSegmentIntersector(osgUtil.Intersector.PROJECTION, x, y)
            intersectionVisitor = osgUtil.IntersectionVisitor(picker)
            viewer.getCamera().accept(intersectionVisitor)
            if picker.containsIntersections():
                # Loop through all of the hits to find the "deepest" one in the sense of the region hierarchy.  So a child of a region will be picked instead of its parent.
                deepestVisible = None
                for intersection in picker.getIntersections():
                    for node in intersection.nodePath:
                        geode = osg.NodeToGeode(node)
                        if geode != None:
                            visibleID = int(geode.getName())
                            visible = self._display.visibleIds[visibleID]
                            if deepestVisible is None or deepestVisible in visible.ancestors():
                                deepestVisible = visible
                self._display.selectVisible(deepestVisible, self._display.selectionShouldExtend, self._display.findShortestPath)
            else:
                self._display.deselectAll()
        return True       
