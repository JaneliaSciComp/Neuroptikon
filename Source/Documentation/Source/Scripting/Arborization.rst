.. image:: ../../../Images/Arborization.png
   :width: 64
   :height: 64
   :align: left

Arborizations
=============

.. class:: Network.Arborization.Arborization

Arborizations represent a :class:`neurite's <Network.Neurite.Neurite>` arborization within a :class:`region <Network.Region.Region>`.

You create an arborization by messaging a :meth:`neuron <Network.Neuron.Neuron.arborize>` or :meth:`neurite <Network.Neurite.Neurite.arborize>`:

>>> neuron1 = network.createNeuron()
>>> region1 = network.createRegion()
>>> arborization_1_1 = neuron1.arborize(region1)

.. attribute:: Arborization.neurite
	
	The :class:`neurite <Network.Neurite.Neurite>` from which this arborization extends.
	
.. attribute:: Arborization.region
	
	The :class:`region <Network.Region.Region>` being arborized.
