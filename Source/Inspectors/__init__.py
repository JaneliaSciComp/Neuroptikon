#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

'''
Inspectors package
'''

import os, sys

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
