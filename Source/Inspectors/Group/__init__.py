'''Group Inspector package'''

__version__ = "1.0.0"

# Register this inspector
try:
    import Inspection
    from GroupInspector import GroupInspector
    Inspection.registerInspectorClass(GroupInspector)
except:
    pass
