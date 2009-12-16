#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

'''Inspection infrastructure'''

__version__ = "1.0.0"


__inspectorClasses__ = []

def registerInspectorClass(inspectorClass):
    __inspectorClasses__.append(inspectorClass)

def inspectorClasses(*args, **keywordArgs):
    return __inspectorClasses__

# TODO: add API/prefs for permanent inspector registration
