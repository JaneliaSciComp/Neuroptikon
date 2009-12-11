import os, sys

__version__ = "1.0.0"

# Import all packages and modules within this package.
try:
    layoutsDir = os.path.dirname(__file__)
    for fileName in os.listdir(layoutsDir):
        layoutName, extension = os.path.splitext(fileName)
        try:
            if os.path.exists(os.path.join(layoutsDir, fileName, '__init__.py')):
                # Import a sub-package.  The sub-package is responsible for importing any modules containing layouts.
                exec('import ' + layoutName)
            elif fileName != '__init__.py' and extension == '.py':
                # Import a module.
                exec('import ' + layoutName)
        except:
            (exceptionType, exceptionValue, exceptionTraceback) = sys.exc_info()
            print 'Could not load layout %s (%s)' % (layoutName, str(exceptionValue) + ' (' + exceptionType.__name__ + ')')
except:
    (exceptionType, exceptionValue, exceptionTraceback) = sys.exc_info()
    print 'Could not load layouts (' + str(exceptionValue) + ' (' + exceptionType.__name__ + ')' + ')'
