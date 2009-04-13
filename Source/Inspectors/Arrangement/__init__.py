'''Arrangement Inspector package'''

__version__ = "1.0.0"

# Register this inspector
try:
    import Inspection
    from ArrangementInspector import ArrangementInspector
    Inspection.registerInspectorClass(ArrangementInspector)
except:
    pass
