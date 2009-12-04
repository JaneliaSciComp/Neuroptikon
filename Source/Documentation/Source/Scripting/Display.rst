.. image:: ../../../../Artwork/Neuroptikon.png
   :width: 64
   :height: 64
   :align: left

Displays
========

.. class:: Display.Display.Display

Displays allow the :ref:`visualization <global>` of networks.  Each display can :ref:`visualize <specific>` any number of objects from a single network.  By default all objects added to the network are visualized but this can be also be managed :ref:`manually <manual>`.

Multiple displays can visualize the same network at the same time.  By default the :ref:`selection <selection>` is synchronized between displays so selecting an object in one display will select the corresponding object in all other displays.  This can be disabled by calling :meth:`setSynchronizeDisplays(False) <Network.Network.Network.setSynchronizeDisplays>` on the network.

You should never create an instance of this class directly.  Instances are automatically created when you open a new window either via :menuselection:`File --> New Network` or by calling displayNetwork() in a :doc:`console <Console>` or script.

.. _global:

Changing the visualization
--------------------------

Use the following methods to change the settings of the entire visualization.

.. automethod:: Display.Display.Display.setBackgroundColor
.. automethod:: Display.Display.Display.setLabelsFloatOnTop
.. automethod:: Display.Display.Display.labelsFloatOnTop
.. automethod:: Display.Display.Display.setShowFlow
.. automethod:: Display.Display.Display.showFlow
.. automethod:: Display.Display.Display.setShowNeuronNames
.. automethod:: Display.Display.Display.showNeuronNames
.. automethod:: Display.Display.Display.setShowRegionNames
.. automethod:: Display.Display.Display.showRegionNames
.. automethod:: Display.Display.Display.setUseGhosts
.. automethod:: Display.Display.Display.useGhosts
.. automethod:: Display.Display.Display.setGhostingOpacity
.. automethod:: Display.Display.Display.ghostingOpacity
.. automethod:: Display.Display.Display.setUseMouseOverSelecting
.. automethod:: Display.Display.Display.useMouseOverSelecting

.. _specific:

Changing the visualization of network objects
---------------------------------------------

Use the following methods to change the settings for individual objects in the visualization.

.. automethod:: Display.Display.Display.setVisibleColor
.. automethod:: Display.Display.Display.setVisibleOpacity
.. automethod:: Display.Display.Display.setVisiblePosition
.. automethod:: Display.Display.Display.setVisibleRotation
.. automethod:: Display.Display.Display.setVisibleShape
.. automethod:: Display.Display.Display.setVisibleSize
.. automethod:: Display.Display.Display.setVisibleTexture
.. automethod:: Display.Display.Display.setVisibleWeight
.. automethod:: Display.Display.Display.setLabel
.. automethod:: Display.Display.Display.setLabelColor
.. automethod:: Display.Display.Display.setLabelPosition

.. automethod:: Display.Display.Display.visiblesForObject

.. _camera:

Changing how the visualization is viewed
----------------------------------------

Use the following methods to alter how the virtual camera looks at the objects in the visualization.

.. automethod:: Display.Display.Display.resetView
.. automethod:: Display.Display.Display.zoomToFit
.. automethod:: Display.Display.Display.zoomToSelection
.. automethod:: Display.Display.Display.zoomIn
.. automethod:: Display.Display.Display.zoomOut
.. automethod:: Display.Display.Display.setViewDimensions
.. automethod:: Display.Display.Display.setOrthoViewPlane
.. automethod:: Display.Display.Display.setUseStereo

.. _selection:

Selection
---------

Each display keeps a list of objects that are currently selected.  These objects are visually highlighted in the display.  If a single object is selected then the connecting objects are also highlighted.  If multiple objects are selected than any connections between them are higlighted.

.. automethod:: Display.Display.Display.selectObjects
.. automethod:: Display.Display.Display.selectObject
.. automethod:: Display.Display.Display.selectAll
.. automethod:: Display.Display.Display.selectedObjects
.. automethod:: Display.Display.Display.objectIsSelected

.. _connections:

Changing the visualization of connections
-----------------------------------------

The appearance of connections between objects can be modified with the following methods.

.. automethod:: Display.Display.Display.setVisiblePath
.. automethod:: Display.Display.Display.setVisibleFlowFrom
.. automethod:: Display.Display.Display.setVisibleFlowTo

You can also globally change the appearance of connections for those that haven't specified their own appearance.

.. automethod:: Display.Display.Display.setDefaultFlowColor
.. automethod:: Display.Display.Display.setDefaultFlowSpacing
.. automethod:: Display.Display.Display.setDefaultFlowSpeed
.. automethod:: Display.Display.Display.setDefaultFlowSpread

.. _nesting:

Changing the visualization of nested objects
--------------------------------------------

The appearance of objects that are visually nested within each other can be controlled with the following methods.

.. automethod:: Display.Display.Display.setArrangedAxis
.. automethod:: Display.Display.Display.setArrangedSpacing
.. automethod:: Display.Display.Display.setArrangedWeight

.. _manual:

Manually visualizing objects
----------------------------

By default any object added to the display's network is automatically visualized.  However you can set the display's autoVisualize attribute to False and then choose which parts of the network should be visualized.

.. automethod:: Display.Display.Display.visualizeObject
.. automethod:: Display.Display.Display.defaultVisualizationParams
.. automethod:: Display.Display.Display.removeObject
.. automethod:: Display.Display.Display.removeVisible

.. _misc:

Miscellaneous methods
---------------------

.. automethod:: Display.Display.Display.saveViewAsImage
