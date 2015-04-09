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
            self._labelForNeuron = wx.StaticText(self._window, wx.ID_ANY, gettext(''))
            

            labelSizer = wx.BoxSizer(wx.HORIZONTAL)
            labelSizer.Add(self._labelForNeuron, 1, wx.LEFT, 2)
            
            self._imageOfNeuron = wx.StaticBitmap(self._window, wx.ID_ANY)
            #self.gridSizer.Add(self._labelForNeuron, 0, wx.EXPAND)
            self.gridSizer.Add(labelSizer)
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

    def _neuronImageCount(self, display):
        selection = display.selection()
        for visible in selection:
            if visible.client is not None and visible.client.displayName() == 'Neuron':          
                if visible.client.neuronImage:
                    return len(visible.client.neuronImage)
        return 0

    def inspectDisplay(self, display, imageIdx=0):
        self.display = display
        image = self._neuronImage(display, imageIdx)
        self.gridSizer.Clear(True)

        if image and image.bmp is not None:
            self.imageIdx = imageIdx
            self.imageCount = self._neuronImageCount(display)
            windowSize = self._window.Parent.GetSize()
            self._labelForNeuron = wx.StaticText(self._window, wx.ID_ANY, gettext(image.label))

            labelSizer = wx.BoxSizer(wx.HORIZONTAL)
            labelSizer.Add(self._labelForNeuron, 1, wx.LEFT, 2)

            #Only show the next and previous buttons if there are multiple images
            if (self._neuronImageCount(display) > 1):
                self._prevButton = wx.Button(self._window, wx.ID_ANY, gettext('Prev'), style = wx.BU_EXACTFIT)
                self._prevButton.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)
                self._prevButton.SetSize(wx.Size(60, self._prevButton.GetSize().GetHeight()))
                self._prevButton.SetMinSize(self._prevButton.GetSize())
                self._window.Bind(wx.EVT_BUTTON, self._displayPrev, self._prevButton)
                labelSizer.Add(self._prevButton, 0, wx.LEFT, 8)

                self._nextButton = wx.Button(self._window, wx.ID_ANY, gettext('Next'), style = wx.BU_EXACTFIT)
                self._nextButton.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)
                self._nextButton.SetSize(wx.Size(60, self._nextButton.GetSize().GetHeight()))
                self._nextButton.SetMinSize(self._nextButton.GetSize())
                self._window.Bind(wx.EVT_BUTTON, self._displayNext, self._nextButton)
                labelSizer.Add(self._nextButton, 0, wx.LEFT, 8)   

            scaledImage = image.bmp.Rescale(windowSize[0], windowSize[1], wx.IMAGE_QUALITY_HIGH)
            self._imageOfNeuron = wx.StaticBitmap(self._window, wx.ID_ANY)
            self._imageOfNeuron.SetBitmap(wx.BitmapFromImage(scaledImage))
            self.gridSizer.Add(labelSizer)
            self.gridSizer.Add(self._imageOfNeuron, 0, wx.EXPAND)
            self._currentIdx = imageIdx
        else:
            pass
        self._window.Layout()

    def _displayNext(self, event):
        nextImage = (self.imageIdx + 1) % self.imageCount
        self.inspectDisplay(self.display, nextImage)

    def _displayPrev(self, event):
        prevImage = (self.imageIdx + 1) % self.imageCount
        self.inspectDisplay(self.display, prevImage)

   
