.. image:: ../../../Images/Stimulus.png
   :width: 64
   :height: 64
   :align: left

Stimuli
=======

.. class:: network.stimulus.Stimulus

Stimulus objects represent external stimulation of objects in the network.

Stimulii are created by calling the :meth:`stimulate <network.neuro_object.NeuroObject.stimulate>` method on an object in the network.  The modality argument must be a :class:`modality <library.modality.Modality>` from the library or None to indicate unknown modality.

>>> stimulus = neuron1.stimulate(modality = library.modality('light'))

.. attribute:: network.stimulus.Stimulus.modality

	The :class:`modality <library.modality.Modality>` of the stimulus or None (unknown).

.. attribute:: network.stimulus.Stimulus.target

	The :class:`target <network.neuro_object.NeuroObject>` of the stimulus.