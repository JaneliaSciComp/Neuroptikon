.. image:: ../../../Images/Innervation.png
   :width: 64
   :height: 64
   :align: left

Innervations
============

.. class:: Network.Innervation.Innervation

Innervations represent a :class:`neurite's <Network.Neurite.Neurite>` connection to a :class:`muscle <Network.Muscle.Muscle>`.

Create an innervation by messaging a :meth:`neuron <Network.Neuron.Neuron.innervate>` or :meth:`neurite <Network.Neurite.Neurite.innervate>`:

>>> neuron1 = network.createNeuron()
>>> muscle1 = network.createMuscle()
>>> innervation_1_1 = neuron1.innervate(muscle1)

.. attribute:: Innervation.neurite
	
	The :class:`neurite <Network.Neurite.Neurite>` doing the innervating.
	
.. attribute:: Innervation.muscle
	
	The :class:`muscle <Network.Muscle.Muscle>` being innervated.
