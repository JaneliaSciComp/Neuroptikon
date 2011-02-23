region = network.createRegion()
display.setVisibleShape(region, shapes['Ball'](tessellation = 4))
display.setVisibleColor(region, [1.0, 1.0, 1.0])
texture = Texture('cube', 'cube')
images = ['+X.png', '-X.png', '+Y.png', '-Y.png', '+Z.png', '-Z.png']
if texture.loadImageCube(images):
    display.setVisibleTexture(region, texture)
display.setViewDimensions(3)
display.resetView()