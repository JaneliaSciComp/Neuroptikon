'''Display package'''

__version__ = "1.0.0"

# Register the display inspectors
import Inspection
from DisplayInspector import DisplayInspector
Inspection.registerInspectorClass(DisplayInspector)

from AppearanceInspector import AppearanceInspector
Inspection.registerInspectorClass(AppearanceInspector)

from ArrangementInspector import ArrangementInspector
Inspection.registerInspectorClass(ArrangementInspector)

from GeometryInspector import GeometryInspector
Inspection.registerInspectorClass(GeometryInspector)

from GroupInspector import GroupInspector
Inspection.registerInspectorClass(GroupInspector)

from PathInspector import PathInspector
Inspection.registerInspectorClass(PathInspector)
