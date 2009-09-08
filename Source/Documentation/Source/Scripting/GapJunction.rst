.. image:: ../../../Images/GapJunction.png
   :width: 64
   :height: 64
   :align: left

Gap Junctions
=============

.. class:: Network.GapJunction.GapJunction

GapJunction objects represent a gap junction between two :class:`neurites <Network.Neurite.Neurite>` in a :class:`network <Network.Network.Network>`.

Instances of this class are created by using the gapJunctionWith method of :meth:`Neuron <Network.Neuron.Neuron.gapJunctionWith>` and :meth:`Neurite <Network.Neurite.Neurite.gapJunctionWith>` objects.

>>> neuron1.gapJunctionWith(neuron2)

.. automethod:: Network.GapJunction.GapJunction.neurites
 