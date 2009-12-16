#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

'''Path Routing package'''

# Register this layout
try:
	import path_routing
#    import display
#    from path_routing import PathRoutingLayout
#    display.registerLayoutClass(PathRoutingLayout)
except:
    import sys
    (exceptionType, exceptionValue, exceptionTraceback) = sys.exc_info()
    print 'Could not load the  path routing layout (%s)' % (str(exceptionValue) + ' (' + exceptionType.__name__ + ')')
