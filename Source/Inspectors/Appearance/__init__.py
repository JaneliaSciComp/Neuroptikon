'''Appearance Inspector package'''

__version__ = "1.0.0"

# Register this inspector
try:
    import Inspection
    from AppearanceInspector import AppearanceInspector
    Inspection.registerInspectorClass(AppearanceInspector)
except:
    pass
