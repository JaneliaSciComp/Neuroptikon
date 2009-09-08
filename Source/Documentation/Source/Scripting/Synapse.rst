.. image:: ../../../Images/Synapse.png
   :width: 64
   :height: 64
   :align: left

Synapses
========

.. class:: Network.Synapse.Synapse

A Synapse object represents a chemical synapse between a single pre-synaptic neurite and one or more post-synaptic neurites.

Instances of this class are created by using the synapseOn method of :meth:`Neuron <Network.Neuron.Neuron.synapseOn>` and :meth:`Neurite <Network.Neurite.Neurite.synapseOn>` objects. 

>>> neuron1.synapseOn(neuron2, activation = 'excitatory')

.. attribute:: Synapse.activation

	The activation of the synapse, one of None (meaning unknown), 'excitatory' or 'inhibitory'

.. attribute:: Synapse.preSynapticNeurite

	The :class:`neurite <Network.Neurite.Neurite>` that is pre-synaptic.
	
.. attribute:: Synapse.postSynapticNeurites

	The list of :class:`neurites <Network.Neurite.Neurite>` that are post-synaptic.
