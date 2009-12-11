from display.layout import Layout
import numpy as N

import pyheapq
from heapset import HeapSet
import os


class VisibleMap:
    
    def __init__(self, display, nodeDims, allowDiagonalNeighbors):
        self.display = display
        self._occupiedNodes = N.ones(list(nodeDims) + [2], N.int_) * -1
        self._distances = {}
        self.allowDiagonalNeighbors = allowDiagonalNeighbors
        self.maxHops = 20
        
        if self.allowDiagonalNeighbors:
            # TODO: better hop selection when this is enabled
            if self.display.viewDimensions == 2:
                self.offsets = [N.array((x, y)) for x in range(-1, 2) for y in range(-1, 2) if x != 0 or y != 0]
            elif self.display.viewDimensions == 3:
                self.offsets = [N.array((x, y, z)) for x in range(-1, 2) for y in range(-1, 2) for z in range(-1, 2) if x != 0 or y != 0 or z != 0]
        else:
            if self.display.viewDimensions == 2:
                self.offsets = [N.array((x, y)) for x, y in [(-1, 0), (1, 0), (0, -1), (0, 1)]]
            elif self.display.viewDimensions == 3:
                self.offsets = [N.array((x, y, z)) for x, y in [(-1, 0, 0), (1, 0, 0), (0, -1, 0), (0, 1, 0), (0, 0, -1), (0, 0, 1)]]
    
    
    def copy(self):
        newMap = VisibleMap(self.display, self._occupiedNodes.shape, self.allowDiagonalNeighbors)
        newMap._occupiedNodes = self._occupiedNodes.copy()
        return newMap
    
    
    def heuristic_estimate_of_distance(self, start, goal):
        return self.dist_between(start, goal)
    
    
    def neighbor_nodes(self, node, edge):
        node = N.array(node)
        
        # TODO: only allow orthogonal hops?
        for offset in self.offsets:
            try:
                neighbor = node.copy()
                hoppedNeighbors = []
                lastNeighbors = []
                for hopCount_ in range(1, self.maxHops + 1):
                    neighbor += offset
                    if min(neighbor) < 0:
                        # Don't go outside of the grid.
                        break
                    neighborVisibles = self.nodeOccupiers(tuple(neighbor))
                    if not any(neighborVisibles):
                        # Nobody there, it's a valid neighbor.
                        yield (tuple(neighbor), hoppedNeighbors)
                        break
                    hoppedNeighbors.append(tuple(neighbor))
                    (pathStart, pathEnd) = edge.pathEndPoints()
                    if not neighborVisibles[0].isPath() and neighborVisibles[0] not in pathStart.ancestors() and neighborVisibles[0] not in pathEnd.ancestors():
                        # Don't hop into a node's space.
                        break
                    if any(set(neighborVisibles).intersection(set(lastNeighbors))):
                        # Don't hop along a parallel path.
                        break
                    lastNeighbors = neighborVisibles
            except IndexError:
                pass
    
    
    def dist_between(self, start, goal):
        dims = len(goal)
        assert len(start) == dims
        key = [abs(goal[dim] - start[dim]) for dim in range(dims)]
        key = tuple(sorted(key))
        if key in self._distances:
            distance = self._distances[key]
        else:
            distance = sum([dim ** 2 for dim in key]) ** 0.5
            self._distances[key] = distance
        return distance
    
    
    def setNodeOccupier(self, node, visible):
        self._occupiedNodes[tuple(node) + (0,)] = -1 if visible == None else visible.displayId
        self._occupiedNodes[tuple(node) + (1,)] = -1
    
    
    def addNodeOccupier(self, node, visible):
        self._occupiedNodes[tuple(node) + (1,)] = visible.displayId
    
    
    def nodeOccupiers(self, node):
        nodeOccupiers = []
        id0, id1 = self._occupiedNodes[tuple(node)]
        if id0 >= 0:
            nodeOccupiers += [self.display.visibleWithId(id0)]
            if id1 >= 0:
                nodeOccupiers += [self.display.visibleWithId(id1)]
        return nodeOccupiers
    
    
#    def show(self):
#        import matplotlib.pyplot as pyplot
#        layer1, layer2 = N.split(self._occupiedNodes, 2, axis = 2)
#        pyplot.matshow(N.transpose(layer1.squeeze()), origin = 'lower', fignum = 1)
#        pyplot.matshow(N.transpose(layer2.squeeze()), origin = 'lower', fignum = 2)
#        pyplot.show()
    

def reconstruct_path(came_from, current_node):
    if current_node in came_from:
        node, hoppedNeighbors = came_from[current_node]
        path = reconstruct_path(came_from, node)
        return path + [(current_node, hoppedNeighbors)]
    else:
        return []


class HeapItem:
    def __init__(self, node, goal, a_map, g_score):

        self.node = node

        # g_score: Distance from start along optimal path.
        self.g_score = g_score

        # h_score: the heuristic estimates of the distances to goal
        self.h_score = a_map.heuristic_estimate_of_distance(node, goal)

        # f_score: Estimated total distance from start to goal through node.
        self.f_score = self.h_score + self.g_score

    def as_tuple(self):
        return (self.f_score, self.g_score, self.h_score, self.node)

    def __hash__(self):
        return self.as_tuple().__hash__()

    def __repr__(self):
        return str(self.as_tuple())

    def type_check(self, other):
        return type(self) == type(other)
    def __lt__(self, other):
        return self.type_check(other) and self.as_tuple().__lt__(other.as_tuple())
    def __le__(self, other):
        return self.type_check(other) and self.as_tuple().__le__(other.as_tuple())
    def __eq__(self, other):
        return self.type_check(other) and self.as_tuple().__eq__(other.as_tuple())
    def __ne__(self, other):
        return self.type_check(other) and self.as_tuple().__ne__(other.as_tuple())
    def __gt__(self, other):
        return self.type_check(other) and self.as_tuple().__gt__(other.as_tuple())
    def __ge__(self, other):
        return self.type_check(other) and self.as_tuple().__ge__(other.as_tuple())


class PathRoutingLayout(Layout):
    
    @classmethod
    def name(cls):
        return gettext('Path Routing')
    
    
    @classmethod
    def canLayoutDisplay(cls, display):
        return display.viewDimensions == 2
    
    
    def __init__(self, nodeSpacing = None, objectPadding = 0.0, crossingPenalty = 5.0, turningPenalty = 5.0, allowDiagonalPaths = True, *args, **keywordArgs):
        Layout.__init__(self, *args, **keywordArgs)
        
        # TODO: determine these values automatically based on visible spacing and connection counts
        self.nodeSpacing = nodeSpacing
        self.objectPadding = objectPadding
        self.crossingPenalty = crossingPenalty
        self.turningPenalty = turningPenalty
        self.allowDiagonalPaths = allowDiagonalPaths
    
    
    def layoutDisplay(self, display):
        # Calculate the bounds of every non-path visible.
        
        # TODO: warn the user if the layout is going to take a while?  Or provide progress with cancel?
        
        centerPositions = {}
        minPositions = {}
        maxPositions = {}
        viewDimensions = display.viewDimensions
        minBound = N.ones(viewDimensions) * 1e300
        maxBound = N.ones(viewDimensions) * -1e300
        edges = []
        ports = {}
        minPortSpacing = 1e300
        for visibles in display.visibles.itervalues():
            for visible in visibles:
                if visible.isPath():
                    if not visible.pathIsFixed():
                        (startPoint, endPoint) = visible.pathEndPoints()
                        edgeLength = ((N.array(endPoint.worldPosition()) - N.array(startPoint.worldPosition())) ** 2).sum()
                        edges.append((edgeLength, visible))
                else:
                    position = visible.worldPosition()
                    if viewDimensions == 2:
                        position = N.array((position[0], position[1]))
                    else:
                        position = N.array(position)
                    centerPositions[visible] = position
                    
                    size = visible.worldSize()
                    if self.nodeSpacing == None:
                        minPorts = len(visible.connectedPaths)
                        if minPorts > 0:
                            if viewDimensions == 2:
                                portSpace = 2.0 * size[0] + 2.0 * size[1]
                            else:
                                portSpace = size[0] * size[1] + size[0]* size[2] + size[1] * size[2]
                            portSpacing = portSpace / minPorts / 2.0
                            if portSpacing < minPortSpacing:
                                minPortSpacing = portSpacing
                    if viewDimensions == 2:
                        if visible.shape() == 'capsule':
                            size = (size[0] / 2.0, size[1])
                        size = N.array((size[0] / 2.0 + self.objectPadding, size[1] / 2.0 + self.objectPadding))
                    else:
                        if visible.shape() == 'capsule':
                            size = (size[0] / 2.0, size[1], size[2] / 2.0)
                        size = N.array((size[0] / 2.0 + self.objectPadding, size[1] / 2.0 + self.objectPadding, size[2] / 2.0 + self.objectPadding))
                    minPositions[visible] = position - size
                    maxPositions[visible] = position + size
                    for dim in range(viewDimensions):
                        minBound[dim] = min(minPositions[visible][dim], minBound[dim])
                        maxBound[dim] = max(maxPositions[visible][dim], maxBound[dim])
                    ports[visible] = []
        
        if self.nodeSpacing != None:
            nodeSpacing = self.nodeSpacing
        else:
            nodeSpacing = minPortSpacing 
        
        # Determine the bounds of all nodes and the mapping scale.
        minBound -= nodeSpacing * len(edges) / 2 + (minBound % nodeSpacing)
        maxBound += nodeSpacing * len(edges) / 2 + nodeSpacing - (maxBound % nodeSpacing)
        mapSize = (maxBound - minBound) / nodeSpacing
        
        # Build the node map
        nodeMap = VisibleMap(display, mapSize, self.allowDiagonalPaths)
        for visible in minPositions.iterkeys():
            minMap = N.ceil((minPositions[visible] - minBound) / nodeSpacing)
            maxMap = N.ceil((maxPositions[visible] - minBound) / nodeSpacing)
            for x in range(int(minMap[0]) - 1, int(maxMap[0]) + 1):
                for y in range(int(minMap[1]) - 1, int(maxMap[1]) + 1):
                    if viewDimensions == 2:
                        xOut = x < minMap[0] or x == maxMap[0]
                        yOut = y < minMap[1] or y == maxMap[1]
                        if xOut != yOut:
                            ports[visible].append((x, y))
                        if not any(visible.children):
                            nodeMap.setNodeOccupier((x, y), visible)
                    else:
                        for z in range(int(minMap[2]) - 1, int(maxMap[2]) + 1):
                            if x < minMap[0] or x == maxMap[0] or y < minMap[1] or y == maxMap[1] or z < minMap[2] or z == maxMap[2]:
                                ports[visible].append((x, y, z))
                            elif not any(visible.children) :
                                nodeMap.setNodeOccupier((x, y, z), visible)
        
        #nodeMap.show()
        
        # TODO: pre-assign ports? or at least port edges?
        
        # Route each edge starting with the shortest and finishing with the longest.
        edges.sort()
        edgeCount = 0
        for edgeLength, edge in edges:
            edgeCount += 1
            (pathStart, pathEnd) = edge.pathEndPoints()
            startName = '???' if not pathStart.client or not pathStart.client.abbreviation else pathStart.client.abbreviation
            endName = '???' if not pathEnd.client or not pathEnd.client.abbreviation else pathEnd.client.abbreviation
            if 'DEBUG' in os.environ:
                print 'Routing path from ' + startName + ' to ' + endName + ' (' + str(edgeCount) + ' of ' + str(len(edges)) + ')'
            
            # TODO: weight the search based on any previous path
            
            # Make a copy of the map to hold our tentative routing.  Once the actual route is determined this map will be discarded and the main map will be updated.
            # TODO: is this really necessary?
            edgeMap = nodeMap.copy()
            
            openHeap = HeapSet()    # priority queue of potential steps in the route
            openDict = {}           # the set of tentative nodes to be evaluated
            closedSet = set([])     # the set of blocked nodes
            came_from = {}          # tracks the route to each visited node
            
            # Aim for the center of the end visible and allow the edge to travel to any unused goal port.
            goal = tuple(N.ceil(((centerPositions[pathEnd]) - minBound) / nodeSpacing))
            goalPorts = ports[pathEnd]
            for goalPort in goalPorts:
                if edgeMap.nodeOccupiers(goalPort)[0] == pathEnd:
                    edgeMap.setNodeOccupier(goalPort, None)
            
            # Seed the walk with all unused ports on the starting visible.
            for startPort in ports[pathStart]:
                if edgeMap.nodeOccupiers(startPort)[0] == pathStart:
                    startItem = HeapItem(startPort, goal, edgeMap, edgeMap.dist_between(startPort, goal))
                    openHeap.append(startItem)
                    openDict[startPort] = startItem
                    closedSet.add(startPort)
            
            while any(openHeap):
                x  = pyheapq.heappop(openHeap)
                
                if x.node in goalPorts:
                    # The goal has been reached.  Build the path in world space and update the global map.
                    path = []
                    prevNode = None
                    for node, hoppedNeighbors in reconstruct_path(came_from, x.node):  #[:-1]:
                        nodeMap.setNodeOccupier(node, edge)
                        for hoppedNeighbor in hoppedNeighbors:
                            nodeMap.addNodeOccupier(hoppedNeighbor, edge)
                        prevNode = node
                        pathPoint = tuple(N.array(node) * nodeSpacing + minBound)
                        path += [(pathPoint[0], pathPoint[1], 0.0 if len(pathPoint) == 2 else pathPoint[2])]
                    # Combine consecutive path segments with the same slope.
                    for index in range(len(path) - 2, 0, -1):
                        delta0 = N.array(path[index + 1]) - N.array(path[index])
                        delta1 = N.array(path[index]) - N.array(path[index - 1])
                        sameSlope = True
                        for dim in range(1, viewDimensions):
                            slope0 = 1e300 if delta0[0] == 0.0 else delta0[dim] / delta0[0]
                            slope1 = 1e300 if delta1[0] == 0.0 else delta1[dim] / delta1[0]
                            if abs(slope0 - slope1) > 0.00001:
                                sameSlope = False
                                break
                        if sameSlope:
                            del path[index]
                    edge.setPathMidPoints(path)
                    del edgeMap
                    break
                
                del openDict[x.node]
                closedSet.add(x.node)
                
                neighbornodes =  []
                for node_y, hoppedNeighbors in edgeMap.neighbor_nodes(x.node, edge):
                    # This block of code gets executed at least hundreds of thousands of times so it needs to be seriously tight.
                    
                    # Start with the distance between the nodes.
                    g_score = x.g_score + edgeMap.dist_between(x.node, node_y)
                    
                    # Penalize crossing over other edges.
                    g_score += len(hoppedNeighbors) * self.crossingPenalty
                    
                    # Penalize turning.
                    if x.node in came_from:
                        prevNode = came_from[x.node][0]
                        
                        delta0 = x.node[0] - prevNode[0]
                        delta1 = node_y[0] - x.node[0]
                        if (delta0 < 0) != (delta1 < 0) or (delta0 > 0) != (delta1 > 0):
                            g_score += self.turningPenalty
                        else:
                            delta0 = x.node[1] - prevNode[1]
                            delta1 = node_y[1] - x.node[1]
                            if (delta0 < 0) != (delta1 < 0) or (delta0 > 0) != (delta1 > 0):
                                g_score += self.turningPenalty
                            elif viewDimensions == 3:
                                delta0 = x.node[2] - prevNode[2]
                                delta1 = node_y[2] - x.node[2]
                                if (delta0 < 0) != (delta1 < 0) or (delta0 > 0) != (delta1 > 0):
                                    g_score += self.turningPenalty
                    
                    neighbornodes.append((g_score, node_y, hoppedNeighbors))
                #better sort here than update the heap ..
                neighbornodes.sort()
                
                for tentative_g_score, node_y, hoppedNeighbors in neighbornodes:
                    
                    if node_y in closedSet:
                        continue
                    
                    oldy = openDict.get(node_y, None)
                    
                    y = HeapItem(node_y, goal, edgeMap, tentative_g_score)
                    
#                    openDict[node_y] = y
#                    came_from[node_y] = (x.node, hoppedNeighbors)
#                    edgeMap.setNodeOccupier(node_y, edge)
#                    for hoppedNeighbor in hoppedNeighbors:
#                        edgeMap.addNodeOccupier(hoppedNeighbor, edge)
                    
                    if oldy == None:
                        openDict[node_y] = y
                        came_from[node_y] = (x.node, hoppedNeighbors)
                        pyheapq.heappush(openHeap, y)
                    elif tentative_g_score < oldy.g_score:
                        openDict[node_y] = y
                        came_from[node_y] = (x.node, hoppedNeighbors)
                        pyheapq.updateheapvalue(openHeap, openHeap.index(oldy), y)
            
                #edgeMap.show()
            
            if 'edgeMap' in dir():
                print '\tCould not find route from ' + startName + ' to ' + endName
        
        #nodeMap.show()

#import pyheapq
#
#from heapset import HeapSet
#from copy import copy
#
#class NotImplemented(Exception):
#    pass
#
#
#class Map:
#    def __init__(self):
#        pass
#    def heuristic_estimate_of_distance(self, start,goal):
#        raise NotImplemented
#    def neighbor_nodes(self, x):
#        raise NotImplemented
#
#    def dist_between(self, x, y):
#        raise NotImplemented
#
#def reconstruct_path(came_from, current_node):
#    if current_node in came_from:
#        p = reconstruct_path(came_from,came_from[current_node])
#        return p + [current_node]
#    else:
#        return []
#
#
#class HeapItem:
#    def __init__(self,y,goal, a_map, g_score):
#
#        self.node = y
#
#        """ g_score = Distance from start along optimal path."""
#        self.g_score = g_score
#
#        """h_score the heuristic estimates of the distances to goal"""
#        self.h_score = a_map.heuristic_estimate_of_distance(y, goal)
#
#        """f_score Estimated total distance from start to goal through y."""
#        self.f_score = self.h_score + self.g_score
#
#    def as_tuple(self):
#        return (self.f_score, self.g_score, self.h_score, self.node)
#
#    def __hash__(self):
#         return self.as_tuple().__hash__()
#
#    def __repr__(self):
#        return str(self.as_tuple())
#
#    def type_check(self,other):
#        return type(self) == type(other)
#    def __lt__(self, other):
#        return self.type_check(other) and self.as_tuple().__lt__(other.as_tuple())
#    def __le__(self, other):
#        return self.type_check(other) and self.as_tuple().__le__(other.as_tuple())
#    def __eq__(self, other):
#        return self.type_check(other) and self.as_tuple().__eq__(other.as_tuple())
#    def __ne__(self, other):
#        return self.type_check(other) and self.as_tuple().__ne__(other.as_tuple())
#    def __gt__(self, other):
#        return self.type_check(other) and self.as_tuple().__gt__(other.as_tuple())
#    def __ge__(self, other):
#        return self.type_check(other) and self.as_tuple().__ge__(other.as_tuple())
#
#
#
#
#def A_star(start, goal, a_map):
#    """
#    start = the start node in a_map
#    goal = the goal node in a_map
#    a_map = a object that should inherit the Map class
#
#    returns a tuple (path, connections, uptated) where:
#      path is the optimal path (as a list of points) from the start to the goal. empty if not found,
#      
#      connections and updated are for debugging (remove them from code if too slow..,):
#        connections is the came_from dictionary and
#        uptated is the set of the connections, which were uptated from the heap
#    """
#
#    """The set of nodes already evaluated."""
#    closedset = set([])
#
#
#    firstItem = HeapItem(start,goal, a_map, 0.0)
#
#
#
#    """
#    openDict is the set of tentative nodes to be evaluated
#    containing just the initial node
#
#    scoreHeap is used as priority queue for next steps. 
#    """
#
#    scoreHeap = HeapSet([firstItem])
#    openDict = {start:firstItem}
#
#
#    """ the second last node in the shortest path from start node"""
#    came_from = {}
#
#    """this is the set of points which were uptated when they were in the heap
#    this is used only to debug the algorithm. remove if slows too much"""
#    updateset = set([])
#
#    while any(scoreHeap): # is not empty
#        """
#        the node in openset having 
#        the lowest (f_score,g_score,h_score, position) value (f_score means the most ...)
#        """
#        x  = pyheapq.heappop(scoreHeap)
#
#        if x.node == goal:
#            return [start] + reconstruct_path(came_from,goal), came_from, updateset
#
#        del openDict[x.node]
#        closedset.add(x.node)
#
#        neighbornodes =  [
#            (x.g_score + a_map.dist_between(x.node, node_y),node_y )
#            for node_y in a_map.neighbor_nodes(x.node)
#            ]
#        #better sort here than update the heap ..
#        neighbornodes.sort()
#
#
#        for tentative_g_score, node_y in neighbornodes:
#
#            if node_y in closedset:
#                continue
#
#
#            oldy = openDict.get(node_y,None)
#            y = copy(oldy)
#
#            y = HeapItem(node_y, goal, a_map, tentative_g_score)
#
#            if oldy == None:
#                openDict[node_y] = y
#                came_from[node_y] = x.node
#
#                pyheapq.heappush(scoreHeap, y)
#
#            elif tentative_g_score < oldy.g_score:
#                updateset.add( (node_y, came_from[node_y]) )
#
#                openDict[node_y] = y
#                came_from[node_y] = x.node
#
#                pyheapq.updateheapvalue(scoreHeap, scoreHeap.index(oldy), y)
#
#
#    return [], came_from, updateset
