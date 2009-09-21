.. image:: ../../../Images/Neurite.png
   :width: 64
   :height: 64
   :align: left

Neurites
========

.. class:: Network.Neurite.Neurite

Neurites represent cellular projections from the soma or other neurites of a :class:`neuron <Network.Neuron.Neuron>`.

You create a neurite by messaging a :meth:`neuron <Network.Neuron.Neuron.extendNeurite>` or :meth:`neurite <Network.Neurite.Neurite.extendNeurite>`:

>>> neurite1 = neuron.extendNeurite(...)
>>> neurite2 = neurite1.extendNeurite(...)

.. automethod:: Network.Neurite.Neurite.neuron

.. automethod:: Network.Neurite.Neurite.extendNeurite
.. automethod:: Network.Neurite.Neurite.neurites

.. automethod:: Network.Neurite.Neurite.arborize
.. automethod:: Network.Neurite.Neurite.gapJunctionWith
.. automethod:: Network.Neurite.Neurite.innervate
.. automethod:: Network.Neurite.Neurite.synapseOn

.. automethod:: Network.Neurite.Neurite.arborizations
.. automethod:: Network.Neurite.Neurite.gapJunctions
.. automethod:: Network.Neurite.Neurite.innervations
.. automethod:: Network.Neurite.Neurite.synapses

.. automethod:: Network.Neurite.Neurite.connections
.. automethod:: Network.Neurite.Neurite.inputs
.. automethod:: Network.Neurite.Neurite.outputs

.. automethod:: Network.Neurite.Neurite.setPathway
.. automethod:: Network.Neurite.Neurite.pathway
