import os, platform, stat, sys

# Turn off OSG warnings.
if 'OSG_NOTIFY_LEVEL' not in os.environ:
    os.environ['OSG_NOTIFY_LEVEL'] = 'ALWAYS'

runningFromSource = not hasattr(sys, "frozen")

# Calculate the root directory and make sure sys.path and DYLD_LIBRARY_PATH/PATH are set up correctly.
if not runningFromSource:
    rootDir = os.path.dirname(sys.executable)
    if platform.system() == 'Darwin':
        rootDir = os.path.dirname(rootDir) + os.sep + 'Resources'
    elif platform.system() == 'Windows':
        sys.path.append(rootDir)
    platformLibPath = rootDir
else:
    rootDir = os.path.abspath(os.path.dirname(sys.modules['__main__'].__file__))
    
    # Make sure that the library paths are set up correctly for the current location.
    commonLibPath = os.path.join(rootDir, 'lib', 'CrossPlatform')
    platformLibPath = os.path.join(rootDir, 'lib', platform.system())

    if platform.system() == 'Darwin':
        # Use the copy of wx in /Library
        import wxversion
        wxversion.select('2.8')
        
        libraryEnvVar = 'DYLD_LIBRARY_PATH'
    elif platform.system() == 'Windows':
        libraryEnvVar = 'PATH'
    #elif platform.system() == 'Linux':
    #    libraryEnvVar = 'LD_LIBRARY_PATH'

    if libraryEnvVar not in os.environ or platformLibPath not in os.environ[libraryEnvVar].split(os.pathsep):
        # Add the search path for the native libraries to the enviroment.
        if libraryEnvVar in os.environ:
            os.environ[libraryEnvVar] = platformLibPath + os.pathsep + os.environ[libraryEnvVar]
        else:
            os.environ[libraryEnvVar] = platformLibPath
        # Restart this script with the same instance of python and the same arguments.
        arguments = [sys.executable]
        arguments.extend(sys.argv)
        os.system(' '.join(arguments))
        raise SystemExit

    sys.path.insert(0, commonLibPath)
    sys.path.insert(0, platformLibPath)


# TODO: figure out if it's worth building and packaging psyco
#    try:
#        import psyco
#        psyco.full()
#    except ImportError:
#        print 'Psyco not installed, the program will just run slower'


# Make sure fonts are found on Mac OS X
if platform.system() == 'Darwin':
    fontPaths = []
    try:
        from Carbon import File, Folder, Folders
        domains = [Folders.kUserDomain, Folders.kLocalDomain, Folders.kSystemDomain]
        if not runningFromSource:
            domains.append(Folders.kNetworkDomain)
        for domain in domains:
            try:
                fsref = Folder.FSFindFolder(domain, Folders.kFontsFolderType, False)
                fontPaths.append(File.pathname(fsref))
            except:
                pass    # Folder probably doesn't exist.
    except:
        fontPaths.extend([os.path.expanduser('~/Library/Fonts'), '/Library/Fonts', '/Network/Library/Fonts', '/System/Library/Fonts'])
    os.environ['OSG_FILE_PATH'] = ':'.join(fontPaths)


# Set up for internationalization.
import gettext as gettext_module, __builtin__
__builtin__.gettext = gettext_module.translation('Neuroptikon', fallback = True).lgettext


# Install a new version of inspect.getdoc() that converts any reST formatting to plain text.
import inspect, re
_orig_getdoc = inspect.getdoc
def _getdoc(object):
    docstring = _orig_getdoc(object)
    if docstring:
        # Convert any interpreted text to plain text.  <http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#interpreted-text>
        docstring = re.sub(r':[^:]+:`([^<]*) \<.*\>`', r'\1', docstring)
        docstring = re.sub(r':[^:]+:`([^<]*)`', r'\1', docstring)

    return docstring
inspect.getdoc = _getdoc


import wx
import wx.py as py
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


if __name__ == "__main__":
    
    class Neuroptikon(wx.App):
        
        def OnInit(self):
            
            self.rootDir = rootDir
            self.platformLibPath = platformLibPath
            
            import Inspectors, Layouts, Shapes
            
            self.library = Library()
            self._loadDefaultLibraryItems()
            
            self._networks = set([])
            
            if platform.system() == 'Darwin':
                wx.MenuBar.MacSetCommonMenuBar(self.menuBar())

            self.preferences = Preferences()
            self.inspector = InspectorFrame()
            
            # Keep track of open frames so we can close them on quit.
            # TODO: use wxWidget's document/view framework instead
            self._frames = []
            self.SetExitOnFrameDelete(False)
            
            # open an empty network by default
            # TODO: pref to re-open last doc?
            self.onNewNetwork()
            
            return True
        
        
        def _loadDefaultLibraryItems(self):
            self.library.add(Neurotransmitter('ACh', gettext('Acetylcholine')))
            self.library.add(Neurotransmitter('DA', gettext('Dopamine')))
            self.library.add(Neurotransmitter('epinephrine', gettext('Epinephrine')))
            self.library.add(Neurotransmitter('GABA', gettext('Gamma-aminobutyric acid'), gettext('GABA')))
            self.library.add(Neurotransmitter('GLU', gettext('Glutamate')))
            self.library.add(Neurotransmitter('glycine', gettext('Glycine')))
            self.library.add(Neurotransmitter('histamine', gettext('Histamine')))
            self.library.add(Neurotransmitter('norepinephrine', gettext('Norepinephrine')))
            self.library.add(Neurotransmitter('5-HT', gettext('Serotonin')))
            
            self.library.add(NeuronClass(identifier = 'basket', name = gettext('Basket cell'), polarity = Neuron.Polarity.MULTIPOLAR, functions = [Neuron.Function.INTERNEURON], activation = 'inhibitory', neurotransmitters = [self.library.neurotransmitter('GABA')]))
            self.library.add(NeuronClass(identifier = 'pyramidal', name = gettext('Pyramidal cell'), polarity = Neuron.Polarity.MULTIPOLAR, activation = 'excitatory', neurotransmitters = [self.library.neurotransmitter('glutamate')]))
            self.library.add(NeuronClass(identifier = 'RSad pyramidal', name = gettext('RSad Pyramidal cell'), parentClass = self.library.neuronClass('pyramidal')))
            self.library.add(NeuronClass(identifier = 'RSna pyramidal', name = gettext('RSna Pyramidal cell'), parentClass = self.library.neuronClass('pyramidal')))
            self.library.add(NeuronClass(identifier = 'IB pyramidal', name = gettext('IB Pyramidal cell'), parentClass = self.library.neuronClass('pyramidal')))
            self.library.add(NeuronClass(identifier = 'betz', name = gettext('Betz cell'), parentClass = self.library.neuronClass('pyramidal'), functions = [Neuron.Function.MOTOR]))
            self.library.add(NeuronClass(identifier = 'medium spiny', name = gettext('Medium spiny neuron'), polarity = Neuron.Polarity.MULTIPOLAR, activation = 'inhibitory', neurotransmitters = [self.library.neurotransmitter('GABA')]))
            self.library.add(NeuronClass(identifier = 'purkinje', name = gettext('Purkinje cell'), polarity = Neuron.Polarity.MULTIPOLAR, activation = 'inhibitory', neurotransmitters = [self.library.neurotransmitter('GABA')]))
            self.library.add(NeuronClass(identifier = 'renshaw', name = gettext('Renshaw cell'), polarity = Neuron.Polarity.MULTIPOLAR, functions = [Neuron.Function.INTERNEURON], activation = 'inhibitory', neurotransmitters = [self.library.neurotransmitter('glycine')]))
            self.library.add(NeuronClass(identifier = 'anterior horn', name = gettext('Anterior horn cell')))
            
            self.library.add(Modality('light', gettext('Light')))
            self.library.add(Modality('odor', gettext('Odor')))
            self.library.add(Modality('sound', gettext('Sound')))
            self.library.add(Modality('taste', gettext('Taste')))
            
            # Load any ontologies in <root>/Ontologies
            try:
                for fileName in os.listdir(rootDir + os.sep + 'Ontologies'):
                    if fileName != '.svn':
                        identifier = os.path.splitext(fileName)[0]
                        ontology = Ontology(identifier)
                        try:
                            ontology.importOBO(rootDir + os.sep + 'Ontologies' + os.sep + fileName)
                            self.library.add(ontology)
                        except:
                            (exceptionType, exceptionValue, exceptionTraceback) = sys.exc_info()
                            print 'Could not import ontology ' + fileName + ' (' + exceptionValue.message + ')'
            except:
                (exceptionType, exceptionValue, exceptionTraceback) = sys.exc_info()
                print 'Could not import ontologies (' + exceptionValue.message + ')'
            
            # Load any textures in <root>/Textures
            try:
                for fileName in os.listdir(rootDir + os.sep + 'Textures'):
                    if fileName != '.svn':
                        identifier = os.path.splitext(fileName)[0]
                        texture = Texture(identifier, gettext(identifier))
                        if texture.loadImage(rootDir + os.sep + 'Textures' + os.sep + fileName):
                            self.library.add(texture)
            except:
                (exceptionType, exceptionValue, exceptionTraceback) = sys.exc_info()
                print 'Could not import textures (' + exceptionValue.message + ')'
        
        
        def onQuit(self, event):
            continueQuit = True
            for frame in list(self._frames):
                if frame.isModified():
                    frame.Raise()
                if not frame.onCloseWindow():
                    continueQuit = False
                    break
            if continueQuit and not any(self._frames) and platform.system() != 'Windows':
                self.ExitMainLoop()
        
        
        def loadImage(self, imageFileName):
            try:
                image = wx.Image(self.rootDir + os.sep + 'Images' + os.sep + imageFileName)
            except:
                image = None
            return image
        
        
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
            locals = {'createNetwork': self.createNetwork, 
                      'displayNetwork': self.displayNetwork, 
                      'networks': self.networks, 
                      'library': self.library, 
                      'Neurotransmitter': Neurotransmitter, 
                      'Modality': Modality, 
                      'Ontology': Ontology, 
                      'NeuralPolarity': Neuron.Polarity,    # DEPRECATED: remove soon... 
                      'NeuralFunction': Neuron.Function,    # DEPRECATED: remove soon...
                      'Attribute': Attribute, 
                      'layouts': layoutClasses, 
                      'shapes': shapeClasses}
            for objectClass in Object.__subclasses__():
                locals[objectClass.__name__] = objectClass
            if 'DEBUG' in os.environ:
                locals['os'] = os
                locals['sys'] = sys
                locals['wx'] = wx
                import osg
                locals['osg'] = osg
                import gc
                locals['gc'] = gc
                try:
                    import objgraph
                    locals['objgraph'] = objgraph
                except:
                    pass
                from pydispatch import dispatcher
                locals['dispatcher'] = dispatcher
                
            return locals
        
        
        def onRunScript(self, event):
            dlg = wx.FileDialog(None, gettext('Choose a script to run'), 'Scripts', '', '*.py', wx.OPEN)
            if dlg.ShowModal() == wx.ID_OK:
                prevDir = os.getcwd()
                os.chdir(os.path.dirname(dlg.GetPath()))
                try:
                    execfile(dlg.GetPath(), self.scriptLocals())
                except:
                    (exceptionType, exceptionValue, exceptionTraceback) = sys.exc_info()
                    dialog = wx.MessageDialog(self, exceptionValue.message, gettext('An error occurred at line %d of the script:') % exceptionTraceback.tb_next.tb_lineno, style = wx.ICON_ERROR | wx.OK)
                    dialog.ShowModal()
                os.chdir(prevDir)
            dlg.Destroy()
        
        
        def onOpenConsole(self, event):
            if '_console' not in dir(self):
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
        
        
        def onNewNetwork(self, event=None):
            network = self.createNetwork()
            self.displayNetwork(network)
        
        
        def createNetwork(self):
            network = Network()
            #TODO: implement doc/view framework
            return network
        
        
        def onOpenNetwork(self, event):
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
                        self.displayNetwork(network)
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

        
        def onOpenPreferences(self, event):
            self.preferences.Show(True)
            self.preferences.Raise()
            return self.preferences
        
        
        def onBrowseLibrary(self, event):
            self.library.browse()
        
        
        def onOpenInspector(self, event):
            self.inspector.Show(True)
            self.inspector.Raise()
            return self.inspector
        
        
        def onOpenWxinspector(self, event):
            self.ShowInspectionTool()
        
        
        def onShowDocumentation(self, event):
            if event.GetId() == self._customizationDocSetId:
                page = 'Customizing/index.html'
            elif event.GetId() == self._dataMgmtDocSetId:
                page = 'DataManagement.html'
            elif event.GetId() == self._scriptingDocSetId:
                page = 'Scripting/index.html'
            elif event.GetId() == self._uiDocSetId:
                page = 'UserInterface.html'
            
            Documentation.showPage(page)
                
        
        def onAboutNeuroptikon(self, event):
            import __version__
            dialog = wx.MessageDialog(None, gettext("Version %s") % (__version__.version), gettext("Neuroptikon"), wx.ICON_INFORMATION | wx.OK)
            dialog.ShowModal()
            dialog.Destroy()
    
    
    def run():
        app = Neuroptikon(None)
        app.MainLoop()
    
    run( )
    
