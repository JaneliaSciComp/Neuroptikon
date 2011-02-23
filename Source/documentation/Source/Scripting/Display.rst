.. image:: ../../../../Artwork/Neuroptikon.png
   :width: 64
   :height: 64
   :align: left

Displays
========

.. class:: display.display.Display

Displays allow the :ref:`visualization <global>` of networks.  Each display can :ref:`visualize <specific>` any number of objects from a single network.  By default all objects added to the network are visualized but this can be also be managed :ref:`manually <manual>`.

Multiple displays can visualize the same network at the same time.  By default the :ref:`selection <selection>` is synchronized between displays so selecting an object in one display will select the corresponding object in all other displays.  This can be disabled by calling :meth:`setSynchronizeDisplays(False) <network.network.Network.setSynchronizeDisplays>` on the network.

You should never create an instance of this class directly.  Instances are automatically created when you open a new window either via :menuselection:`File --> New Network` or by calling displayNetwork() in a :doc:`console <Console>` or script.

.. _global:

Changing the visualization
--------------------------

Use the following methods to change the settings of the entire visualization.

.. automethod:: display.display.Display.setBackgroundColor
.. automethod:: display.display.Display.setLabelsFloatOnTop
.. automethod:: display.display.Display.labelsFloatOnTop
.. automethod:: display.display.Display.setShowFlow
.. automethod:: display.display.Display.showFlow
.. automethod:: display.display.Display.setShowNeuronNames
.. automethod:: display.display.Display.showNeuronNames
.. automethod:: display.display.Display.setShowRegionNames
.. automethod:: display.display.Display.showRegionNames
.. automethod:: display.display.Display.setUseGhosts
.. automethod:: display.display.Display.useGhosts
.. automethod:: display.display.Display.setGhostingOpacity
.. automethod:: display.display.Display.ghostingOpacity
.. automethod:: display.display.Display.setUseMouseOverSelecting
.. automethod:: display.display.Display.useMouseOverSelecting
.. automethod:: display.display.Display.setSelectionHighlightDepth
.. automethod:: display.display.Display.selectionHighlightDepth
.. automethod:: display.display.Display.setHighlightOnlyWithinSelection
.. automethod:: display.display.Display.highlightOnlyWithinSelection

.. _specific:

Changing the visualization of network objects
---------------------------------------------

Use the following methods to change the settings for individual objects in the visualization.

.. automethod:: display.display.Display.setVisibleColor
.. automethod:: display.display.Display.setVisibleOpacity
.. automethod:: display.display.Display.setVisiblePosition
.. automethod:: display.display.Display.setVisibleRotation
.. automethod:: display.display.Display.setVisibleShape
.. automethod:: display.display.Display.setVisibleSize
.. automethod:: display.display.Display.setVisibleTexture
.. automethod:: display.display.Display.setVisibleWeight
.. automethod:: display.display.Display.setLabel
.. automethod:: display.display.Display.setLabelColor
.. automethod:: display.display.Display.setLabelPosition

.. automethod:: display.display.Display.visiblesForObject

.. _camera:

Changing how the visualization is viewed
----------------------------------------

Use the following methods to alter how the virtual camera looks at the objects in the visualization.

.. automethod:: display.display.Display.resetView
.. automethod:: display.display.Display.zoomToFit
.. automethod:: display.display.Display.zoomToSelection
.. automethod:: display.display.Display.zoomIn
.. automethod:: display.display.Display.zoomOut
.. automethod:: display.display.Display.setViewDimensions
.. automethod:: display.display.Display.setOrthoViewPlane
.. automethod:: display.display.Display.setUseStereo

.. _selection:

Selection
---------

Each display keeps a list of objects that are currently selected.  These objects are visually highlighted in the display.  If a single object is selected then the connecting objects are also highlighted.  If multiple objects are selected than any connections between them are higlighted.

.. automethod:: display.display.Display.selectObjects
.. automethod:: display.display.Display.selectObject
.. automethod:: display.display.Display.selectAll
.. automethod:: display.display.Display.selectedObjects
.. automethod:: display.display.Display.objectIsSelected

.. _connections:

Changing the visualization of connections
-----------------------------------------

The appearance of connections between objects can be modified with the following methods.

.. automethod:: display.display.Display.setVisiblePath
.. automethod:: display.display.Display.setVisibleFlowFrom
.. automethod:: display.display.Display.setVisibleFlowTo

You can also globally change the appearance of connections for those that haven't specified their own appearance.

.. automethod:: display.display.Display.setDefaultFlowColor
.. automethod:: display.display.Display.setDefaultFlowSpacing
.. automethod:: display.display.Display.setDefaultFlowSpeed
.. automethod:: display.display.Display.setDefaultFlowSpread

.. _nesting:

Changing the visualization of nested objects
--------------------------------------------

The appearance of objects that are visually nested within each other can be controlled with the following methods.

.. automethod:: display.display.Display.setArrangedAxis
.. automethod:: display.display.Display.setArrangedSpacing
.. automethod:: display.display.Display.setArrangedWeight

.. _manual:

Manually visualizing objects
----------------------------

By default any object added to the display's network is automatically visualized.  However you can set the display's autoVisualize attribute to False and then choose which parts of the network should be visualized.

.. automethod:: display.display.Display.visualizeObject
.. automethod:: display.display.Display.removeObject
.. automethod:: display.display.Display.removeVisible

.. _misc:

Miscellaneous methods
---------------------

.. automethod:: display.display.Display.saveViewAsImage
