#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

import wx
from inspection.inspector import Inspector
from network.neuron import Neuron


class NeuronImageInspector( Inspector ):
    @classmethod
    def name(cls):
        return gettext('NeuronImage')
    
    @classmethod
    def objectClass(cls):
        return gettext('NeuronImage')
    
    @classmethod
    def canInspectDisplay(cls, display):
        if display:
            for visible in display.selection():
                if visible.client.displayName() == gettext('Neuron'):
                    if visible.client.neuronImage:
                        return True	
        return None
    
    def window(self, parentWindow=None):
        if not hasattr(self, '_window'):
            self._window = wx.Window(parentWindow, wx.ID_ANY)
            self.gridSizer = wx.FlexGridSizer(2, 1, 8, 8)
            self._currentIdx = 0
            self._labelForNeuron = wx.StaticText(parentWindow, wx.ID_ANY, gettext(''))
            self._imageOfNeuron = wx.StaticBitmap(self._window, wx.ID_ANY)
            self.gridSizer.Add(self._labelForNeuron, 0, wx.EXPAND)
            self.gridSizer.Add(self._imageOfNeuron, 0, wx.EXPAND)
            
            mainSizer = wx.BoxSizer(wx.VERTICAL)
            mainSizer.Add(self.gridSizer, 1, wx.ALL, 5)
            self._window.SetSizer(mainSizer)
        
        return self._window

    def _neuronImage(self, display, imageIdx=0):
        selection = display.selection()
        for visible in selection:
            if visible.client is not None and visible.client.displayName() == 'Neuron':          
                if visible.client.neuronImage:
                    try:
                        image = visible.client.neuronImage[imageIdx]
                        return image
                    except:
                        return False
                return False #return only for first neuron selected
        return False

    def inspectDisplay(self, display, imageIdx=0):
        image = self._neuronImage(display, imageIdx)
        self.gridSizer.Clear(True)
        if image and image.bmp is not None:
            windowSize = self._window.Parent.GetSize()
            self._labelForNeuron = wx.StaticText(self._window, wx.ID_ANY, gettext(image.label))
            scaledImage = image.bmp.Rescale(windowSize[0], windowSize[1], wx.IMAGE_QUALITY_HIGH)
            self._imageOfNeuron = wx.StaticBitmap(self._window, wx.ID_ANY)
            self._imageOfNeuron.SetBitmap(wx.BitmapFromImage(scaledImage))
            self.gridSizer.Add(self._labelForNeuron, 0, wx.EXPAND)
            self.gridSizer.Add(self._imageOfNeuron, 0, wx.EXPAND)
            self._currentIdx = imageIdx
        else:
            pass
        self._window.Layout()
   
