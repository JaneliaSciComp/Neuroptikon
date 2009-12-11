import os, sys

__version__ = "1.0.0"

# Import all packages and modules within this package.
try:
    shapesDir = os.path.dirname(__file__)
    for fileName in os.listdir(shapesDir):
        shapeName, extension = os.path.splitext(fileName)
        try:
            if os.path.exists(os.path.join(shapesDir, fileName, '__init__.py')):
                # Import a sub-package.  The sub-package is responsible for registering any modules containing shapes.
                exec('import ' + shapeName)
            elif fileName != '__init__.py' and extension == '.py':
                # Import a module.
                exec('import ' + shapeName)
        except:
            (exceptionType, exceptionValue, exceptionTraceback) = sys.exc_info()
            print 'Could not load shape %s (%s)' % (shapeName, str(exceptionValue) + ' (' + exceptionType.__name__ + ')')
except:
    (exceptionType, exceptionValue, exceptionTraceback) = sys.exc_info()
    print 'Could not load shapes (' + str(exceptionValue) + ' (' + exceptionType.__name__ + ')' + ')'
