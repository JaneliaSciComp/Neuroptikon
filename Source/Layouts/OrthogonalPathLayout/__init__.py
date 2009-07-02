'''OrthogonalPathLayout package'''

__version__ = "1.0.0"

# Register this layout
try:
    import Display
    from OrthogonalPathLayout import OrthogonalPathLayout
    Display.registerLayoutClass(OrthogonalPathLayout)
except:
    import sys
    (exceptionType, exceptionValue, exceptionTraceback) = sys.exc_info()
    print 'Could not load the orthogonal path layout (%s)' % (exceptionValue.message)
