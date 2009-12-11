.. image:: ../../../../Artwork/Neuroptikon.png
   :width: 64
   :height: 64
   :align: left

Visualized Objects
==================

.. class:: display.visible.Visible

Instances of this class map a :class:`network object <network.object.Object>` (neurion, region, etc.) to a specific :class:`display <display.display.Display>`.  They capture all of the attributes needed to render the object.

You should never create an instance of this class directly.  Instead use the value returned by calling :meth:`visualizeObject() <display.display.Display.visualizeObject>` on a display.  If you want to have a purely visual object that does not represent any object in the biological network then pass None to visualizeObject().

.. _geometry:

Changing the geometry of a visualized object
--------------------------------------------

Use the following methods to change the settings for individual objects in the visualization.

.. automethod:: display.visible.Visible.setPosition
.. automethod:: display.visible.Visible.offsetPosition
.. automethod:: display.visible.Visible.position
.. automethod:: display.visible.Visible.worldPosition
.. automethod:: display.visible.Visible.setPositionIsFixed
.. automethod:: display.visible.Visible.positionIsFixed
.. automethod:: display.visible.Visible.setSize
.. automethod:: display.visible.Visible.size
.. automethod:: display.visible.Visible.worldSize
.. automethod:: display.visible.Visible.setSizeIsFixed
.. automethod:: display.visible.Visible.sizeIsFixed
.. automethod:: display.visible.Visible.setSizeIsAbsolute
.. automethod:: display.visible.Visible.sizeIsAbsolute

.. _appearance:

Changing the appearance of a visualized object
----------------------------------------------

.. automethod:: display.visible.Visible.setColor
.. automethod:: display.visible.Visible.color
.. automethod:: display.visible.Visible.setOpacity
.. automethod:: display.visible.Visible.opacity
.. automethod:: display.visible.Visible.setShape
.. automethod:: display.visible.Visible.shape
.. automethod:: display.visible.Visible.setTexture
.. automethod:: display.visible.Visible.texture
.. automethod:: display.visible.Visible.setTextureScale
.. automethod:: display.visible.Visible.textureScale
.. automethod:: display.visible.Visible.setWeight
.. automethod:: display.visible.Visible.weight

.. _label:

Changing the label of a visualized object
-----------------------------------------

Use the following methods to change the settings for the label that adorns a visualized object.

.. automethod:: display.visible.Visible.setLabel
.. automethod:: display.visible.Visible.label
.. automethod:: display.visible.Visible.setLabelColor
.. automethod:: display.visible.Visible.labelColor
.. automethod:: display.visible.Visible.setLabelPosition
.. automethod:: display.visible.Visible.labelPosition

.. _connection:

Changing the visualization of a connection
------------------------------------------

The end and mid-points of a connection between objects can be modified with the following methods.

.. automethod:: display.visible.Visible.setPathEndPoints
.. automethod:: display.visible.Visible.pathEndPoints
.. automethod:: display.visible.Visible.setPathMidPoints
.. automethod:: display.visible.Visible.pathMidPoints
.. automethod:: display.visible.Visible.isPath

The appearance of the connection's flow can also be customized.  If None is passed to any of the methods then the default value for the display will be used instead.

.. automethod:: display.visible.Visible.setFlowFrom
.. automethod:: display.visible.Visible.flowFrom
.. automethod:: display.visible.Visible.setFlowFromColor
.. automethod:: display.visible.Visible.flowFromColor
.. automethod:: display.visible.Visible.setFlowFromSpacing
.. automethod:: display.visible.Visible.flowFromSpacing
.. automethod:: display.visible.Visible.setFlowFromSpeed
.. automethod:: display.visible.Visible.flowFromSpeed
.. automethod:: display.visible.Visible.setFlowFromSpread
.. automethod:: display.visible.Visible.flowFromSpread
.. automethod:: display.visible.Visible.setFlowTo
.. automethod:: display.visible.Visible.flowTo
.. automethod:: display.visible.Visible.setFlowToColor
.. automethod:: display.visible.Visible.flowToColor
.. automethod:: display.visible.Visible.setFlowToSpacing
.. automethod:: display.visible.Visible.flowToSpacing
.. automethod:: display.visible.Visible.setFlowToSpeed
.. automethod:: display.visible.Visible.flowToSpeed
.. automethod:: display.visible.Visible.setFlowToSpread
.. automethod:: display.visible.Visible.flowToSpread

.. _hierarchy:

Changing the visualization of nested objects
--------------------------------------------

The relationships and appearance of objects that are visually nested within each other can be controlled with the following methods.

.. automethod:: display.visible.Visible.addChildVisible
.. automethod:: display.visible.Visible.removeChildVisible
.. automethod:: display.visible.Visible.descendants
.. automethod:: display.visible.Visible.ancestors
.. automethod:: display.visible.Visible.rootVisible
.. automethod:: display.visible.Visible.setArrangedAxis
.. automethod:: display.visible.Visible.setArrangedSpacing
.. automethod:: display.visible.Visible.setArrangedWeight
