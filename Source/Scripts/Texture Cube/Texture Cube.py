#  Copyright (c) 2011 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

"""
A script to demonstrate 3D textures.
Earth images from <http://www.randelshofer.ch/rubik/virtualcubes/virtual_rubik_en.html>
"""

region = network.createRegion()
display.setVisibleShape(region, shapes['Ball'](tessellation = 4))
display.setVisibleColor(region, [1.0, 1.0, 1.0])
texture = Texture('cube', 'cube')
images = ['+X.png', '-X.png', '+Y.png', '-Y.png', '+Z.png', '-Z.png']
if texture.loadImageCube(images):
    display.setVisibleTexture(region, texture)
display.setViewDimensions(3)
display.resetView()