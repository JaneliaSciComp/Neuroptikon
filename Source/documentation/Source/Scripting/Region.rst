.. image:: ../../../Images/Region.png
   :width: 64
   :height: 64
   :align: left

Regions
=======

.. class:: network.region.Region

Regions represent a physical subset of a nervous system.  They can also be hierarchical with regions nested within other regions.  Regions can also be associated with an entry in one of the :class:`ontologies <library.ontology.Ontology>` in the library.

You create a region by :meth:`messaging <network.network.Network.createRegion>` a :class:`network <network.network.Network>`:

>>> region1 = network.createRegion(...)

.. automethod:: network.region.Region.projectToRegion
