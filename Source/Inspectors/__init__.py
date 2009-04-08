'''Inspectors package'''

import os, sys

__version__ = "1.0.0"

try:
    inspectorsDir = os.path.dirname(__file__)
    for fileName in os.listdir(inspectorsDir):
        # TODO: only import if fileName/__init__.py exists
        if os.path.exists(inspectorsDir + os.sep + fileName + os.sep + '__init__.py'):
            inspectorName = os.path.splitext(fileName)[0]
            exec('import ' + inspectorName)
except:
    pass
