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
            self.gridSizer = wx.FlexGridSizer(1, 1, 8, 8)
            
            self.imageOfNeuron = wx.StaticBitmap(self._window, wx.ID_ANY)
            self.gridSizer.Add(self.imageOfNeuron, 0, wx.EXPAND)
            
            mainSizer = wx.BoxSizer(wx.VERTICAL)
            mainSizer.Add(self.gridSizer, 1, wx.ALL, 5)
            self._window.SetSizer(mainSizer)
        
        return self._window
    
    def inspectDisplay(self, display):
        selection = display.selection()
        
        self.gridSizer.Clear(True)
        neuron = None
        for visible in selection:
            if visible.client is not None and visible.client.displayName() == 'Neuron':
                neuron = visible
                break
        if neuron.client is not None and neuron.client.displayName() == 'Neuron':
            if neuron.client.neuronImage:
                image = neuron.client.neuronImage
                if image == None:
                    pass
                else:
                    windowSize = self._window.Parent.GetSize()
                    scaledImage = image.Rescale(windowSize[0], windowSize[1], wx.IMAGE_QUALITY_HIGH)
                    self.imageOfNeuron = wx.StaticBitmap(self._window, wx.ID_ANY)
                    self.imageOfNeuron.SetBitmap(wx.BitmapFromImage(scaledImage))
                    self.gridSizer.Add(self.imageOfNeuron, 0, wx.EXPAND)
            else:
                pass
        
        self._window.Layout()
   
