# Open the "connectivity" visualization in the current display.
execfile('Connectivity.py')

# Open the "physical layout" visualization in a second display.
scriptGlobals = globals()
scriptGlobals['display'] = displayNetwork(network)
execfile('Physical Layout.py', scriptGlobals, locals())

# By default the selections of the two display will be synchronized.
