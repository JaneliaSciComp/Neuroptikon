import os, sys
import Display
from Display.Layout import Layout

__version__ = "1.0.0"

# Import all packages and modules within this package.
try:
    layoutsDir = os.path.dirname(__file__)
    for fileName in os.listdir(layoutsDir):
        layoutName, extension = os.path.splitext(fileName)
        try:
            if os.path.exists(os.path.join(layoutsDir, fileName, '__init__.py')):
                # Import a sub-package.  The sub-package is responsible for registering any layouts it contains.
                exec('import ' + layoutName)
            elif fileName != '__init__.py' and extension == '.py':
                # Import a module and register the class if it is a layout.
                exec('from ' + layoutName + ' import ' + layoutName)
                layoutClass = eval(layoutName)
                if isinstance(layoutClass, Layout.__class__) and layoutClass.shouldBeRegistered():
                    Display.registerLayoutClass(layoutClass)
        except:
            (exceptionType, exceptionValue, exceptionTraceback) = sys.exc_info()
            print 'Could not load layout %s (%s)' % (layoutName, str(exceptionValue) + ' (' + exceptionType.__name__ + ')')
except:
    (exceptionType, exceptionValue, exceptionTraceback) = sys.exc_info()
    print 'Could not load layouts (' + str(exceptionValue) + ' (' + exceptionType.__name__ + ')' + ')'
