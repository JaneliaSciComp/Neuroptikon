#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

"""
This script adds arrowheads to the selected paths.  Currently it is only intended for producing printed figures.

You may need to change the length and width parameters depending on the scale of your visualization.
The arrowheads are not connected to the paths in any way so they will not move if the paths are moved.
"""

from math import atan2, sqrt
import osg

def addArrowhead(arrowPoint, otherPoint, length = 0.005, width = 0.0025):
    dx = arrowPoint[0] - otherPoint[0]
    dy = arrowPoint[1] - otherPoint[1]
    dz = arrowPoint[2] - otherPoint[2]
    
    # Determine the position of the midpoint of the arrowhead.
    mag = sqrt(dx**2.0 + dy**2.0 + dz**2.0)
    position = (arrowPoint[0] + (otherPoint[0] - arrowPoint[0]) / mag * length / 2.0, \
                arrowPoint[1] + (otherPoint[1] - arrowPoint[1]) / mag * length / 2.0, \
                arrowPoint[2] + (otherPoint[2] - arrowPoint[2]) / mag * length / 2.0)
    
    # Determine the rotation of the arrowhead.
    dxz = sqrt(dx**2.0 + dz**2.0)
    dAngle = atan2(dxz, dy)
    rotationVec = osg.Vec3f(0, 1, 0) ^ osg.Vec3f(dx, dy, dz)
    rotationVec.normalize()
    rotation = (rotationVec.x(), rotationVec.y(), rotationVec.z(), dAngle)
    
    # Add the arrowhead to the display.
    display.visualizeObject(None, shape = shapes['Cone'], color = visible.color(), position = position, size = (width, length, width), rotation = rotation)
    

for visible in display.selection():
    if visible.isPath() and hasattr(visible.shape(), 'points'):
        pathPoints = visible.shape().points()
        pathStart, pathEnd = visible.pathEndPoints()
        
        if visible.flowTo() and pathEnd.opacity() > 0.0 and pathEnd.shape() != None:
            addArrowhead(pathPoints[-1], pathPoints[-2])
        
        if visible.flowFrom() and pathStart.opacity() > 0.0 and pathStart.shape() != None:
            addArrowhead(pathPoints[0], pathPoints[1])
