'''Display Inspector package'''

__version__ = "1.0.0"

# Register this inspector
try:
    import Inspection
    from DisplayInspector import DisplayInspector
    Inspection.registerInspectorClass(DisplayInspector)
except:
    pass
