Interactive Scripting
=====================

Each :doc:`network window <../UserInterface/NetworkWindow>` includes a console that allows you to enter commands to interact with the network being displayed.  Both the biological network itself and the way it is being displayed can be queried and/or manipulated. The following commands give you access to the root :class:`network <Network.Network.Network>` and :class:`display <Display.Display.Display>` objects as well as the :class:`library <Library.Library.Library>`.

=======  =================================================================================
Object   Description
=======  =================================================================================
display  the :class:`display <Display.Display.Display>` object managing the visualization.
network  the :class:`network <Network.Network.Network>` being displayed.
=======  =================================================================================

There is also an application-wide console that can be used to create new networks or do multi-network scripting.

==============  =============================================================================
Command         Description
==============  =============================================================================
createNetwork   creates a new :class:`network <Network.Network.Network>`.
displayNetwork  opens a new visualization for the :class:`network <Network.Network.Network>`.
networks        the list of all existing :class:`networks <Network.Network.Network>`.
layouts         a dictionary of known :class:`Layout <Display.Layout.Layout>` sub-classes keyed by class name.
library         the global :class:`library <Library.Library.Library>` object.
shapes          a dictionary of known :class:`Shape <Display.Shape.Shape>` sub-classes keyed by class name.
==============  =============================================================================
