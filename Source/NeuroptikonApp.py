import Neuroptikon
import wx
import wx.py as py
import os, platform, sys
import xml.etree.ElementTree as ElementTree
from Network.Network import Network
from Network.Object import Object
from Network.Neuron import Neuron
from Network.Attribute import Attribute
from Library.Library import Library
from Library.Neurotransmitter import Neurotransmitter
from Library.NeuronClass import NeuronClass
from Library.Modality import Modality
from Library.Ontology import Ontology
from Library.Texture import Texture
from Preferences import Preferences
from Inspection.InspectorFrame import InspectorFrame
import Display
import Documentation

    
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
        
        wx.App.__init__(self, *args, **keywordArgs)
    
    
    def OnInit(self):
        
        import Inspectors, Layouts, Shapes  # pylint: disable-msg=W0612
        
        Neuroptikon.library = Library()
        self._loadDefaultLibraryItems()
        
        if platform.system() == 'Darwin':
            wx.MenuBar.MacSetCommonMenuBar(self.menuBar())
        
        Neuroptikon.scriptLocals = self.scriptLocals

        self.preferences = Preferences()
        self.inspector = InspectorFrame()
        
        self.SetExitOnFrameDelete(False)
        
        # open an empty network by default
        # TODO: pref to re-open last doc?
        self.onNewNetwork()
        
        return True
    
    
    def _loadDefaultLibraryItems(self):
        Neuroptikon.library.add(Neurotransmitter('ACh', gettext('Acetylcholine')))
        Neuroptikon.library.add(Neurotransmitter('DA', gettext('Dopamine')))
        Neuroptikon.library.add(Neurotransmitter('epinephrine', gettext('Epinephrine')))
        Neuroptikon.library.add(Neurotransmitter('GABA', gettext('Gamma-aminobutyric acid'), gettext('GABA')))
        Neuroptikon.library.add(Neurotransmitter('GLU', gettext('Glutamate')))
        Neuroptikon.library.add(Neurotransmitter('glycine', gettext('Glycine')))
        Neuroptikon.library.add(Neurotransmitter('histamine', gettext('Histamine')))
        Neuroptikon.library.add(Neurotransmitter('norepinephrine', gettext('Norepinephrine')))
        Neuroptikon.library.add(Neurotransmitter('5-HT', gettext('Serotonin')))
        
        # pylint: disable-msg=E1101
        Neuroptikon.library.add(NeuronClass(identifier = 'basket', name = gettext('Basket cell'), polarity = Neuron.Polarity.MULTIPOLAR, functions = [Neuron.Function.INTERNEURON], activation = 'inhibitory', neurotransmitters = [Neuroptikon.library.neurotransmitter('GABA')]))
        Neuroptikon.library.add(NeuronClass(identifier = 'pyramidal', name = gettext('Pyramidal cell'), polarity = Neuron.Polarity.MULTIPOLAR, activation = 'excitatory', neurotransmitters = [Neuroptikon.library.neurotransmitter('glutamate')]))
        Neuroptikon.library.add(NeuronClass(identifier = 'RSad pyramidal', name = gettext('RSad Pyramidal cell'), parentClass = Neuroptikon.library.neuronClass('pyramidal')))
        Neuroptikon.library.add(NeuronClass(identifier = 'RSna pyramidal', name = gettext('RSna Pyramidal cell'), parentClass = Neuroptikon.library.neuronClass('pyramidal')))
        Neuroptikon.library.add(NeuronClass(identifier = 'IB pyramidal', name = gettext('IB Pyramidal cell'), parentClass = Neuroptikon.library.neuronClass('pyramidal')))
        Neuroptikon.library.add(NeuronClass(identifier = 'betz', name = gettext('Betz cell'), parentClass = Neuroptikon.library.neuronClass('pyramidal'), functions = [Neuron.Function.MOTOR]))
        Neuroptikon.library.add(NeuronClass(identifier = 'medium spiny', name = gettext('Medium spiny neuron'), polarity = Neuron.Polarity.MULTIPOLAR, activation = 'inhibitory', neurotransmitters = [Neuroptikon.library.neurotransmitter('GABA')]))
        Neuroptikon.library.add(NeuronClass(identifier = 'purkinje', name = gettext('Purkinje cell'), polarity = Neuron.Polarity.MULTIPOLAR, activation = 'inhibitory', neurotransmitters = [Neuroptikon.library.neurotransmitter('GABA')]))
        Neuroptikon.library.add(NeuronClass(identifier = 'renshaw', name = gettext('Renshaw cell'), polarity = Neuron.Polarity.MULTIPOLAR, functions = [Neuron.Function.INTERNEURON], activation = 'inhibitory', neurotransmitters = [Neuroptikon.library.neurotransmitter('glycine')]))
        Neuroptikon.library.add(NeuronClass(identifier = 'anterior horn', name = gettext('Anterior horn cell')))
        # pylint: enable-msg=E1101
        
        Neuroptikon.library.add(Modality('light', gettext('Light')))
        Neuroptikon.library.add(Modality('odor', gettext('Odor')))
        Neuroptikon.library.add(Modality('sound', gettext('Sound')))
        Neuroptikon.library.add(Modality('taste', gettext('Taste')))
        
        # Load any ontologies in <root>/Ontologies
        try:
            for fileName in os.listdir(Neuroptikon.rootDir + os.sep + 'Ontologies'):
                if fileName != '.svn':
                    identifier = os.path.splitext(fileName)[0]
                    ontology = Ontology(identifier)
                    try:
                        ontology.importOBO(Neuroptikon.rootDir + os.sep + 'Ontologies' + os.sep + fileName)
                        Neuroptikon.library.add(ontology)
                    except:
                        (exceptionType_, exceptionValue, exceptionTraceback_) = sys.exc_info()
                        print 'Could not import ontology ' + fileName + ' (' + exceptionValue.message + ')'
        except:
            (exceptionType_, exceptionValue, exceptionTraceback_) = sys.exc_info()
            print 'Could not import ontologies (' + exceptionValue.message + ')'
        
        # Load any textures in <root>/Textures
        try:
            for fileName in os.listdir(Neuroptikon.rootDir + os.sep + 'Textures'):
                if fileName != '.svn':
                    identifier = os.path.splitext(fileName)[0]
                    texture = Texture(identifier, gettext(identifier))
                    if texture.loadImage(Neuroptikon.rootDir + os.sep + 'Textures' + os.sep + fileName):
                        Neuroptikon.library.add(texture)
        except:
            (exceptionType_, exceptionValue, exceptionTraceback_) = sys.exc_info()
            print 'Could not import textures (' + exceptionValue.message + ')'
    
    
    def onQuit(self, event_):
        continueQuit = True
        for frame in list(self._frames):
            if frame.isModified():
                frame.Raise()
            if not frame.onCloseWindow():
                continueQuit = False
                break
        if continueQuit and not any(self._frames) and platform.system() != 'Windows':
            self.ExitMainLoop()
    
    
    def menuBar(self, frame = None):
        menuBar = wx.MenuBar()
        
        fileMenu = wx.Menu()
        self.Bind(wx.EVT_MENU, self.onNewNetwork, fileMenu.Append(wx.NewId(), gettext('New Network\tCtrl-N'), gettext('Open a new network window')))
        self.Bind(wx.EVT_MENU, self.onOpenNetwork, fileMenu.Append(wx.NewId(), gettext('Open Network...\tCtrl-O'), gettext('Open a previously saved network')))
        closeItem = fileMenu.Append(wx.NewId(), gettext('Close Network\tCtrl-W'), gettext('Close the current network window'))
        if frame:
            self.Bind(wx.EVT_MENU, frame.onCloseWindow, closeItem)
        else:
            closeItem.Enable(False)
        saveItem = fileMenu.Append(wx.NewId(), gettext('Save Network...\tCtrl-S'), gettext('Save the current network'))
        if frame:
            self.Bind(wx.EVT_MENU, frame.onSaveNetwork, saveItem)
        else:
            saveItem.Enable(False)
        saveAsItem = fileMenu.Append(wx.NewId(), gettext('Save As...\tCtrl-Shift-S'), gettext('Save to a new file'))
        if frame:
            self.Bind(wx.EVT_MENU, frame.onSaveNetworkAs, saveAsItem)
        else:
            saveAsItem.Enable(False)
        fileMenu.AppendSeparator()
        runScriptItem = fileMenu.Append(wx.NewId(), gettext('Run Script...\tCtrl-R'), gettext('Run a console script file'))
        if frame:
            self.Bind(wx.EVT_MENU, frame.onRunScript, runScriptItem)
        else:
            runScriptItem.Enable(False)
        self.Bind(wx.EVT_MENU, self.onBrowseLibrary, fileMenu.Append(wx.NewId(), gettext('Browse the Library\tCtrl-Alt-L'), gettext('Open the Library window')))
        self.Bind(wx.EVT_MENU, self.onOpenConsole, fileMenu.Append(wx.NewId(), gettext('Open the Console\tCtrl-Alt-O'), gettext('Open the Console window')))
        self.Bind(wx.EVT_MENU, self.onOpenPreferences, fileMenu.Append(wx.ID_PREFERENCES, gettext('Settings'), gettext('Change Neuroptikon preferences')))
        fileMenu.AppendSeparator()
        self.Bind(wx.EVT_MENU, self.onQuit, fileMenu.Append(wx.ID_EXIT, gettext('E&xit\tCtrl-Q'), gettext('Exit the Neuroptikon application')))
        menuBar.Append(fileMenu, gettext('&File'))
        
        helpMenu = wx.Menu()
        self._customizationDocSetId = wx.NewId()
        self.Bind(wx.EVT_MENU, self.onShowDocumentation, helpMenu.Append(self._customizationDocSetId, gettext('Customizing Neuroptikon'), gettext('Show the documentation on customizing Neuroptikon')))
        self._dataMgmtDocSetId = wx.NewId()
        self.Bind(wx.EVT_MENU, self.onShowDocumentation, helpMenu.Append(self._dataMgmtDocSetId, gettext('Data Management'), gettext('Show the documentation on managing Neuroptikon data')))
        self._scriptingDocSetId = wx.NewId()
        self.Bind(wx.EVT_MENU, self.onShowDocumentation, helpMenu.Append(self._scriptingDocSetId, gettext('Scripting Interface'), gettext('Show the documentation on scripting Neuroptikon')))
        self._uiDocSetId = wx.NewId()
        self.Bind(wx.EVT_MENU, self.onShowDocumentation, helpMenu.Append(self._uiDocSetId, gettext('User Interface'), gettext('Show the documentation on interacting with Neuroptikon')))
        self.Bind(wx.EVT_MENU, self.onAboutNeuroptikon, helpMenu.Append(wx.ID_ABOUT, gettext('About Neuroptikon'), gettext('Information about this program')))
        menuBar.Append(helpMenu, gettext('&Help'))
        
        return menuBar
    
    
    def scriptLocals(self):
        layoutClasses = {}
        for layoutClass in Display.layoutClasses().itervalues():
            layoutClasses[layoutClass.__name__] = layoutClass
        shapeClasses = {}
        for shapeClass in Display.shapeClasses().itervalues():
            shapeClasses[shapeClass.__name__] = shapeClass
        scriptLocals = {'createNetwork': self.createNetwork, 
                        'displayNetwork': self.displayNetwork, 
                        'networks': self.networks, 
                        'library': Neuroptikon.library, 
                        'Neurotransmitter': Neurotransmitter, 
                        'Modality': Modality, 
                        'Ontology': Ontology, 
                        'Texture': Texture, 
                        'NeuralPolarity': Neuron.Polarity,    # DEPRECATED: remove soon... 
                        'NeuralFunction': Neuron.Function,    # DEPRECATED: remove soon...
                        'Attribute': Attribute, 
                        'layouts': layoutClasses, 
                        'shapes': shapeClasses}
        for objectClass in Object.__subclasses__(): # pylint: disable-msg=E1101
            scriptLocals[objectClass.__name__] = objectClass
        if 'DEBUG' in os.environ:
            scriptLocals['os'] = os
            scriptLocals['sys'] = sys
            scriptLocals['wx'] = wx
            import osg
            scriptLocals['osg'] = osg
            import gc
            scriptLocals['gc'] = gc
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
                (exceptionType_, exceptionValue, exceptionTraceback) = sys.exc_info()
                dialog = wx.MessageDialog(self, exceptionValue.message, gettext('An error occurred at line %d of the script:') % exceptionTraceback.tb_next.tb_lineno, style = wx.ICON_ERROR | wx.OK)
                dialog.ShowModal()
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
    
    
    def onOpenNetwork(self, event_):
        from NeuroptikonFrame import NeuroptikonFrame
        dlg = wx.FileDialog(None, gettext('Choose a saved network to open:'), '', '', '*.xml', wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            
            # TODO: raise an existing window if the network is already open
            
            try:
                xmlTree = ElementTree.parse(path)
                
                # Instantiate the network
                networkElement = xmlTree.find('Network')
                network = Network._fromXMLElement(networkElement)
                if network is None:
                    raise ValueError, gettext('Could not load the network')
                network.setSavePath(path)
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
                    self.displayNetwork(network).centerView()
            except:
                raise
    
    
    def networks(self):
        return list(self._networks)
    
    
    def releaseNetwork(self, network):
        if not any(network.displays):
            network.removeAllObjects()
            self._networks.remove(network)
    
    
    def displayNetwork(self, network):
        self._networks.add(network)
        from NeuroptikonFrame import NeuroptikonFrame
        frame = NeuroptikonFrame(network = network)
        frame.Show(True)
        frame.Raise()
        self._frames.append(frame)
        return frame.display
    
    
    def displayWasClosed(self, displayFrame):
        self._frames.remove(displayFrame)
        if len(self._frames) == 0 and platform.system() == 'Windows':
            self.ExitMainLoop()

    
    def onOpenPreferences(self, event_):
        self.preferences.Show(True)
        self.preferences.Raise()
        return self.preferences
    
    
    def onBrowseLibrary(self, event_):
        Neuroptikon.library.browse()
    
    
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
        
        Documentation.showPage(page)
            
    
    def onAboutNeuroptikon(self, event_):
        import __version__
        info = wx.AboutDialogInfo()
        info.SetName(gettext('Neuroptikon'))
        info.SetVersion(__version__.version)
        info.SetDescription(gettext('Neural ciruit visualization'))
        info.SetCopyright(gettext('Copyright (c) 2009 - Howard Hughes Medical Institute'))
        wx.AboutBox(info)