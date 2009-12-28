Interactive Scripting
=====================

Each :doc:`network window <../UserInterface/NetworkWindow>` includes a console that allows you to enter commands to interact with the network being displayed.  Both the biological network itself and the way it is being displayed can be queried and/or manipulated. The following commands give you access to the root :class:`network <network.network.Network>` and :class:`display <display.display.Display>` objects as well as the :class:`library <library.library.Library>`.

=======  =================================================================================
Object   Description
=======  =================================================================================
display  the :class:`display <display.display.Display>` object managing the visualization.
network  the :class:`network <network.network.Network>` being displayed.
=======  =================================================================================

When a script is run via File > Run Script the current working directory is set to directory containing the script file.  This allows simple access to other files or scripts in the same directory, e.g. "textFile = open('file.txt')" would open a text file stored with the script.  Scripts can also query the __file__ local variable to get the full path of their location.

There is also an application-wide console that can be used to create new networks or do multi-network scripting.

==============  =============================================================================
Command         Description
==============  =============================================================================
createNetwork   creates a new :class:`network <network.network.Network>`.
displayNetwork  opens a new visualization for the :class:`network <network.network.Network>`.
openNetwork     opens a previously saved :class:`network <network.network.Network>` and any of its :class:`displays <display.display.Display>`.
networks        the list of all existing :class:`networks <network.network.Network>`.
layouts         a dictionary of known :class:`Layout <display.layout.Layout>` sub-classes keyed by class name.
library         the global :class:`library <library.library.Library>` object.
shapes          a dictionary of known :class:`Shape <display.shape.Shape>` sub-classes keyed by class name.
==============  =============================================================================
