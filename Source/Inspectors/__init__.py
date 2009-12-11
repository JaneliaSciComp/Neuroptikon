'''Inspectors package'''

import os, sys

__version__ = "1.0.0"

# Import all packages and modules within this package.
try:
    inspectorsDir = os.path.dirname(__file__)
    for fileName in os.listdir(inspectorsDir):
        inspectorName, extension = os.path.splitext(fileName)
        if os.path.exists(inspectorsDir + os.sep + fileName + os.sep + '__init__.py'):
            # Import a sub-package.  The sub-package is responsible for importing any modules containing inspectors.
            exec('import ' + inspectorName)
        elif fileName != '__init__.py' and extension == '.py':
            # Import a module.
            exec('import ' + inspectorName)
except:
    pass
