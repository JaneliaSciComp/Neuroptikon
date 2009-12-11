.. image:: ../../../Images/Synapse.png
   :width: 64
   :height: 64
   :align: left

Synapses
========

.. class:: network.synapse.Synapse

A Synapse object represents a chemical synapse between a single pre-synaptic neurite and one or more post-synaptic neurites.

Instances of this class are created by using the synapseOn method of :meth:`Neuron <network.neuron.Neuron.synapseOn>` and :meth:`Neurite <network.neurite.Neurite.synapseOn>` objects. 

>>> neuron1.synapseOn(neuron2, activation = 'excitatory')

.. attribute:: network.synaspe.Synapse.activation

	The activation of the synapse, one of None (meaning unknown), 'excitatory' or 'inhibitory'

.. attribute:: network.synaspe.Synapse.preSynapticNeurite

	The :class:`neurite <network.neurite.Neurite>` that is pre-synaptic.
	
.. attribute:: network.synaspe.Synapse.postSynapticNeurites

	The list of :class:`neurites <network.neurite.Neurite>` that are post-synaptic.
