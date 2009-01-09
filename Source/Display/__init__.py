'''Display package'''

__version__ = "1.0.0"

# Register the display inspectors
import Inspection
from DisplayInspector import DisplayInspector
Inspection.registerInspectorClass(DisplayInspector)

from VisibleInspector import VisibleInspector
Inspection.registerInspectorClass(VisibleInspector)

from GroupInspector import GroupInspector
Inspection.registerInspectorClass(GroupInspector)
