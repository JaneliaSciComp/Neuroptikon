"""
This script adds arrowheads to the selected paths.

You may need to change the length and width parameters depending on the scale of your visualization.  All objects must be laid out in the same Z plane.  The arrowheads are not connected to the paths in any way so they will not move if the paths are moved.
"""

from math import atan2, cos, pi, sin


def addArrowhead(arrowPoint, otherPoint, length = 0.005, width = 0.0025):
    angle = atan2(otherPoint[1] - arrowPoint[1], otherPoint[0] - arrowPoint[0])
    # Objects are positioned at their center point so pull the arrowhead back by half its length so it's not sticking into the pointed at object.
    position = (arrowPoint[0] + cos(angle) * length / 2.0, arrowPoint[1] + sin(angle) * length / 2.0, arrowPoint[2])
    display.visualizeObject(None, shape = shapes['Cone'], color = visible.color(), position = position, size = (width, length, width), rotation = (0, 0, 1, angle + pi / 2.0))
    

for visible in display.selection():
    if visible.isPath() and hasattr(visible.shape(), 'points'):
        pathPoints = visible.shape().points()
        
        if visible.flowTo():
            addArrowhead(pathPoints[-1], pathPoints[-2])
        
        if visible.flowFrom():
            addArrowhead(pathPoints[0], pathPoints[1])
