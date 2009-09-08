.. image:: ../../../../Artwork/Neuroptikon.png
   :width: 64
   :height: 64
   :align: left

Networks
========

.. class:: Network.Network.Network
	
Networks are containers for all :class:`objects <Network.Object.Object>` that exist in a neural circuit. 

.. _adding-objects:

Adding objects to the network
-----------------------------

.. automethod:: Network.Network.Network.createMuscle
.. automethod:: Network.Network.Network.createNeuron
.. automethod:: Network.Network.Network.createRegion

.. _finding-objects:

Finding objects in the network
------------------------------

.. automethod:: Network.Network.Network.findMuscle
.. automethod:: Network.Network.Network.findNeuron
.. automethod:: Network.Network.Network.findRegion
.. automethod:: Network.Network.Network.findStimulus

.. automethod:: Network.Network.Network.arborizations
.. automethod:: Network.Network.Network.gapJunctions
.. automethod:: Network.Network.Network.innervations
.. automethod:: Network.Network.Network.muscles
.. automethod:: Network.Network.Network.neurites
.. automethod:: Network.Network.Network.neurons
.. automethod:: Network.Network.Network.pathways
.. automethod:: Network.Network.Network.regions
.. automethod:: Network.Network.Network.stimuli
.. automethod:: Network.Network.Network.synapses

.. _user-defined-network-attributes:

User-Defined Attributes
-----------------------

Networks can have any number of user-defined attributes.  Each attribute has a name, a type and a value.

.. automethod:: Network.Network.Network.addAttribute
.. automethod:: Network.Network.Network.getAttribute
.. automethod:: Network.Network.Network.getAttributes

.. _save-state:

Managing the network's save state
---------------------------------

Networks keep track of changes made to them relative to the last time they were saved.

.. automethod:: Network.Network.Network.setModified
.. automethod:: Network.Network.Network.isModified
