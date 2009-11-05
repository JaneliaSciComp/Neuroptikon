import os, sys
import Display
from Display.Shape import Shape

__version__ = "1.0.0"

# Import all packages and modules within this package.
try:
    shapesDir = os.path.dirname(__file__)
    for fileName in os.listdir(shapesDir):
        shapeName, extension = os.path.splitext(fileName)
        try:
            if os.path.exists(os.path.join(shapesDir, fileName, '__init__.py')):
                # Import a sub-package.  The sub-package is responsible for registering any shapes it contains.
                exec('import ' + shapeName)
            elif fileName != '__init__.py' and extension == '.py':
                # Import a module and register the class if it is a shape.
                exec('from ' + shapeName + ' import ' + shapeName)
                shapeClass = eval(shapeName)
                if isinstance(shapeClass, Shape.__class__) and shapeClass.shouldBeRegistered():
                    Display.registerShapeClass(shapeClass)
        except:
            (exceptionType, exceptionValue, exceptionTraceback) = sys.exc_info()
            print 'Could not load shape %s (%s)' % (shapeName, str(exceptionValue) + ' (' + exceptionType.__name__ + ')')
except:
    (exceptionType, exceptionValue, exceptionTraceback) = sys.exc_info()
    print 'Could not load shapes (' + str(exceptionValue) + ' (' + exceptionType.__name__ + ')' + ')'
