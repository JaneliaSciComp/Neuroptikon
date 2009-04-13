'''Geometry Inspector package'''

__version__ = "1.0.0"

# Register this inspector
try:
    import Inspection
    from GeometryInspector import GeometryInspector
    Inspection.registerInspectorClass(GeometryInspector)
except:
    pass
