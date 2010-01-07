#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

import neuroptikon
from display.layout import Layout
import os, stat, sys


# Try to import pygraphviz or pydot, preferring the former.
try:
    # Uncomment the following line to test the pydot code path when pygraphviz is installed.
    #raise ImportError
    
    import pygraphviz
    
    # Graphviz emits warnings whenever a node's label won't fit inside the node which pygraphviz then raises.  The warnings end up littering the console which is a pain.
    # Add a filter so we don't have to see these warnings but will still see others.
    import warnings
    warnings.filterwarnings("ignore", ".*size too small for label.*")
    warnings.filterwarnings("ignore", ".*Unhandled adjust option vpsc.*")
except ImportError:
    pygraphviz = None
    try:
        import pydot
    except ImportError:
        pydot = None


class GraphvizLayout(Layout):
    
    @classmethod
    def name(cls):
        return gettext('Graphviz')
    
    
    @classmethod
    def shouldBeRegistered(cls):
        # Check if Graphviz's fdp binary is available. 
        if pygraphviz is not None:
            try:
                pygraphviz.AGraph()._which('fdp')
                return True
            except:
                return False
        if pydot is not None:
            return (pydot.find_graphviz() or {}).get('fdp', '') != ''
    
    
    @classmethod
    def canLayoutDisplay(cls, display):
        return display.viewDimensions == 2
    
    
    def layoutDisplay(self, display):
        graphVisibles = {}
        edgeVisibles = []
        if pygraphviz is not None:  # Use pygraphviz if it's available as it's faster than pydot.
            graph = pygraphviz.AGraph(strict = False, overlap = 'vpsc', sep = '+1', splines = 'polyline')
        else:
            graph = pydot.Dot(graph_type = 'graph', overlap = 'vpsc', sep = '+1', splines = 'polyline')
        for visibles in display.visibles.itervalues():
            for visible in visibles:
                if visible.isPath():
                    edgeVisibles.append(visible)   # don't add edges until all the nodes have been added
                elif len(visible.children) == 0:    #visible.parent is None:
                    graphVisibles[str(visible.displayId)] = visible
                    if pygraphviz is not None:
                        graph.add_node(str(visible.displayId), **self.graphvizAttributes(visible))
                    else:
                        graph.add_node(pydot.Node(str(visible.displayId), **self.graphvizAttributes(visible)))
        for edgeVisible in edgeVisibles:
            graphVisibles[str(edgeVisible.displayId)] = edgeVisible
            (pathStart, pathEnd) = edgeVisible.pathEndPoints()
            if pygraphviz is not None:
                graph.add_edge(str(pathStart.displayId), str(pathEnd.displayId), str(edgeVisible.displayId))
            else:
                graph.add_edge(pydot.Edge(str(pathStart.displayId), str(pathEnd.displayId), tooltip = str(edgeVisible.displayId)))
        
        # TODO: do the graph layout on a separate thread
        if pygraphviz is not None:
            #print mainGraph.to_string()
            graph.layout(prog='fdp')
            graphData = graph.to_string()
        else:
            graphData = graph.create_dot(prog='fdp')
            graph = pydot.graph_from_dot_data(graphData)
        
        # Get the bounding box of the entire graph so we can center it in the display.
        # The 'bb' attribute doesn't seem to be exposed by pydot or pygraphviz so we have to hack it out of the text dump.
        import re
        matches = re.search('bb="([0-9,.]+)"', graphData)
        bbx1, bby1, bbx2, bby2 = matches.group(1).split(',')
        width, height = (float(bbx2) - float(bbx1), float(bby2) - float(bby1))
        if width > height:
            scale = 1.0 / width
        else:
            scale = 1.0 / height
        dx, dy = ((float(bbx2) + float(bbx1)) / 2.0, (float(bby2) + float(bby1)) / 2.0)
        for visibleId, visible in graphVisibles.iteritems():
            if visible.parent is None:
                pos = None
                if not visible.isPath():
                    if not visible.positionIsFixed():
                        # Set the position of a node
                        pos = self._graphvizNodePos(graph, visibleId)
                        if pos is not None:
                            x, y = pos.split(',') 
                            # TODO: convert to local coordinates?
                            visible.setPosition(((float(x) - dx) * scale, (float(y) - dy) * scale, 0))
                elif False:
                    # Set the path of an edge
                    (pathStart, pathEnd) = visible.pathEndPoints()
                    if pygraphviz is not None:
                        edge = pygraphviz.Edge(graph, str(pathStart.displayId), str(pathEnd.displayId))
                        if 'pos' in edge.attr:
                            pos = edge.attr['pos']
                    else:
                        pass    # TODO
                    if pos is not None:
                        (startVisX, startVisY, startVisZ) = pathStart.worldPosition()
                        (endVisX, endVisY, endVisZ) = pathEnd.worldPosition()
                        startPos = self._graphvizNodePos(graph, str(pathStart.displayId))
                        startDotX, startDotY = startPos.split(',')
                        startDotX = float(startDotX)
                        startDotY = float(startDotY)
                        endPos = self._graphvizNodePos(graph, str(pathEnd.displayId))
                        endDotX, endDotY = endPos.split(',')
                        endDotX = float(endDotX)
                        endDotY = float(endDotY)
                        if startDotX != endDotX and startDotY != endDotY and startVisX != endVisX and startVisY != endVisY:
                            scaleX = (startDotX - endDotX) / (startVisX - endVisX)
                            translateX = startDotX - scaleX * startVisX
                            scaleY = (startDotY - endDotY) / (startVisY - endVisY)
                            translateY = startDotY - scaleY * startVisY
                            path_3D = []
                            path = pos.split(' ')
                            for pathElement in path[1:-1]:
                                x, y = pathElement.split(',')
                                path_3D.append(((float(x) - translateX) / scaleX, (float(y) - translateY) / scaleY, 0))
                            visible.setPathMidPoints(path_3D)
    
    
    def _graphvizNodePos(self, graph, nodeId):
        pos = None
        if pygraphviz is not None:
            node = pygraphviz.Node(graph, nodeId) 
            if 'pos' in node.attr:
                pos = node.attr['pos']
        else:
            node = graph.get_node(nodeId)
            if isinstance(node, pydot.Node):
                pos = node.get_pos()[1:-1] 
        return pos
    
    
#    def graphvizRecordLabel(self, visible):
#        labels = []
#        for child in visible.children:
#            if len(child.children) == 0:
#                labels.append(child.graphvizRecordLabel())
#            else:
#                subLabel = child.graphvizRecordLabel()
#                if child.arrangedAxis == visible.arrangedAxis:
#                    labels.append('{' + subLabel + '}')
#                else:
#                    labels.append('{{' + subLabel + '}}')
#        return '|'.join(labels)
    
    
    def graphvizAttributes(self, visible):
        pos = visible.worldPosition()
        size = visible.worldSize()
        attributes = {'width': str(size[0] * 1000.0 / 72.0), 
                      'height': str(size[1] * 1000.0 / 72.0), 
                      'fixedsize': 'true', 
                      'pos': '%f,%f' % (pos[0] * 1000.0 / 72.0, pos[1] * 1000.0 / 72.0)}
        if visible.positionIsFixed():
            attributes['pin'] = 'true'
        if False:   #len(visible.children) > 0:
            attributes['shape'] = 'record'
            attributes['label'] = '{<00>|<10>|<20>|<30>|<40>|<50>|<60>|<70>|<80>}|{<01>|<11>|<21>|<31>|<41>|<51>|<61>|<71>|<81>}|{<02>|<12>|<22>|<32>|<42>|<52>|<62>|<72>|<82>}|{<03>|<13>|<23>|<33>|<43>|<53>|<63>|<73>|<83>}|{<04>|<14>|<24>|<34>|<44>|<54>|<64>|<74>|<84>}|{<05>|<15>|<25>|<35>|<45>|<55>|<65>|<75>|<85>}|{<06>|<16>|<26>|<36>|<46>|<56>|<66>|<76>|<86>}|{<07>|<17>|<27>|<37>|<47>|<57>|<67>|<77>|<87>}|{<08>|<18>|<28>|<38>|<48>|<58>|<68>|<78>|<88>}'
        else:
            attributes['shape'] = 'box'
            attributes['label'] = ''
        return attributes
