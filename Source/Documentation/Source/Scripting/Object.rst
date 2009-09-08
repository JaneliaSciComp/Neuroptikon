.. image:: ../../../../Artwork/Neuroptikon.png
   :width: 64
   :height: 64
   :align: left

Network objects
===============

.. class:: Network.Object.Object

The Object class is the base class for every object in a :class:`network <Network.Network.Network>`.  Object's can have names, abbreviations and/or descriptions.  Any number of :ref:`user-defined attributes <user-defined-attributes>` or :ref:`external stimuli <stimuli>` can be added to an object.  The :ref:`connectivity <connectivity>` of objects can also be investigated.

The sub-classes of Object are:

* :class:`Arborization <Network.Arborization.Arborization>`
* :class:`GapJunction <Network.GapJunction.GapJunction>`
* :class:`Innervation <Network.Innervation.Innervation>`
* :class:`Muscle <Network.Muscle.Muscle>`
* :class:`Neurite <Network.Neurite.Neurite>`
* :class:`Neuron <Network.Neuron.Neuron>`
* :class:`Pathway <Network.Pathway.Pathway>`
* :class:`Region <Network.Region.Region>`
* :class:`Stimulus <Network.Stimulus.Stimulus>`
* :class:`Synapse <Network.Synapse.Synapse>`

.. _connectivity:

Connectivity
------------

There are a variety of methods for investigating the connections to and from objects.

.. automethod:: Network.Object.Object.connections
.. automethod:: Network.Object.Object.inputs
.. automethod:: Network.Object.Object.outputs
.. automethod:: Network.Object.Object.shortestPathTo


.. _stimuli:

External Stimulation
--------------------

Inputs from outside of the network are represented with :class:`Stimuli <Network.Stimulus.Stimulus>` objects.

.. automethod:: Network.Object.Object.stimulate


.. _user-defined-attributes:

User-Defined Attributes
-----------------------

Each object in a network can have any number of user-defined attributes.  Each attribute has a name, a type and a value.

.. automethod:: Network.Object.Object.addAttribute
.. automethod:: Network.Object.Object.getAttribute
.. automethod:: Network.Object.Object.getAttributes
