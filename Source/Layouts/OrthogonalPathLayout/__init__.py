'''Path Routing package'''

__version__ = "1.0.0"

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
