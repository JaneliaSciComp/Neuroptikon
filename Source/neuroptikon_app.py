#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

import neuroptikon
import wx
import wx.py as py
import os, platform, sys, traceback, urllib
try:
    import xml.etree.cElementTree as ElementTree
except ImportError:
    import xml.etree.ElementTree as ElementTree
from datetime import datetime, date, time

from network.network import Network
from network.object import Object
from network.neuro_object import NeuroObject
from network.neuron import Neuron
from network.attribute import Attribute
from library.library import Library
from library.neurotransmitter import Neurotransmitter
from library.neuron_class import NeuronClass
from library.modality import Modality
from library.ontology import Ontology
from library.texture import Texture
from preferences import Preferences
from inspection.inspector_frame import InspectorFrame
import display
import documentation
from feedback_dialog import FeedbackDialog
import __version__

# The following import is required to allow quitting on Mac OS X when no windows are open.  If osgViewer is imported after the common menu bar is set then the quit event handler is overwritten.
import osgViewer

from gettext import gettext
    
class NeuroptikonApp(wx.App):
    
    def __init__(self, *args, **keywordArgs):
        self._networks = set([])
        self.preferences = None
        self.inspector = None
        
        self.config = None
        self._console = None
        
        # Keep track of open frames so we can close them on quit.
        # TODO: use wxWidget's document/view framework instead
        self._frames = []
        
        self._customizationDocSetId = wx.NewId()
        self._dataMgmtDocSetId = wx.NewId()
        self._scriptingDocSetId = wx.NewId()
        self._uiDocSetId = wx.NewId()
        
        wx.App.__init__(self, *args, **keywordArgs)
    
    
    def OnInit(self):
        
        import Inspectors, Layouts, Shapes  # pylint: disable=W0612
        
        neuroptikon.library = Library()
        self._loadDefaultLibraryItems()

        neuroptikon.config = wx.Config('Neuroptikon')
        
        if platform.system() == 'Darwin':
            wx.MenuBar.MacSetCommonMenuBar(self.menuBar())
        
        neuroptikon.scriptLocals = self.scriptLocals

        self.preferences = Preferences()
        self.inspector = InspectorFrame()
        
        self.SetExitOnFrameDelete(False)
        
        startupScript = neuroptikon.config.Read('Startup Script', '')
        try:
            exec startupScript in self.scriptLocals()
        except:
            (exceptionType, exceptionValue, exceptionTraceback) = sys.exc_info()
            frames = traceback.extract_tb(exceptionTraceback)[1:]
            message = gettext('An error occurred while running the startup script:')
            subMessage = str(exceptionValue) + ' (' + exceptionType.__name__ + ')' + '\n\nTraceback:\n' + ''.join(traceback.format_list(frames))
            if platform.system() == 'Darwin':
                wx.MessageBox(subMessage, message, style = wx.ICON_ERROR | wx.OK)
            else:
                wx.MessageBox(message + '\n\n' + subMessage, 'Neuroptikon', parent = self, style = wx.ICON_ERROR | wx.OK)
        
        # open an empty network by default
        # TODO: pref to re-open last doc?
        self.onNewNetwork()
        
        return True
    
    
    def _loadDefaultLibraryItems(self):
        neuroptikon.library.add(Neurotransmitter('ACh', gettext('Acetylcholine')))
        neuroptikon.library.add(Neurotransmitter('DA', gettext('Dopamine')))
        neuroptikon.library.add(Neurotransmitter('epinephrine', gettext('Epinephrine')))
        neuroptikon.library.add(Neurotransmitter('GABA', gettext('Gamma-aminobutyric acid'), gettext('GABA')))
        neuroptikon.library.add(Neurotransmitter('GLU', gettext('Glutamate')))
        neuroptikon.library.add(Neurotransmitter('glycine', gettext('Glycine')))
        neuroptikon.library.add(Neurotransmitter('histamine', gettext('Histamine')))
        neuroptikon.library.add(Neurotransmitter('norepinephrine', gettext('Norepinephrine')))
        neuroptikon.library.add(Neurotransmitter('5-HT', gettext('Serotonin')))
        
        # pylint: disable=E1101
        neuroptikon.library.add(NeuronClass(identifier = 'basket', name = gettext('Basket cell'), polarity = Neuron.Polarity.MULTIPOLAR, functions = [Neuron.Function.INTERNEURON], activation = 'inhibitory', neurotransmitters = [neuroptikon.library.neurotransmitter('GABA')]))
        neuroptikon.library.add(NeuronClass(identifier = 'pyramidal', name = gettext('Pyramidal cell'), polarity = Neuron.Polarity.MULTIPOLAR, activation = 'excitatory', neurotransmitters = [neuroptikon.library.neurotransmitter('glutamate')]))
        neuroptikon.library.add(NeuronClass(identifier = 'RSad pyramidal', name = gettext('RSad Pyramidal cell'), parentClass = neuroptikon.library.neuronClass('pyramidal')))
        neuroptikon.library.add(NeuronClass(identifier = 'RSna pyramidal', name = gettext('RSna Pyramidal cell'), parentClass = neuroptikon.library.neuronClass('pyramidal')))
        neuroptikon.library.add(NeuronClass(identifier = 'IB pyramidal', name = gettext('IB Pyramidal cell'), parentClass = neuroptikon.library.neuronClass('pyramidal')))
        neuroptikon.library.add(NeuronClass(identifier = 'betz', name = gettext('Betz cell'), parentClass = neuroptikon.library.neuronClass('pyramidal'), functions = [Neuron.Function.MOTOR]))
        neuroptikon.library.add(NeuronClass(identifier = 'medium spiny', name = gettext('Medium spiny neuron'), polarity = Neuron.Polarity.MULTIPOLAR, activation = 'inhibitory', neurotransmitters = [neuroptikon.library.neurotransmitter('GABA')]))
        neuroptikon.library.add(NeuronClass(identifier = 'purkinje', name = gettext('Purkinje cell'), polarity = Neuron.Polarity.MULTIPOLAR, activation = 'inhibitory', neurotransmitters = [neuroptikon.library.neurotransmitter('GABA')]))
        neuroptikon.library.add(NeuronClass(identifier = 'renshaw', name = gettext('Renshaw cell'), polarity = Neuron.Polarity.MULTIPOLAR, functions = [Neuron.Function.INTERNEURON], activation = 'inhibitory', neurotransmitters = [neuroptikon.library.neurotransmitter('glycine')]))
        neuroptikon.library.add(NeuronClass(identifier = 'anterior horn', name = gettext('Anterior horn cell')))
        # pylint: enable=E1101
        
        neuroptikon.library.add(Modality('light', gettext('Light')))
        neuroptikon.library.add(Modality('odor', gettext('Odor')))
        neuroptikon.library.add(Modality('sound', gettext('Sound')))
        neuroptikon.library.add(Modality('taste', gettext('Taste')))
        
        # Load any ontologies in <root>/Ontologies
        try:
            for fileName in os.listdir(neuroptikon.rootDir + os.sep + 'Ontologies'):
                if fileName.endswith('.obo'):
                    identifier = os.path.splitext(fileName)[0]
                    ontology = Ontology(identifier)
                    try:
                        ontology.importOBO(neuroptikon.rootDir + os.sep + 'Ontologies' + os.sep + fileName)
                        neuroptikon.library.add(ontology)
                    except:
                        (exceptionType, exceptionValue, exceptionTraceback_) = sys.exc_info()
                        print 'Could not import ontology ' + fileName + ' (' + str(exceptionValue) + ' (' + exceptionType.__name__ + ')' + ')'
        except:
            (exceptionType, exceptionValue, exceptionTraceback_) = sys.exc_info()
            print 'Could not import ontologies (' + str(exceptionValue) + ' (' + exceptionType.__name__ + ')' + ')'
        
        # Load any textures in <root>/Textures
        try:
            for fileName in os.listdir(neuroptikon.rootDir + os.sep + 'Textures'):
                if fileName != '.svn':
                    identifier = os.path.splitext(fileName)[0]
                    texture = Texture(identifier, gettext(identifier))
                    if texture.loadImage(neuroptikon.rootDir + os.sep + 'Textures' + os.sep + fileName):
                        neuroptikon.library.add(texture)
        except:
            (exceptionType, exceptionValue, exceptionTraceback_) = sys.exc_info()
            print 'Could not import textures (' + str(exceptionValue) + ' (' + exceptionType.__name__ + ')' + ')'
    
    
    def onQuit(self, event_):
        continueQuit = True
        for frame in list(self._frames):
            if frame.isModified():
                frame.Raise()
            if not frame.Close():
                continueQuit = False
                break
        if continueQuit and not any(self._frames) and platform.system() == 'Darwin':
            self.ExitMainLoop()
    
    
    def menuBar(self, frame = None):
        menuBar = wx.MenuBar()
        
        fileMenu = wx.Menu()
        self.Bind(wx.EVT_MENU, self.onNewNetwork, fileMenu.Append(wx.ID_NEW, gettext('New Network\tCtrl-N'), gettext('Open a new network window')))
        self.Bind(wx.EVT_MENU, self.onOpenNetwork, fileMenu.Append(wx.ID_OPEN, gettext('Open Network...\tCtrl-O'), gettext('Open a previously saved network')))
        closeItem = fileMenu.Append(wx.ID_CLOSE, gettext('Close Network\tCtrl-W'), gettext('Close the current network window'))
        if frame:
            frame.Bind(wx.EVT_MENU, frame.onCloseWindow, closeItem)
        else:
            closeItem.Enable(False)
        saveItem = fileMenu.Append(wx.ID_SAVE, gettext('Save Network...\tCtrl-S'), gettext('Save the current network'))
        if frame:
            frame.Bind(wx.EVT_MENU, frame.onSaveNetwork, saveItem)
        else:
            saveItem.Enable(False)
        saveAsItem = fileMenu.Append(wx.ID_SAVEAS, gettext('Save As...\tCtrl-Shift-S'), gettext('Save to a new file'))
        if frame:
            frame.Bind(wx.EVT_MENU, frame.onSaveNetworkAs, saveAsItem)
        else:
            saveAsItem.Enable(False)
        fileMenu.AppendSeparator()
        runScriptItem = fileMenu.Append(wx.NewId(), gettext('Run Script...\tCtrl-R'), gettext('Run a console script file'))
        if frame:
            frame.Bind(wx.EVT_MENU, frame.onRunScript, runScriptItem)
        else:
            runScriptItem.Enable(False)
        self.Bind(wx.EVT_MENU, self.onBrowseLibrary, fileMenu.Append(wx.NewId(), gettext('Browse the Library\tCtrl-Alt-L'), gettext('Open the Library window')))
        self.Bind(wx.EVT_MENU, self.onOpenConsole, fileMenu.Append(wx.NewId(), gettext('Open the Console\tCtrl-Alt-O'), gettext('Open the Console window')))
        self.Bind(wx.EVT_MENU, self.onOpenPreferences, fileMenu.Append(wx.ID_PREFERENCES, gettext('Settings'), gettext('Change Neuroptikon preferences')))
        fileMenu.AppendSeparator()
        self.Bind(wx.EVT_MENU, self.onQuit, fileMenu.Append(wx.ID_EXIT, gettext('E&xit\tCtrl-Q'), gettext('Exit the Neuroptikon application')))
        menuBar.Append(fileMenu, gettext('&File'))
        
        helpMenu = wx.Menu()
        self.Bind(wx.EVT_MENU, self.onShowDocumentation, helpMenu.Append(self._customizationDocSetId, gettext('Customizing Neuroptikon'), gettext('Show the documentation on customizing Neuroptikon')))
        self.Bind(wx.EVT_MENU, self.onShowDocumentation, helpMenu.Append(self._dataMgmtDocSetId, gettext('Data Management'), gettext('Show the documentation on managing Neuroptikon data')))
        self.Bind(wx.EVT_MENU, self.onShowDocumentation, helpMenu.Append(self._scriptingDocSetId, gettext('Scripting Interface'), gettext('Show the documentation on scripting Neuroptikon')))
        self.Bind(wx.EVT_MENU, self.onShowDocumentation, helpMenu.Append(self._uiDocSetId, gettext('User Interface'), gettext('Show the documentation on interacting with Neuroptikon')))
        helpMenu.AppendSeparator()
        self.Bind(wx.EVT_MENU, self.onSendFeedback, helpMenu.Append(wx.NewId(), gettext('Report Bug or Enhancement'), gettext('Report a bug or request a new feature')))
        if platform.system() != 'Darwin':
            helpMenu.AppendSeparator()
        self.Bind(wx.EVT_MENU, self.onAboutNeuroptikon, helpMenu.Append(wx.ID_ABOUT, gettext('About Neuroptikon'), gettext('Information about this program')))
        menuBar.Append(helpMenu, gettext('&Help'))
        
        return menuBar
    
    
    def scriptLocals(self):
        layoutClasses = {}
        for layoutClass in display.layout.layoutClasses():
            layoutClasses[layoutClass.name()] = layoutClass
        shapeClasses = {}
        for shapeClass in display.shape.shapeClasses():
            shapeClasses[shapeClass.__name__] = shapeClass
        scriptLocals = {'createNetwork': self.createNetwork, 
                        'displayNetwork': self.displayNetwork, 
                        'openNetwork': self.openNetwork, 
                        'networks': self.networks, 
                        'library': neuroptikon.library, 
                        'Neurotransmitter': Neurotransmitter, 
                        'NeuronClass': NeuronClass, 
                        'Modality': Modality, 
                        'Ontology': Ontology, 
                        'Texture': Texture, 
                        'NeuralPolarity': Neuron.Polarity,    # DEPRECATED: remove soon... 
                        'NeuralFunction': Neuron.Function,    # DEPRECATED: remove soon...
                        'Attribute': Attribute, 
                        'layouts': layoutClasses, 
                        'shapes': shapeClasses, 
                        'Object': Object, 
                        'showMessage': self.showMessage}
        for objectClass in NeuroObject.__subclasses__(): # pylint: disable=E1101
            scriptLocals[objectClass.__name__] = objectClass
        if 'DEBUG' in os.environ:
            scriptLocals['os'] = os
            scriptLocals['sys'] = sys
            scriptLocals['wx'] = wx
            import osg
            scriptLocals['osg'] = osg
            import gc
            scriptLocals['gc'] = gc
            scriptLocals['datetime'] = datetime
            scriptLocals['date'] = date
            scriptLocals['time'] = time
            try:
                import objgraph
                scriptLocals['objgraph'] = objgraph
            except ImportError:
                pass
            from pydispatch import dispatcher
            scriptLocals['dispatcher'] = dispatcher
            
        return scriptLocals
    
    
    def onRunScript(self, event_):
        dlg = wx.FileDialog(None, gettext('Choose a script to run'), 'Scripts', '', '*.py', wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            prevDir = os.getcwd()
            os.chdir(os.path.dirname(dlg.GetPath()))
            try:
                execfile(dlg.GetPath(), self.scriptLocals())
            except:
                (exceptionType, exceptionValue, exceptionTraceback) = sys.exc_info()
                wx.MessageBox(str(exceptionValue) + ' (' + exceptionType.__name__ + ')', gettext('An error occurred at line %d of the script:') % exceptionTraceback.tb_next.tb_lineno, style = wx.ICON_ERROR | wx.OK)
            os.chdir(prevDir)
        dlg.Destroy()
    
    
    def onOpenConsole(self, event_):
        if not self._console:
            confDir = wx.StandardPaths.Get().GetUserDataDir()
            if not os.path.exists(confDir):
                os.mkdir(confDir)
            fileName = os.path.join(confDir, 'Console.config')
            self.config = wx.FileConfig(localFilename=fileName)
            self.config.SetRecordDefaults(True)
            self._console = py.shell.ShellFrame(title=gettext('Console'), config=self.config, dataDir=confDir, locals=self.scriptLocals())
            #TODO: need to just hide the console window on close or set up some kind of callback to clear _console when the console closes
        self._console.Show()
        self._console.Raise()
    
    
    def onNewNetwork(self, event_ = None):
        network = self.createNetwork()
        self.displayNetwork(network)
    
    
    def createNetwork(self):
        network = Network()
        #TODO: implement doc/view framework
        return network
    
    
    def openNetwork(self, filePath):
        """
        Open the previously saved network at the indicated path.
        
        Any displays will be restored or a default one will be opened.
        """
        
        from neuroptikon_frame import NeuroptikonFrame
        
        # TODO: raise an existing window if the network is already open
        
        try:
            xmlTree = ElementTree.parse(filePath)
            
            # Instantiate the network
            networkElement = xmlTree.find('Network')
            network = Network._fromXMLElement(networkElement)
            if network is None:
                raise ValueError, gettext('Could not load the network')
            network.setSavePath(filePath)
            network.setModified(False)
            self._networks.add(network)
            
            # Instantiate any displays
            for frameElement in xmlTree.findall('DisplayWindow'):
                frame = NeuroptikonFrame._fromXMLElement(frameElement, network = network)
                if frame is None:
                    raise ValueError, gettext('Could not create one of the displays')
                frame.Show(True)
                frame.Raise()
                self._frames.append(frame)
            
            # Create a default display if none were specified in the file.
            if len(network.displays) == 0:
                self.displayNetwork(network).zoomToFit()
        except:
            raise
    
    
    def onOpenNetwork(self, event_):
        dlg = wx.FileDialog(None, gettext('Choose a saved network to open:'), '', '', '*.xml', wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.openNetwork(dlg.GetPath())
        dlg.Destroy()
    
    
    def networks(self):
        return list(self._networks)
    
    
    def releaseNetwork(self, network):
        if not any(network.displays):
            network.removeAllObjects()
            self._networks.remove(network)
    
    
    def displayNetwork(self, network, populateDisplay = True):
        """
        Open a new display for the network.
        """
        
        self._networks.add(network)
        from neuroptikon_frame import NeuroptikonFrame
        frame = NeuroptikonFrame(network = network, populateDisplay = populateDisplay)
        frame.Show(True)
        frame.Raise()
        self._frames.append(frame)
        return frame.display
    
    
    def displayWasClosed(self, displayFrame):
        self._frames.remove(displayFrame)
        if len(self._frames) == 0 and platform.system() != 'Darwin':
            self.ExitMainLoop()

    
    def onOpenPreferences(self, event_):
        self.preferences.Show(True)
        self.preferences.Raise()
        return self.preferences
    
    
    def onBrowseLibrary(self, event_):
        neuroptikon.library.browse()
    
    
    def onOpenInspector(self, event_):
        self.inspector.Show(True)
        self.inspector.Raise()
        return self.inspector
    
    
    def onShowDocumentation(self, event):
        if event.GetId() == self._customizationDocSetId:
            page = 'Customizing/index.html'
        elif event.GetId() == self._dataMgmtDocSetId:
            page = 'DataManagement.html'
        elif event.GetId() == self._scriptingDocSetId:
            page = 'Scripting/index.html'
        elif event.GetId() == self._uiDocSetId:
            page = 'UserInterface/index.html'
        
        documentation.showPage(page)
    
    
    def onSendFeedback(self, event_):
        dlg = FeedbackDialog()
        if dlg.ShowModal() == wx.ID_OK:
            queryDict = {'pid': 10000, 'summary': dlg.summary(), 'description': dlg.description(), 'customfield_10000': dlg.contactEmail()}
            if platform.system() == 'Darwin':
                environment = 'OS: Mac OS X ' + platform.mac_ver()[0] + '\n'
            elif platform.system() == 'Windows':
                release, version, csd, ptype = platform.win32_ver()
                environment = 'OS: Windows ' + release + '  ' + version + ' ' + csd + ' ' + ptype + '\n'
            else:
                environment = 'OS: ' + platform.system() + ' ' + platform.version() + '\n'
            environment += 'Python version: ' + platform.python_version() + '\n'
            queryDict['environment'] = environment
            if dlg.isBugReport():
                queryDict['issuetype'] = 1
            elif dlg.isFeatureRequest():
                queryDict['issuetype'] = 2
            # task = 3, improvement = 4
            queryDict['versions'] = __version__.JIRA_version_id
            url = 'http://www.neuroptikon.org/issues/secure/CreateIssueDetails.jspa?' + urllib.urlencode(queryDict)
            if not wx.LaunchDefaultBrowser(url):
                message = gettext('The issue could not be created')
                resolution = gettext('Please visit http://www.neuroptikon.org/issues/ to send your feedback.')
                if platform.system() == 'Darwin':
                    wx.MessageBox(resolution, message)
                else:
                    wx.MessageBox(gettext('Send Feedback'), message + '\n\n' + resolution)
            
        dlg.Destroy()
        
    
    def onAboutNeuroptikon(self, event_):
        info = wx.AboutDialogInfo()
        info.SetName(gettext('Neuroptikon'))
        info.SetVersion(__version__.version)
        info.SetDescription(gettext('Developed at the \nJanelia Farm Research Campus by:\n\nFrank Midgley\nVivek Jayaraman\nMitya Chklovskii\nDon Olbris'))
        info.SetCopyright(gettext('Copyright \xa9 2010 - Howard Hughes Medical Institute'))
        wx.AboutBox(info)
    
    
    def showMessage(self, message, subMessage = None, isError = False):
        """
        Display a message to the user.
        """
        
        if platform.system() == 'Darwin':
            wx.MessageBox(subMessage, message or '', style = (wx.ICON_ERROR if isError else wx.ICON_INFORMATION) | wx.OK)
        else:
            wx.MessageBox('Neuroptikon', (message + '\n\n' + subMessage if message else subMessage or ''), style = (wx.ICON_ERROR if isError else wx.ICON_INFORMATION) | wx.OK)
    
