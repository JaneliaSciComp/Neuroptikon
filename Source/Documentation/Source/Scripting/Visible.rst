.. image:: ../../../../Artwork/Neuroptikon.png
   :width: 64
   :height: 64
   :align: left

Visualized Objects
==================

.. class:: Display.Visible.Visible

Instances of this class map a :class:`network object <Network.Object.Object>` (neurion, region, etc.) to a specific :class:`display <Display.Display.Display>`.  They capture all of the attributes needed to render the object.

You should never create an instance of this class directly.  Instead use the value returned by calling :meth:`visualizeObject() <Display.Display.Display.visualizeObject>` on a display.

.. _geometry:

Changing the geometry of a visualized object
--------------------------------------------

Use the following methods to change the settings for individual objects in the visualization.

.. automethod:: Display.Visible.Visible.setPosition
.. automethod:: Display.Visible.Visible.offsetPosition
.. automethod:: Display.Visible.Visible.position
.. automethod:: Display.Visible.Visible.worldPosition
.. automethod:: Display.Visible.Visible.setPositionIsFixed
.. automethod:: Display.Visible.Visible.positionIsFixed
.. automethod:: Display.Visible.Visible.setSize
.. automethod:: Display.Visible.Visible.size
.. automethod:: Display.Visible.Visible.worldSize
.. automethod:: Display.Visible.Visible.setSizeIsFixed
.. automethod:: Display.Visible.Visible.sizeIsFixed
.. automethod:: Display.Visible.Visible.setSizeIsAbsolute
.. automethod:: Display.Visible.Visible.sizeIsAbsolute

.. _appearance:

Changing the appearance of a visualized object
----------------------------------------------

.. automethod:: Display.Visible.Visible.setColor
.. automethod:: Display.Visible.Visible.color
.. automethod:: Display.Visible.Visible.setOpacity
.. automethod:: Display.Visible.Visible.opacity
.. automethod:: Display.Visible.Visible.setShape
.. automethod:: Display.Visible.Visible.shape
.. automethod:: Display.Visible.Visible.setTexture
.. automethod:: Display.Visible.Visible.texture
.. automethod:: Display.Visible.Visible.setTextureScale
.. automethod:: Display.Visible.Visible.textureScale
.. automethod:: Display.Visible.Visible.setWeight
.. automethod:: Display.Visible.Visible.weight

.. _label:

Changing the label of a visualized object
-----------------------------------------

Use the following methods to change the settings for the label that adorns a visualized object.

.. automethod:: Display.Visible.Visible.setLabel
.. automethod:: Display.Visible.Visible.label
.. automethod:: Display.Visible.Visible.setLabelColor
.. automethod:: Display.Visible.Visible.labelColor
.. automethod:: Display.Visible.Visible.setLabelPosition
.. automethod:: Display.Visible.Visible.labelPosition

.. _connection:

Changing the visualization of a connection
------------------------------------------

The end and mid-points of a connection between objects can be modified with the following methods.

.. automethod:: Display.Visible.Visible.setPathEndPoints
.. automethod:: Display.Visible.Visible.pathEndPoints
.. automethod:: Display.Visible.Visible.setPathMidPoints
.. automethod:: Display.Visible.Visible.pathMidPoints
.. automethod:: Display.Visible.Visible.isPath

The appearance of the connection's flow can also be customized.  If None is passed to any of the methods then the default value for the display will be used instead.

.. automethod:: Display.Visible.Visible.setFlowFrom
.. automethod:: Display.Visible.Visible.flowFrom
.. automethod:: Display.Visible.Visible.setFlowFromColor
.. automethod:: Display.Visible.Visible.flowFromColor
.. automethod:: Display.Visible.Visible.setFlowFromSpacing
.. automethod:: Display.Visible.Visible.flowFromSpacing
.. automethod:: Display.Visible.Visible.setFlowFromSpeed
.. automethod:: Display.Visible.Visible.flowFromSpeed
.. automethod:: Display.Visible.Visible.setFlowFromSpread
.. automethod:: Display.Visible.Visible.flowFromSpread
.. automethod:: Display.Visible.Visible.setFlowTo
.. automethod:: Display.Visible.Visible.flowTo
.. automethod:: Display.Visible.Visible.setFlowToColor
.. automethod:: Display.Visible.Visible.flowToColor
.. automethod:: Display.Visible.Visible.setFlowToSpacing
.. automethod:: Display.Visible.Visible.flowToSpacing
.. automethod:: Display.Visible.Visible.setFlowToSpeed
.. automethod:: Display.Visible.Visible.flowToSpeed
.. automethod:: Display.Visible.Visible.setFlowToSpread
.. automethod:: Display.Visible.Visible.flowToSpread

.. _hierarchy:

Changing the visualization of nested objects
--------------------------------------------

The relationships and appearance of objects that are visually nested within each other can be controlled with the following methods.

.. automethod:: Display.Visible.Visible.addChildVisible
.. automethod:: Display.Visible.Visible.removeChildVisible
.. automethod:: Display.Visible.Visible.allChildren
.. automethod:: Display.Visible.Visible.ancestors
.. automethod:: Display.Visible.Visible.rootVisible
.. automethod:: Display.Visible.Visible.setArrangedAxis
.. automethod:: Display.Visible.Visible.setArrangedSpacing
.. automethod:: Display.Visible.Visible.setArrangedWeight
