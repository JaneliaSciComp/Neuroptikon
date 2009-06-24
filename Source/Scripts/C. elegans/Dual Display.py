import os, os.path

# Open the "connectivity" visualization in the current display.
execfile(os.path.dirname(__file__) + os.sep + 'Connectivity.py')

# Open the "physical layout" visualization in a second display.
scriptGlobals = globals()
scriptGlobals['display'] = displayNetwork(network)
execfile(os.path.dirname(__file__) + os.sep + 'Physical Layout.py', scriptGlobals, locals())

# By default the selections of the two display will be synchronized.
