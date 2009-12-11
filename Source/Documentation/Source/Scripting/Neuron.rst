.. image:: ../../../Images/Neuron.png
   :width: 64
   :height: 64
   :align: left

Neurons
=======

.. class:: network.neuron.Neuron

Neurons represent individual neural cells in the :class:`network <network.network.Network>`.

You create a neuron by messaging the network:

>>> neuron1 = network.createNeuron(...)

.. automethod:: network.neuron.Neuron.extendNeurite
.. automethod:: network.neuron.Neuron.neurites

.. automethod:: network.neuron.Neuron.arborize
.. automethod:: network.neuron.Neuron.gapJunctionWith
.. automethod:: network.neuron.Neuron.innervate
.. automethod:: network.neuron.Neuron.synapseOn

.. automethod:: network.neuron.Neuron.arborizations
.. automethod:: network.neuron.Neuron.gapJunctions
.. automethod:: network.neuron.Neuron.innervations
.. automethod:: network.neuron.Neuron.synapses

.. automethod:: network.neuron.Neuron.connections
.. automethod:: network.neuron.Neuron.inputs
.. automethod:: network.neuron.Neuron.outputs

.. automethod:: network.neuron.Neuron.setHasFunction
.. automethod:: network.neuron.Neuron.hasFunction
