.. image:: ../../../../Artwork/Neuroptikon.png
   :width: 64
   :height: 64
   :align: left

Network objects
===============

.. class:: network.object.Object

The Object class is the base class for every object in a :class:`network <network.network.Network>`.  Object's can have names, abbreviations and/or descriptions.  Any number of :ref:`user-defined attributes <user-defined-attributes>` or :ref:`external stimuli <stimuli>` can be added to an object.  The :ref:`connectivity <connectivity>` of objects can also be investigated.

The sub-classes of Object are:

* :class:`Arborization <network.arborization.Arborization>`
* :class:`GapJunction <network.gap_junction.GapJunction>`
* :class:`Innervation <network.innervation.Innervation>`
* :class:`Muscle <network.muscle.Muscle>`
* :class:`Neurite <network.neurite.Neurite>`
* :class:`Neuron <network.neuron.Neuron>`
* :class:`Pathway <network.pathway.Pathway>`
* :class:`Region <network.region.Region>`
* :class:`Stimulus <network.stimulus.Stimulus>`
* :class:`Synapse <network.synapse.Synapse>`

.. _connectivity:

Connectivity
------------

There are a variety of methods for investigating the connections to and from objects.

.. automethod:: network.object.Object.connections
.. automethod:: network.object.Object.inputs
.. automethod:: network.object.Object.outputs


.. _stimuli:

External Stimulation
--------------------

Inputs from outside of the network are represented with :class:`Stimuli <network.stimulus.Stimulus>` objects.

.. automethod:: network.neuro_object.NeuroObject.stimulate


.. _user-defined-attributes:

User-Defined Attributes
-----------------------

Each object in a network can have any number of user-defined attributes.  Each attribute has a name, a type and a value.

.. automethod:: network.object.Object.addAttribute
.. automethod:: network.object.Object.getAttribute
.. automethod:: network.object.Object.getAttributes


.. _visualization:

Visualization
-------------

Each object provides a default set of visualization parameters.  These parameters are used when auto-visualization is enabled (the default) otherwise the parameters can be queried, modified if desired and then used to manually visualize the object.

.. automethod:: network.object.Object.defaultVisualizationParams
