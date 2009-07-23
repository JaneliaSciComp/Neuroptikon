import os, platform, stat, sys

if 'OSG_NOTIFY_LEVEL' not in os.environ:
    os.environ['OSG_NOTIFY_LEVEL'] = 'ALWAYS'

runningFromSource = not hasattr(sys, "frozen")

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

if platform.system() == 'Darwin':
    # Make sure fonts are found on Mac OS X
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

def debugException(type, value, tb):
    import traceback; traceback.print_tb(tb)
    print "Exception:", value
    import pdb; pdb.pm()


if __name__ == "__main__":
    #if __debug__:
    #    sys.excepthook = debugException
    
    class Neuroptikon(wx.App):
        
        def OnInit(self):
            
            self.rootDir = rootDir
            self.platformLibPath = platformLibPath
            
            import Inspectors, Layouts, Shapes
            
            self.library = Library()
            self._loadDefaultLibraryItems()
            
            self._networks = []
            
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
            for frame in list(self._frames):
                frame.Close()
            if len(self._frames) == 0 and platform.system() != 'Windows':
                self.ExitMainLoop()
        
        
        def loadImage(self, imageFileName):
            try:
                image = wx.Image(self.rootDir + os.sep + 'Images' + os.sep + imageFileName)
            except:
                image = None
            return image
        
        
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
                      'NeuralPolarity': Neuron.Polarity, 
                      'NeuralFunction': Neuron.Function, 
                      'Attribute': Attribute, 
                      'layouts': layoutClasses, 
                      'shapes': shapeClasses}
            for objectClass in Object.__subclasses__():
                locals[objectClass.__name__] = objectClass
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
            self._networks.append(network)
            #TODO: implement doc/view framework
            return network
        
        
        def onOpenNetwork(self, event):
            from NeuroptikonFrame import NeuroptikonFrame
            dlg = wx.FileDialog(None, gettext('Choose a saved network to open:'), '', '', '*.xml', wx.OPEN)
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
                try:
                    xmlTree = ElementTree.parse(path)
                    
                    # Instantiate the network
                    networkElement = xmlTree.find('Network')
                    network = Network.fromXMLElement(networkElement)
                    if network is None:
                        raise ValueError, gettext('Could not load the network')
                    network.setSavePath(path)
                    self._networks.append(network)
                    
                    # Instantiate any displays
                    for frameElement in xmlTree.findall('DisplayWindow'):
                        frame = NeuroptikonFrame.fromXMLElement(frameElement, network = network)
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
            return self._networks
        
        
        def displayNetwork(self, network):
            from NeuroptikonFrame import NeuroptikonFrame
            frame = NeuroptikonFrame(network = network)
            frame.Show(True)
            frame.Raise()
            self._frames.append(frame)
            return frame.display
        
        
        def displayWasClosed(self, display):
            self._frames.remove(display)
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
        
        
        def onAboutNeuroptikon(self, event):
            import __version__
            dialog = wx.MessageDialog(None, gettext("Version %s") % (__version__.version), gettext("Neuroptikon"), wx.ICON_INFORMATION | wx.OK)
            dialog.ShowModal()
            dialog.Destroy()
        
    
    def run():
        app = Neuroptikon(None)
        app.MainLoop()
    
    run( )
    
