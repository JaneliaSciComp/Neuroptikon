.. image:: ../../../Images/Pathway.png
   :width: 64
   :height: 64
   :align: left

Pathways
========

.. class:: network.pathway.Pathway

Pathways connect pairs of :class:`regions <network.region.Region>`.  They consist of bundles of :class:`neurites <network.neurite.Neurite>` which can be optionally specified.

You create a pathway by :meth:`messaging <network.region.Region.projectToRegion>` one of the regions:

>>> pathway_1_2 = region1.projectToRegion(region2)

.. automethod:: network.pathway.Pathway.regions

.. attribute:: network.pathway.Pathway.region1Projects

	Indicates whether the first region in :meth:`regions <network.pathway.Pathway.regions>` sends information to the second.  One of True, False or None (unknown).

.. attribute:: network.pathway.Pathway.region1Activation

	Indicates how the first region in :meth:`regions <network.pathway.Pathway.regions>` is being activated by the pathway.  One of 'excitatory', 'inhibitory' or None (unknown).

.. attribute:: network.pathway.Pathway.region2Projects

	Indicates whether the second region in :meth:`regions <network.pathway.Pathway.regions>` sends information to the first.  One of True, False or None (unknown).

.. attribute:: network.pathway.Pathway.region2Activation

	Indicates how the second region in :meth:`regions <network.pathway.Pathway.regions>` is being activated by the pathway.  One of 'excitatory', 'inhibitory' or None (unknown).

.. automethod:: network.pathway.Pathway.addNeurite
.. automethod:: network.pathway.Pathway.removeNeurite
.. automethod:: network.pathway.Pathway.neurites
