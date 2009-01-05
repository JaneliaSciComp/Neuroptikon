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
            x, y = eventAdaptor.getXnormalized(), eventAdaptor.getYnormalized()
            picker = osgUtil.LineSegmentIntersector(osgUtil.Intersector.PROJECTION, x, y)
            intersectionVisitor = osgUtil.IntersectionVisitor(picker)
            viewer.getCamera().accept(intersectionVisitor)
            if picker.containsIntersections():
                self.pointerInfo.setCamera(viewer.getCamera())
                self.pointerInfo.setMousePosition(eventAdaptor.getX(), eventAdaptor.getY())
                # TODO: need to add all intersections to self.pointerInfo?
                for intersection in picker.getIntersections():
                    localPoint = intersection.getLocalIntersectPoint()  # have to do stupid conversion from Vec3d to Vec3
                    self.pointerInfo.addIntersection(intersection.nodePath, osg.Vec3(localPoint.x(), localPoint.y(), localPoint.z()))
                intersection = picker.getFirstIntersection()
                for node in intersection.nodePath:
                    self.dragger = osgManipulator.NodeToDragger(node)
                    if self.dragger != None:
                        self.dragger.handle(self.pointerInfo, eventAdaptor, viewer)
                        eventWasHandled = True
                        break
        return eventWasHandled
    
    
    # TODO: have this return the picked object (or None) and leave the action up to the caller
    def pick(self, x, y, viewer):
        if viewer.getSceneData():
            picker = osgUtil.LineSegmentIntersector(osgUtil.Intersector.PROJECTION, x, y)
            intersectionVisitor = osgUtil.IntersectionVisitor(picker)
            viewer.getCamera().accept(intersectionVisitor)
            if picker.containsIntersections():
                intersection = picker.getFirstIntersection()
                geode = osg.NodeToGeode(intersection.nodePath[-1])
                if geode != None:
                    #print "Picking geode ", geode.getName()
                    objectID = int(geode.getName())
                    self._display.selectObject(self._display.network.objectWithId(objectID), self._display.selectionShouldExtend, self._display.findShortestPath)
            else:
                self._display.deselectAll()
        return True       
