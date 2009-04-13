'''Path Inspector package'''

__version__ = "1.0.0"

# Register this inspector
try:
    import Inspection
    from PathInspector import PathInspector
    Inspection.registerInspectorClass(PathInspector)
except:
    pass
