'''Attributes Inspector package'''

__version__ = "1.0.0"

# Register this inspector
try:
    import Inspection
    from AttributesInspector import AttributesInspector
    Inspection.registerInspectorClass(AttributesInspector)
except:
    pass
