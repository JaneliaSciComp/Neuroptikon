.. image:: ../../../Images/Neuron.png
   :width: 64
   :height: 64
   :align: left

Neurons
=======

.. class:: Network.Neuron.Neuron

Neurons represent individual neural cells in the :class:`network <Network.Network.Network>`.

You create a neuron by messaging the network:

>>> neuron1 = network.createNeuron(...)

.. automethod:: Network.Neuron.Neuron.extendNeurite
.. automethod:: Network.Neuron.Neuron.neurites

.. automethod:: Network.Neuron.Neuron.arborize
.. automethod:: Network.Neuron.Neuron.gapJunctionWith
.. automethod:: Network.Neuron.Neuron.innervate
.. automethod:: Network.Neuron.Neuron.synapseOn

.. automethod:: Network.Neuron.Neuron.arborizations
.. automethod:: Network.Neuron.Neuron.gapJunctions
.. automethod:: Network.Neuron.Neuron.innervations
.. automethod:: Network.Neuron.Neuron.synapses

.. automethod:: Network.Neuron.Neuron.connections
.. automethod:: Network.Neuron.Neuron.inputs
.. automethod:: Network.Neuron.Neuron.outputs

.. automethod:: Network.Neuron.Neuron.setHasFunction
.. automethod:: Network.Neuron.Neuron.hasFunction
