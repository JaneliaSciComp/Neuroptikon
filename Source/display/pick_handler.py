#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

import osg, osgGA, osgManipulator, osgUtil, osgViewer

import display
from shape import UnitShape


class PickHandler(osgGA.GUIEventHandler): 
    """PickHandler -- A GUIEventHandler that implements picking."""
    
    def __init__(self, display):
        self._display = display
        self._lastMouse = (0, 0)
        self._panning = False
        self.pointerInfo = osgManipulator.PointerInfo()
        self.dragger = None
        osgGA.GUIEventHandler.__init__(self)
    
    
    def handle(self, eventAdaptor, actionAdaptor, osgObject_, nodeVisitor_):
        eventWasHandled = False
        viewer = osgViewer.GUIActionAdapterToViewer(actionAdaptor)
        if viewer:
            eventtype = eventAdaptor.getEventType()
            if eventtype == eventAdaptor.PUSH:
                self.pointerInfo.reset()
                self._lastMouse = (eventAdaptor.getX(), eventAdaptor.getY())
                eventWasHandled = self.startDragPanOrPick(eventAdaptor, viewer)
            elif eventtype == eventAdaptor.MOVE:
                self._lastMouse = (eventAdaptor.getX(), eventAdaptor.getY())
                eventWasHandled = False
            elif eventtype == eventAdaptor.DRAG:
                if self.dragger != None:
                    self.pointerInfo.setCamera(viewer.getCamera())
                    self.pointerInfo.setMousePosition(eventAdaptor.getX(), eventAdaptor.getY())
                    eventWasHandled = self.dragger.handle(self.pointerInfo, eventAdaptor, actionAdaptor)
                    if eventWasHandled:
                        self._display._visibleWasDragged()
                elif self._panning or self._display.navigationMode() == display.PANNING_MODE:
                    self._display.shiftView(eventAdaptor.getX() - self._lastMouse[0], eventAdaptor.getY() - self._lastMouse[1])
                    self._panning = True
                    self._lastMouse = (eventAdaptor.getX(), eventAdaptor.getY())
                    eventWasHandled = True
            elif eventtype == eventAdaptor.RELEASE:
                if self.dragger != None:
                    # Finish the drag.
                    self.pointerInfo.setCamera(viewer.getCamera())
                    self.pointerInfo.setMousePosition(eventAdaptor.getX(), eventAdaptor.getY())
                    eventWasHandled = self.dragger.handle(self.pointerInfo, eventAdaptor, actionAdaptor)
                    self.dragger = None
                    self.pointerInfo.reset()
                    self._display.computeVisiblesBound()
                    self._display._resetView()
                    # TODO: is this where visible's size and position should get updated?
                elif self._panning:
                    # Finish panning.
                    self._panning = False
                elif self._lastMouse == (eventAdaptor.getX(), eventAdaptor.getY()):
                    # Do a pick.
                    
                    eventWasHandled = self.pick(eventAdaptor.getX(), eventAdaptor.getY(), viewer)
        return eventWasHandled
    
    
    def startDragPanOrPick(self, eventAdaptor, viewer):
        eventWasHandled = False
        if viewer.getSceneData():
            # TODO: This is a major hack.  The intersection code below always picks the composite dragger, even if it isn't being rendered.  So we remove the inactive dragger while picking.
            # TODO: Figure out how to make the intersection code honor the LOD and get rid of the DraggerCullCallback class.
            if self._display.draggerLOD is not None:
                if self._display.activeDragger == self._display.simpleDragger:
                    self._display.draggerLOD.removeChild(self._display.compositeDragger)
                if self._display.activeDragger == self._display.compositeDragger:
                    self._display.draggerLOD.removeChild(self._display.simpleDragger)
            x, y = eventAdaptor.getX(), eventAdaptor.getY()
            picker = osgUtil.PolytopeIntersector(osgUtil.Intersector.WINDOW, x - 2.0, y - 2.0, x + 2.0, y + 2.0)
            intersectionVisitor = osgUtil.IntersectionVisitor(picker)
            intersectionVisitor.setTraversalMode(osg.NodeVisitor.TRAVERSE_ACTIVE_CHILDREN)
            viewer.getCamera().accept(intersectionVisitor)
            if picker.containsIntersections():
                # Add all intersections from the first dragger hit onward to the pointer info.  This allows dragging of nested regions.
                self.pointerInfo.setCamera(viewer.getCamera())
                self.pointerInfo.setMousePosition(eventAdaptor.getX(), eventAdaptor.getY())
                for intersection in picker.getIntersections():
                    for node in intersection.nodePath:
                        if self.dragger is None:
                            self.dragger = osgManipulator.NodeToDragger(node)
                        if self.dragger is not None:
                            localPoint = intersection.localIntersectionPoint  # have to do stupid conversion from Vec3d to Vec3
                            self.pointerInfo.addIntersection(intersection.nodePath, osg.Vec3(localPoint.x(), localPoint.y(), localPoint.z()))
                if self.dragger is not None:
                    self.dragger.handle(self.pointerInfo, eventAdaptor, viewer)
                    eventWasHandled = True
            if self._display.draggerLOD is not None:
                if self._display.activeDragger == self._display.simpleDragger:
                    self._display.draggerLOD.addChild(self._display.compositeDragger)
                if self._display.activeDragger == self._display.compositeDragger:
                    self._display.draggerLOD.addChild(self._display.simpleDragger)
        return eventWasHandled
    
    
    # TODO: have this return the picked object (or None) and leave the action up to the caller
    def pick(self, x, y, viewer):
        if viewer.getSceneData():
            picker = osgUtil.PolytopeIntersector(osgUtil.Intersector.WINDOW, x - 2.0, y - 2.0, x + 2.0, y + 2.0)
            intersectionVisitor = osgUtil.IntersectionVisitor(picker)
            viewer.getCamera().accept(intersectionVisitor)
            if picker.containsIntersections():
                intersections = picker.getIntersections()
                
                # The PolytopeIntersector mis-calculates the eye distance for geometry nested under a transform, which is true for all UnitShapes.  (See the thread at http://www.mail-archive.com/osg-users@lists.openscenegraph.org/msg29195.html for some discussion.)
                # Calculate the correct distance and re-sort.
                # This will probably still work correctly after that bug is fixed but will be inefficient.
                visibleHits = []
                eye, center, up = (osg.Vec3(), osg.Vec3(), osg.Vec3())
                viewer.getCamera().getViewMatrixAsLookAt(eye, center, up)
                eye = (eye.x(), eye.y(), eye.z())
                for intersection in intersections:
                    for node in intersection.nodePath:
                        geode = osg.NodeToGeode(node)
                        if geode != None:
                            visibleID = int(geode.getName())
                            visible = self._display.visibleWithId(visibleID)
                            if geode.getOrCreateStateSet().getAttribute(osg.StateAttribute.DEPTH):
                                # If a geode has this attribute set then (currently) it is being rendered in front of all other nodes.  Simulate this here by placing the geode right at the eye.
                                # If depths other than the default or osg.Depth.ALWAYS are used in the future then this check will need to be modified.
                                eyeDistance = 0.0
                            else:
                                intersectionPoint = intersection.localIntersectionPoint
                                if isinstance(visible.shape(), UnitShape):
                                    position = visible.worldPosition()
                                    size = visible.worldSize()
                                    intersectionPoint = (position[0] + size[0] * intersectionPoint.x(), position[1] + size[1] * intersectionPoint.y(), position[2] + size[2] * intersectionPoint.z())
                                eyeDistance = (intersectionPoint[0] - eye[0]) ** 2 + (intersectionPoint[1] - eye[1]) ** 2 + (intersectionPoint[2] - eye[2]) ** 2
                            visibleHits += [(eyeDistance, visible)]
                visibleHits.sort()
                
                # Loop through all of the hits to find the "deepest" one in the sense of the visible hierarchy.  For example, a neuron in a region will be picked instead of the region even though the region hit is closer.
                if self._display.useGhosts():
                    # Make a first pass only picking non-ghosted items.
                    # TODO: this could be done with node masks...
                    deepestVisible = None
                    for distance_, visible in visibleHits:
                        if (visible in self._display.highlightedVisibles or visible in self._display.animatedVisibles) and (deepestVisible is None or deepestVisible in visible.ancestors()):
                            deepestVisible = visible
                    if deepestVisible is not None:
                        self._display.selectVisibles([deepestVisible], self._display.selectionShouldExtend, self._display.findShortestPath)
                        return True
                deepestVisible = None
                for distance_, visible in visibleHits:
                    if deepestVisible is None or deepestVisible in visible.ancestors():
                        deepestVisible = visible
                self._display.selectVisibles([deepestVisible], self._display.selectionShouldExtend, self._display.findShortestPath)
            else:
                self._display.selectVisibles([])
        return True
