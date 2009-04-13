'''Inspectors package'''

import os, sys
import Inspection
from Inspection.Inspector import Inspector

__version__ = "1.0.0"

# Import all packages and modules within this package.
try:
    inspectorsDir = os.path.dirname(__file__)
    for fileName in os.listdir(inspectorsDir):
        inspectorName, extension = os.path.splitext(fileName)
        if os.path.exists(inspectorsDir + os.sep + fileName + os.sep + '__init__.py'):
            # Import a sub-package.  The sub-package is responsible for registering any inspectors it contains.
            exec('import ' + inspectorName)
        elif fileName != '__init__.py' and extension == '.py':
            # Import a module and register the class if it is an inspector.
            exec('from ' + inspectorName + ' import ' + inspectorName)
            inspectorClass = eval(inspectorName)
            if isinstance(inspectorClass, Inspector.__class__) and inspectorClass.shouldBeRegistered():
                Inspection.registerInspectorClass(inspectorClass)
except:
    pass
