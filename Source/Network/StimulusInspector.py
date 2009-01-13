import wx
from ObjectInspector import ObjectInspector
from Stimulus import Stimulus


class StimulusInspector( ObjectInspector ):
    
    @classmethod
    def objectClass(cls):
        return Stimulus
