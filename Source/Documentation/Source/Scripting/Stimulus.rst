.. image:: ../../../Images/Stimulus.png
   :width: 64
   :height: 64
   :align: left

Stimuli
=======

.. class:: Network.Stimulus.Stimulus

Stimulus objects represent external stimulation of objects in the network.

Stimulii are created by calling the :meth:`stimulate <Network.Object.Object.stimulate>` method on an object in the network.  The modality argument must be a :class:`modality <Library.Modality.Modality>` from the library or None to indicate unknown modality.

>>> stimulus = neuron1.stimulate(modality = library.modality('light'))

.. attribute:: Network.Stimulus.Stimulus.modality

	The :class:`modality <Library.Modality.Modality>` of the stimulus or None (unknown).

.. attribute:: Network.Stimulus.Stimulus.target

	The :class:`target <Network.Object.Object>` of the stimulus.