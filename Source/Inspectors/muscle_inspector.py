import wx
from object_inspector import ObjectInspector
from network.muscle import Muscle


class MuscleInspector( ObjectInspector ):
    
    @classmethod
    def objectClass(cls):
        return Muscle
