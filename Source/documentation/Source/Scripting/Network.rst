.. image:: ../../../../Artwork/Neuroptikon.png
   :width: 64
   :height: 64
   :align: left

Networks
========

.. class:: network.network.Network
	
Networks are containers for all :class:`objects <network.object.Object>` that exist in a neural circuit. 

.. _adding-objects:

Adding objects to the network
-----------------------------

.. automethod:: network.network.Network.createMuscle
.. automethod:: network.network.Network.createNeuron
.. automethod:: network.network.Network.createRegion

.. _finding-objects:

Finding objects in the network
------------------------------

.. automethod:: network.network.Network.findMuscle
.. automethod:: network.network.Network.findNeuron
.. automethod:: network.network.Network.findRegion
.. automethod:: network.network.Network.findStimulus

.. automethod:: network.network.Network.arborizations
.. automethod:: network.network.Network.gapJunctions
.. automethod:: network.network.Network.innervations
.. automethod:: network.network.Network.muscles
.. automethod:: network.network.Network.neurites
.. automethod:: network.network.Network.neurons
.. automethod:: network.network.Network.pathways
.. automethod:: network.network.Network.regions
.. automethod:: network.network.Network.stimuli
.. automethod:: network.network.Network.synapses

.. automethod:: network.network.Network.shortestPath

.. _removing-objects:

Removing objects from the network
---------------------------------

.. automethod:: network.network.Network.removeObject
.. automethod:: network.network.Network.removeAllObjects

.. _weighting:

Weighting
---------

There are various algorithms that can be used from the NetworkX library that can take advantage of "weighted" connections between objects in the network, e.g. finding a shortest path.  You can specify a weighting function for each network or let each object be weighted equally.

.. automethod:: network.network.Network.setWeightingFunction
.. automethod:: network.network.Network.weightingFunction
.. automethod:: network.network.Network.weightOfObject

.. _user-defined-network-attributes:

User-Defined Attributes
-----------------------

Networks can have any number of user-defined attributes.  Each attribute has a name, a type and a value.

.. automethod:: network.network.Network.addAttribute
.. automethod:: network.network.Network.getAttribute
.. automethod:: network.network.Network.getAttributes

.. _save-state:

Managing the network's save state
---------------------------------

Networks keep track of changes made to them relative to the last time they were saved.

.. automethod:: network.network.Network.setModified
.. automethod:: network.network.Network.isModified
