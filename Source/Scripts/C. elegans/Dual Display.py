"""
This script demonstrates opening two visualizations of the same network.
"""

# Open the "connectivity" visualization in the current display.
execfile('Connectivity.py')

# Don't show the muscles in the original display
display.autoVisualize = False

# Open the "physical layout" visualization in a second display.
scriptGlobals = globals()
scriptGlobals['display'] = displayNetwork(network)
execfile('Physical Layout.py', scriptGlobals, locals())

# Re-enable auto-visualization in case anything else gets added by the user.
display.autoVisualize = True

# By default the selections of the two display will be synchronized.
