'''Inspection infrastructure'''

__version__ = "1.0.0"


__inspectorClasses__ = []

def registerInspectorClass(inspectorClass):
    __inspectorClasses__.append(inspectorClass)

def inspectorClasses(*args, **keywordArgs):
    return __inspectorClasses__

# TODO: add API/prefs for permanent inspector registration
